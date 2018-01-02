import logging
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from chat import utils
from account.models import Memo
from event.models import Event, EventGroup
from money.models import Product
from . import test_data

# Disable logging
logging.disable(logging.CRITICAL)
LOGGER = logging.getLogger(__name__)


# Test the scheduling algorithms
class UtilsTest(TestCase):
    def test_generate_conversations_two_groups(self):
        user1 = test_data.make_user('bob1', 'male', '1980-01-01')
        user2 = test_data.make_user('bob2', 'male', '1980-01-01')
        user3 = test_data.make_user('bob3', 'male', '1980-01-01')
        user4 = test_data.make_user('bob4', 'male', '1980-01-01')
        user5 = test_data.make_user('alice1', 'female', '1980-01-01')
        user6 = test_data.make_user('alice2', 'female', '1980-01-01')
        user7 = test_data.make_user('alice3', 'female', '1980-01-01')
        user8 = test_data.make_user('alice4', 'female', '1980-01-01')

        product1 = Product(name='product1', short_code='product1', amount=100)
        product1.save()

        event = Event(creator=user1, name='test event', locationName='location',
                      startDateTime=timezone.now() + timedelta(days=2),
                      maxParticipantsInGroup=5, numGroups=2, product=product1)
        event.save()

        group1 = EventGroup(event=event, sexualIdentity='male', ageMin=20, ageMax=99)
        group1.save()

        group2 = EventGroup(event=event, sexualIdentity='female', ageMin=20, ageMax=99)
        group2.save()

        group1.add_participant(user1)
        group1.add_participant(user2)
        group1.add_participant(user3)
        group1.add_participant(user4)

        group2.add_participant(user5)
        group2.add_participant(user6)
        group2.add_participant(user7)
        group2.add_participant(user8)

        Memo.objects.create_or_update_memo(user1, user5, 'lorem ipsum ' + str(user5))
        Memo.objects.create_or_update_memo(user1, user6, 'lorem ipsum ' + str(user6))
        Memo.objects.create_or_update_memo(user1, user7, 'lorem ipsum ' + str(user7))
        Memo.objects.create_or_update_memo(user1, user8, 'lorem ipsum ' + str(user8))

        utils.generate_conversations(event)

        # Dates must be symmetrical (if user1 talks to user5, then user5 talks to user1)
        user1_date_1 = utils.get_user_dates(user1, event)[0].get('user')
        self.assertEqual(utils.get_user_dates(user1_date_1, event)[0].get('user'), user1)
        self.assertNotEqual(utils.get_user_dates(user1_date_1, event)[1].get('user'), user1)

        # Session ID must match in a pair
        user2_date_2 = utils.get_user_dates(user2, event)[1]
        session_id_1 = user2_date_2.get('sessionID')
        session_id_2 = utils.get_user_dates(user2_date_2.get('user'), event)[1].get('sessionID')
        session_id_3 = utils.get_user_dates(user2_date_2.get('user'), event)[0].get('sessionID')
        self.assertIsNotNone(session_id_1)
        self.assertIsNotNone(session_id_2)
        self.assertIsNotNone(session_id_3)
        self.assertEqual(session_id_1, session_id_2)
        self.assertNotEqual(session_id_1, session_id_3)

        user5_date_3 = utils.get_user_dates(user5, event)[2].get('user')
        self.assertEqual(utils.get_user_dates(user5_date_3, event)[2].get('user'), user5)
        self.assertNotEqual(utils.get_user_dates(user5_date_3, event)[1].get('user'), user5)

        # User must talk to all users in the opposite group
        user1_all_dates = []
        for date in utils.get_user_dates(user1, event):
            user1_all_dates.append(date.get('user'))

        self.assertTrue(user5 in user1_all_dates)
        self.assertTrue(user6 in user1_all_dates)
        self.assertTrue(user7 in user1_all_dates)
        self.assertTrue(user8 in user1_all_dates)

        # User must not talk to any users in the same group
        self.assertFalse(user1 in user1_all_dates)
        self.assertFalse(user2 in user1_all_dates)
        self.assertFalse(user3 in user1_all_dates)
        self.assertFalse(user4 in user1_all_dates)

        # Memo must be included in the date list
        self.assertEqual(utils.get_user_dates(user1, event)[0].get('memo').content,
                         'lorem ipsum ' + str(user1_date_1))

        # User must have 4 dates in total
        self.assertEqual(len(user1_all_dates), 4)

    def test_generate_date_matrix_one_group(self):
        user1 = test_data.make_user('bob1', 'male', '1980-01-01')
        user2 = test_data.make_user('bob2', 'male', '1980-01-01')
        user3 = test_data.make_user('bob3', 'male', '1980-01-01')
        user4 = test_data.make_user('bob4', 'male', '1980-01-01')
        user5 = test_data.make_user('bob5', 'male', '1980-01-01')

        product1 = Product(name='product1', short_code='product1', amount=100)
        product1.save()

        event = Event(creator=user1, name='test event', locationName='location',
                      startDateTime=timezone.now() + timedelta(days=2),
                      maxParticipantsInGroup=5, numGroups=1, product=product1)
        event.save()

        group1 = EventGroup(event=event, sexualIdentity='male', ageMin=20, ageMax=90)
        group1.save()

        group1.add_participant(user1)
        group1.add_participant(user2)
        group1.add_participant(user3)
        group1.add_participant(user4)
        group1.add_participant(user5)

        utils.generate_conversations(event)

        # Dates must be symmetrical (if user1 talks to user5, then user5 talks to user1)
        user1_date_1 = utils.get_user_dates(user1, event)[0].get('user')
        if user1_date_1:
            self.assertEqual(utils.get_user_dates(user1_date_1, event)[0].get('user'), user1)
            self.assertNotEqual(utils.get_user_dates(user1_date_1, event)[2].get('user'), user1)
        else:
            user1_date_2 = utils.get_user_dates(user1, event)[1].get('user')
            self.assertEqual(utils.get_user_dates(user1_date_2, event)[1].get('user'), user1)
            self.assertNotEqual(utils.get_user_dates(user1_date_2, event)[2].get('user'), user1)

        user5_date_3 = utils.get_user_dates(user5, event)[2].get('user')
        if user5_date_3:
            self.assertEqual(utils.get_user_dates(user5_date_3, event)[2].get('user'), user5)
            self.assertNotEqual(utils.get_user_dates(user5_date_3, event)[1].get('user'), user5)
        else:
            user5_date_1 = utils.get_user_dates(user5, event)[0].get('user')
            self.assertEqual(utils.get_user_dates(user5_date_1, event)[0].get('user'), user5)
            self.assertNotEqual(utils.get_user_dates(user5_date_1, event)[1].get('user'), user5)

        # User must talk to all users in the group
        user1_all_dates = []
        for date in utils.get_user_dates(user1, event):
            user1_all_dates.append(date.get('user'))

        self.assertTrue(user2 in user1_all_dates)
        self.assertTrue(user3 in user1_all_dates)
        self.assertTrue(user4 in user1_all_dates)
        self.assertTrue(user5 in user1_all_dates)

        # User must have 5 dates in total
        self.assertEqual(len(user1_all_dates), 5)

        # There should be a break as one of the dates
        found = False
        for date in utils.get_user_dates(user1, event):
            if date.get('is_break'):
                found = True
                self.assertIsNone(date.get('user'))
                self.assertIsNone(date.get('account'))
                self.assertIsNone(date.get('memo'))
        self.assertTrue(found)

        user4_all_dates = []
        for date in utils.get_user_dates(user4, event):
            user4_all_dates.append(date.get('user'))

        # User must have 5 dates in total
        self.assertEqual(len(user4_all_dates), 5)

        self.assertTrue(user1 in user4_all_dates)
        self.assertTrue(user2 in user4_all_dates)
        self.assertTrue(user3 in user4_all_dates)
        self.assertTrue(user5 in user4_all_dates)

        # There should be a break as one of the dates
        found = False
        for date in utils.get_user_dates(user4, event):
            if date.get('is_break'):
                found = True
                self.assertIsNone(date.get('user'))
                self.assertIsNone(date.get('account'))
                self.assertIsNone(date.get('memo'))
        self.assertTrue(found)
