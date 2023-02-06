from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from chats.constants import SERIALIZER_STATUS_CHOICES
from chats.models import Message, ChatGroup, MessageStatus

User = get_user_model()


class GetMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "text",
            "sender__username",
        )


class CreateMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=ChatGroup.objects.all())

    class Meta:
        model = Message
        fields = (
            "text",
            "group",
        )

    def create_message(self, sender, group):
        Message.objects.create(
            sender=sender, group=group, text=self.validated_data["text"]
        )


class EditMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)

    class Meta:
        model = Message
        fields = ("text",)


class GetChatGroupSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta:
        model = ChatGroup
        fields = "__all__"


class PostChatGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = ChatGroup
        fields = ("name",)

    def save(self, **kwargs):
        user = self.context["request"].user
        name = self.validated_data["name"]
        instance = ChatGroup.objects.create(name=name, owner=user)
        instance.members.add(user)
        return instance


class UpdateChatGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = ChatGroup
        fields = ("name",)

    def save(self, **kwargs):
        name = self.validated_data["name"]
        self.instance.name = name
        self.instance.save()
        return self.instance


class MemberSerializer(serializers.Serializer):
    members = serializers.ListField(required=True)

    def validate_members(self, members):
        for member in members:
            if not User.objects.filter(username=member).exists():
                raise ValidationError(f"Member: {member} does not exists.")
        return members


class MessageStatusGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageStatus
        fields = "__all__"


class MessageStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(required=True, choices=SERIALIZER_STATUS_CHOICES)
