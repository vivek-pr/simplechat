from rest_framework import serializers
from chat.models import Message

class MessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message', 'sender', 'recipient', 'sent_at')