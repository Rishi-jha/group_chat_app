from django.contrib.auth import get_user_model
from django.db import models

from chats.constants import STATUS_CHOICES

User = get_user_model()


class ChatGroup(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name="chatgroups"
    )
    members = models.ManyToManyField(User)


class Message(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=True, null=True)


class MessageStatus(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="statuses"
    )
