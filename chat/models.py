import logging

from django.conf import settings
from django.db import models

from event.models import Event
from account.models import Account, Memo

logger = logging.getLogger(__name__)


class ConversationManager(models.Manager):
    def mark_token_requested(self, conversation_id):
        conversation = self.get(pk=conversation_id)
        conversation.tokenRequested = True
        conversation.save()


class Conversation(models.Model):
    BREAK = 'break'

    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField()
    interlocutorUser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='interlocutor', blank=True, null=True,
                                         on_delete=models.SET_NULL)
    interlocutorAccount = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL)
    interlocutorMemo = models.ForeignKey(Memo, blank=True, null=True, on_delete=models.SET_NULL)
    sessionID = models.CharField(max_length=200, blank=True, null=True)
    tokenRequested = models.BooleanField(default=False)

    # Automatic timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = ConversationManager()

    def __str__(self):
        interlocutor = Conversation.BREAK
        if self.interlocutorUser is not None:
            interlocutor = self.interlocutorUser.username

        return 'Event: ' + str(self.event.id) + '[' + str(self.order) + '] | user ' \
               + str(self.user) + ' talks to ' + interlocutor
