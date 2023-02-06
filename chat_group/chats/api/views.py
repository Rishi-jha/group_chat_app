from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    GetChatGroupSerializer,
    PostChatGroupSerializer,
    UpdateChatGroupSerializer,
    MemberSerializer,
    CreateMessageSerializer,
    EditMessageSerializer,
    MessageStatusSerializer,
    MessageStatusGetSerializer,
)
from chats.models import ChatGroup

from ..models import Message, MessageStatus

User = get_user_model()


class ChatGroupViewset(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all()
    http_method_names = ["get", "patch", "post", "delete"]
    serializer_get = GetChatGroupSerializer
    # permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return GetChatGroupSerializer
        if self.request.method.lower() == "post":
            return PostChatGroupSerializer
        if self.request.method.lower() == "patch":
            return UpdateChatGroupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        request_user = self.request.user
        queryset = queryset.filter(members__username=request_user.username)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.serializer_get(instance).data
        return Response(data=response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        if instance.owner != request.user:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="User is not same as owner of chatgroup!",
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.serializer_get(instance).data
        return Response(data=response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.onwer != self.request.user:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="User is not same as owner of chatgroup!",
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post", "delete"], detail=True)
    def members(self, request, pk=None, *args, **kwargs):
        group = self.get_object()
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            members = serializer.validated_data["members"]
            member_users = User.objects.filter(username__in=members)
            if request.method.lower() == "post":
                for member in member_users:
                    group.members.add(member)
                return Response(
                    {"status": f"Members Added in group `{group.name}`: {members}"}
                )

            if request.method.lower() == "delete":
                for member in member_users:
                    group.members.remove(member)
                return Response(
                    {"status": f"Members Removed from group `{group.name}`: {members}"}
                )

    @action(methods=["get"], detail=True)
    def messages(self, request, pk=None, *args, **kwargs):
        group = self.get_object()
        user = request.user
        if not group.members.filter(username=user.username).exists():
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data="Only Members of the group can read messages",
            )
        from_query_param = request.query_params.get(
            "from", 1
        )  # this is to get message from last hour
        time_from = timezone.now() - timedelta(hours=from_query_param)
        messages = Message.objects.filter(group=group, timestamp__gte=time_from)
        messages_block = []
        for message in messages.values("text", "sender__username", "timestamp"):
            message["sender"] = message.pop("sender__username")
            messages_block.append(message)
        response = {"messages": messages_block}
        return Response(data=response, status=status.HTTP_200_OK)


class MessageViewset(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    http_method_names = ["patch", "post", "get"]
    serializer_get = GetChatGroupSerializer

    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return CreateMessageSerializer
        if self.request.method.lower() == "patch":
            return EditMessageSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            group = serializer.validated_data["group"]
            if not group.members.filter(username=request.user.username).exists():
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data=f"User {request.user.username} is not a part of the group {group.name}",
                )
            instance = serializer.create_message(sender=request.user, group=group)
        return Response(data="Message Created", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        message = self.get_object()
        if message.owner != request.user:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data=f"Owner of the message is not same as user",
            )
        serializer = self.get_serializer(message, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.serializer_get(instance).data
        return Response(data=response_data, status=status.HTTP_200_OK)

    @action(methods=["post", "patch", "delete", "get"], detail=True)
    def status(self, request, pk=None, *args, **kwargs):
        message = self.get_object()
        if request.method.lower() == "get":
            statuses = message.statuses.all()
            if statuses:
                return Response(
                    data={
                        "data": MessageStatusGetSerializer(
                            instance=statuses, many=True
                        ).data
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                data={},
                status=status.HTTP_200_OK,
            )

        if request.method.lower() == "delete":
            message_status = message.statuses.filter(owner=request.user)
            message_status.delete()
            return Response(data="Status Removed", status=status.HTTP_200_OK)
        else:
            serializer = MessageStatusSerializer(data=request.data)
            if serializer.is_valid():
                if request.method.lower() == "post":
                    existing_message_status = message.statuses.filter(
                        owner=request.user
                    )
                    if existing_message_status:
                        existing_message_status.delete()
                    message_status = MessageStatus.objects.create(
                        owner=request.user,
                        status=serializer.validated_data["status"],
                        message=message,
                    )
                    return Response(
                        data=MessageStatusGetSerializer(message_status).data,
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    existing_message_status = message.statuses.filter(
                        owner=request.user
                    )
                    if not existing_message_status:
                        return Response(
                            status=status.HTTP_404_NOT_FOUND,
                            data="No status found to update",
                        )
                    existing_message_status = existing_message_status.first()
                    existing_message_status.status = serializer.validated_data["status"]
                    existing_message_status.save()
                    return Response(
                        data=MessageStatusGetSerializer(existing_message_status).data,
                        status=status.HTTP_200_OK,
                    )
