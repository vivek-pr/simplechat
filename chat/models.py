from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



class Message(models.Model):
    """
    A private message from user to user
    """
    message = models.CharField(("Subject"), max_length=140)
    sender = models.ForeignKey(User, related_name='sent_messages', verbose_name=("Sender"))
    recipient = models.ForeignKey(User, related_name='received_messages', null=True, blank=True, verbose_name=("Recipient"))
    sent_at = models.DateTimeField(("sent at"), null=True, blank=True)



    def __unicode__(self):
        return self.message

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = timezone.now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['sent_at']
        verbose_name = ("Message")
        verbose_name_plural = ("Messages")

