from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from money.models import Product
from .models import Event, EventGroup, Pick, EventParticipant


# from .forms import EventForm, EventGroupForm


# Test the manager EventManager
class EventManagerTestCase(TestCase):
    def test_filter_by_distance(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event1 = Event(creator=self.user1, name='test event', locationName='location',
                            locationCoordinates=Point(-0.1192746, 51.5163499), startDateTime=timezone.now(),
                            maxParticipantsInGroup=10, numGroups=2, product=self.product1)
        self.event1.save()

        self.event2 = Event(creator=self.user1, name='test event', locationName='location',
                            locationCoordinates=Point(-0.1194731, 51.5167871), startDateTime=timezone.now(),
                            maxParticipantsInGroup=10, numGroups=2, product=self.product1)
        self.event2.save()

        events = Event.objects.filter_by_distance(-0.1209811, 51.5163032, 10)
        self.assertEqual(events.count(), 2)

        events = Event.objects.filter_by_distance(-0.1209811, 51.5163032, 0.1)
        self.assertEqual(events.count(), 0)

        events = Event.objects.filter_by_distance(0.1209811, 51.5163032, 10)
        self.assertEqual(events.count(), 0)


# Test the model Event
class EventModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='bob5', email='bob5@alice.com', password='top_secret')
        self.user6 = User.objects.create_user(username='bob6', email='bob6@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', locationName='location', startDateTime=timezone.now(),
                           maxParticipantsInGroup=10, numGroups=2, product=self.product1)
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        self.group1.save()

        self.group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30)
        self.group2.save()

        ep1 = EventParticipant(group=self.group1, user=self.user1, status='registered')
        ep1.save()

        ep2 = EventParticipant(group=self.group1, user=self.user2, status='registered')
        ep2.save()

        ep3 = EventParticipant(group=self.group2, user=self.user3, status='registered')
        ep3.save()

        ep4 = EventParticipant(group=self.group2, user=self.user4, status='registered')
        ep4.save()

        ep5 = EventParticipant(group=self.group2, user=self.user5, status='waiting_list')
        ep5.save()

    def test_is_registered(self):
        # Registered users
        self.assertTrue(self.event.is_registered(self.user1))
        self.assertTrue(self.event.is_registered(self.user2))
        # Waiting list user
        self.assertFalse(self.event.is_registered(self.user5))
        # Unrelated user
        self.assertFalse(self.event.is_registered(self.user6))

    def test_is_on_waiting_list(self):
        # Waiting list user
        self.assertTrue(self.event.is_on_waiting_list(self.user5))
        # Registered users
        self.assertFalse(self.event.is_on_waiting_list(self.user1))
        # Unrelated user
        self.assertFalse(self.event.is_on_waiting_list(self.user6))


# Test the model EventGroup
class EventGroupModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='bob5', email='bob5@alice.com', password='top_secret')
        self.user6 = User.objects.create_user(username='bob6', email='bob6@alice.com', password='top_secret')
        self.user7 = User.objects.create_user(username='bob7', email='bob7@alice.com', password='top_secret')
        self.user8 = User.objects.create_user(username='bob8', email='bob8@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', locationName='location',
                           startDateTime=datetime.now(timezone.utc) + timedelta(days=2),
                           maxParticipantsInGroup=3, numGroups=2, product=self.product1)
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        self.group1.save()

        self.group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30)
        self.group2.save()

        self.ep1 = EventParticipant(group=self.group1, user=self.user1, status='registered')
        self.ep1.save()

        self.ep2 = EventParticipant(group=self.group1, user=self.user2, status='registered')
        self.ep2.save()

        self.ep3 = EventParticipant(group=self.group2, user=self.user3, status='registered')
        self.ep3.save()

        self.ep4 = EventParticipant(group=self.group2, user=self.user4, status='registered')
        self.ep4.save()

        self.ep5 = EventParticipant(group=self.group2, user=self.user5, status='waiting_list')
        self.ep5.save()

    def test_get_registered_participants(self):
        # Must be 2 participants in the group 1 already
        self.assertEqual(len(self.group1.get_registered_participants()), 2)

        # Add another participant
        ep6 = EventParticipant(group=self.group1, user=self.user6, status='registered')
        ep6.save()

        # Must be 3 participants in the group 1 now
        participants = self.group1.get_registered_participants()
        self.assertEqual(len(participants), 3)

        # Check the order of participants
        self.assertEqual(participants[0], self.ep1)
        self.assertEqual(participants[2], ep6)

        # Must be 2 participants in the group 2 already
        self.assertEqual(len(self.group2.get_registered_participants()), 2)

        # Add a participant with payment_processed
        ep7 = EventParticipant(group=self.group2, user=self.user7, status='registered')
        ep7.save()

        # Must be 3 participants in the group 2 now
        self.assertEqual(len(self.group2.get_registered_participants()), 3)

    def test_count_registered_participants(self):
        # Must be 2 participants in the group 1
        self.assertEqual(self.group1.count_registered_participants(), 2)

        # Add another participant
        ep = EventParticipant(group=self.group1, user=self.user6, status='registered')
        ep.save()

        # Must be 3 participants in the group 1
        self.assertEqual(self.group1.count_registered_participants(), 3)

        # Must be 2 participants in the group 2
        self.assertEqual(self.group2.count_registered_participants(), 2)

    def test_add_participant(self):
        # Must be 2 participants in the group 1
        self.assertEqual(self.group1.count_registered_participants(), 2)

        # Add a new participant
        self.group1.add_participant(self.user6)

        # Must be 3 participants in the group 1 now
        self.assertEqual(self.group1.count_registered_participants(), 3)

        # Add the same participant
        with self.assertRaises(Exception):
            self.group1.add_participant(self.user6)

        # Must be 3 participants in the group 1 now
        self.assertEqual(self.group1.count_registered_participants(), 3)

        # Add the same participant to another group
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user6)

        # Add one too many participants
        with self.assertRaises(Exception):
            self.group1.add_participant(self.user7)

        # Add a user on the waiting list
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user5)


# Test model Pick
class PickModelCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', locationName='location', startDateTime=timezone.now(),
                           maxParticipantsInGroup=3, numGroups=2, product=self.product1)
        self.event.save()

        self.event2 = Event(creator=self.user4, name='test event 2', locationName='location',
                            startDateTime=timezone.now(),
                            maxParticipantsInGroup=3, numGroups=2, product=self.product1)
        self.event2.save()

        Pick.objects.pick(self.user1, self.user2, self.event, Pick.YES)
        Pick.objects.pick(self.user1, self.user3, self.event, Pick.YES)
        Pick.objects.pick(self.user2, self.user1, self.event, Pick.YES)
        Pick.objects.pick(self.user2, self.user3, self.event, Pick.YES)
        Pick.objects.pick(self.user1, self.user4, self.event2, Pick.YES)
        Pick.objects.pick(self.user4, self.user1, self.event2, Pick.YES)

    def test_get_all_matches_by_user_and_event(self):
        # Get all matches for user1
        matches = Pick.objects.get_all_matches_by_user_and_event(self.user1, self.event)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user2 in matches)

        # Get all matches for user2
        matches = Pick.objects.get_all_matches_by_user_and_event(self.user2, self.event)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user1 in matches)

        # Get all matches for user1, event2
        matches = Pick.objects.get_all_matches_by_user_and_event(self.user1, self.event2)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user4 in matches)

    def test_get_all_matches_by_user(self):
        # Get all matches for user1
        matches = Pick.objects.get_all_matches_by_user(self.user1)
        self.assertEqual(len(matches), 2)
        self.assertTrue(self.event in matches)
        self.assertTrue(self.event2 in matches)
        self.assertEqual(len(matches[self.event]), 1)
        self.assertEqual(len(matches[self.event2]), 1)
        self.assertTrue(self.user2 in matches[self.event])

        # Get all matches for user3
        matches = Pick.objects.get_all_matches_by_user(self.user3)
        self.assertEqual(len(matches), 0)

# Testing the forms EventForm and EventGroupForm
# class EventForm(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='bob', email='bob@alice.com', password='top_secret')
#         # self.user = AnonymousUser()
#
#     def test_CreateEventWithOneGroup(self):
#         form_data = {'name': 'event name', 'location': 'event location',
#                      'startDateTime': '2011-11-11'}
#         form = EventForm(form_data)
#         # Validate form
#         self.assertTrue(form.is_valid())
#         # Save form
#         form.save(True)
#         event = Event.objects.get(name='event name')
#         self.assertEqual(event.location, 'event location')
#         # self.assertEqual(event.creator, self.user)
#         # Create a group
#         form_data_group = {'name': 'group 1', 'ageMin': '20', 'ageMax': '30', 'participantsMaxNumber': '20'}
#         form_group = EventGroupForm(form_data_group)
#         # Validate form
#         self.assertTrue(form_group.is_valid())
#         # Save form
#         form_group.save(True)
#         event_group = EventGroup.objects.get(name='group 1')
#         self.assertEqual(event_group.ageMin, 20)
#         self.assertEqual(event_group.event, event)
#         self.assertTrue(event_group in event.eventgroup_set.all())
#
#     def test_CreateEventWithTwoGroups(self):
#         form_data = {'name': 'event name', 'location': 'event location',
#                      'startDateTime': '2011-11-11'}
#         form = EventForm(form_data)
#         # Validate form
#         self.assertTrue(form.is_valid())
#         # Save form
#         form.save(True)
#         event = Event.objects.get(name='event name')
#         self.assertEqual(event.location, 'event location')
#         # self.assertEqual(event.creator, self.user)
#         # Create group 1
#         form_data_group = {'name': 'group 1', 'ageMin': '20', 'ageMax': '30', 'participantsMaxNumber': '20'}
#         form_group = EventGroupForm(form_data_group)
#         # Validate form
#         self.assertTrue(form_group.is_valid())
#         # Save group 1
#         form_group.save(True)
#         event_group = EventGroup.objects.get(name='group 1')
#         self.assertEqual(event_group.ageMin, 20)
#         self.assertEqual(event_group.event, event)
#         self.assertTrue(event_group in event.eventgroup_set.all())
#
#     def test_CreateEventWithNoUser(self):
#         form_data = {'name': 'event name', 'location': 'event location',
#                      'startDateTime': '2011-11-11', 'isSingleGroup': 'True'}
#         with self.assertRaises(Exception):
#             EventForm(data=form_data)
