from django.contrib.auth.models import User
from django.test import TestCase

from .models import Memo


# Test model Memo
class MemoModelCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')

    def test_create_or_update_memo(self):
        # Create a memo
        Memo.objects.create_or_update_memo(self.user1, self.user2, 'memo1')

        m = Memo.objects.get(owner=self.user1, about=self.user2)

        self.assertEqual(m.content, 'memo1')

        # Update a memo
        Memo.objects.create_or_update_memo(self.user1, self.user2, 'memo123')

        m = Memo.objects.get(owner=self.user1, about=self.user2)

        self.assertEqual(m.content, 'memo123')
