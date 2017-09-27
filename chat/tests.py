import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from chat import utils
from money.models import Product
from web.models import Event, EventGroup

# Disable logging
logging.disable(logging.CRITICAL)


# Test the model EventGroup
class UtilsTest(TestCase):
    def test_generate_date_matrix_two_groups(self):
        cache.clear()

        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='alice1', email='bob5@alice.com', password='top_secret')
        self.user6 = User.objects.create_user(username='alice2', email='bob6@alice.com', password='top_secret')
        self.user7 = User.objects.create_user(username='alice3', email='bob7@alice.com', password='top_secret')
        self.user8 = User.objects.create_user(username='alice4', email='bob8@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', locationName='location',
                           startDateTime=datetime.now(timezone.utc) + timedelta(days=2),
                           maxParticipantsInGroup=5, numGroups=2, product=self.product1)
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        self.group1.save()

        self.group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30)
        self.group2.save()

        self.group1.add_participant(self.user1)
        self.group1.add_participant(self.user2)
        self.group1.add_participant(self.user3)
        self.group1.add_participant(self.user4)

        self.group2.add_participant(self.user5)
        self.group2.add_participant(self.user6)
        self.group2.add_participant(self.user7)
        self.group2.add_participant(self.user8)

        date_matrix = utils.get_date_matrix(self.event.id)

        # Dates must be symmetrical (if user1 talks to user5, then user5 talks to user1)
        user1_date_1 = date_matrix[self.user1.id][0]
        user5_date_3 = date_matrix[self.user5.id][2]
        self.assertEqual(date_matrix[user1_date_1][0], self.user1.id)
        self.assertNotEqual(date_matrix[user1_date_1][1], self.user1.id)

        # User must talk to all users in the opposite group
        user1_all_dates = date_matrix[self.user1.id]
        self.assertTrue(self.user5.id in user1_all_dates.values())
        self.assertTrue(self.user6.id in user1_all_dates.values())
        self.assertTrue(self.user7.id in user1_all_dates.values())
        self.assertTrue(self.user8.id in user1_all_dates.values())

        # User must not talk to any users in the same group
        self.assertFalse(self.user1.id in user1_all_dates.values())
        self.assertFalse(self.user2.id in user1_all_dates.values())
        self.assertFalse(self.user3.id in user1_all_dates.values())
        self.assertFalse(self.user4.id in user1_all_dates.values())

        # Matrix must persist in cache
        date_matrix = utils.get_date_matrix(self.event.id)
        self.assertEqual(user1_date_1, date_matrix[self.user1.id][0])
        self.assertEqual(user5_date_3, date_matrix[self.user5.id][2])

    def test_generate_date_matrix_one_group(self):
        cache.clear()

        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='bob5', email='bob5@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', locationName='location',
                           startDateTime=datetime.now(timezone.utc) + timedelta(days=2),
                           maxParticipantsInGroup=5, numGroups=1, product=self.product1)
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        self.group1.save()

        self.group1.add_participant(self.user1)
        self.group1.add_participant(self.user2)
        self.group1.add_participant(self.user3)
        self.group1.add_participant(self.user4)
        self.group1.add_participant(self.user5)

        date_matrix = utils.get_date_matrix(self.event.id)

        # Dates must be symmetrical (if user1 talks to user5, then user5 talks to user1)
        user1_date_1 = date_matrix[self.user1.id][0]
        user5_date_3 = date_matrix[self.user5.id][2]
        self.assertEqual(date_matrix[user1_date_1][0], self.user1.id)
        self.assertNotEqual(date_matrix[user1_date_1][1], self.user1.id)

        # User must talk to all users in the group
        user1_all_dates = date_matrix[self.user1.id]
        self.assertTrue(self.user2.id in user1_all_dates.values())
        self.assertTrue(self.user3.id in user1_all_dates.values())
        self.assertTrue(self.user4.id in user1_all_dates.values())
        self.assertTrue(self.user5.id in user1_all_dates.values())

        user4_all_dates = date_matrix[self.user4.id]
        self.assertTrue(self.user2.id in user4_all_dates.values())
        self.assertTrue(self.user3.id in user4_all_dates.values())
        self.assertTrue(self.user1.id in user4_all_dates.values())
        self.assertTrue(self.user5.id in user4_all_dates.values())

        # Matrix must persist in cache
        date_matrix = utils.get_date_matrix(self.event.id)
        self.assertEqual(user1_date_1, date_matrix[self.user1.id][0])
        self.assertEqual(user5_date_3, date_matrix[self.user5.id][2])

    def test_send_message_get_message(self):
        cache.clear()

        user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')

        # Send a message from 1 to 2
        utils.send_message(user1.id, user2.id, 'lorem ipsum dolor sit amet')

        # Send a message from 2 to 1
        utils.send_message(user2.id, user1.id, {'key': 'value'})

        # Read a message from 1
        message1 = utils.get_message(user2.id, user1.id)
        self.assertEqual(message1, 'lorem ipsum dolor sit amet')

        # Read a message from 2
        message2 = utils.get_message(user1.id, user2.id)
        self.assertEqual(message2['key'], 'value')
