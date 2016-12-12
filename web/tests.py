from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Event, EventGroup
from .forms import EventForm, EventGroupForm


# Test the model Event
class EventModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='bob5', email='bob5@alice.com', password='top_secret')
        self.user6 = User.objects.create_user(username='bob6', email='bob6@alice.com', password='top_secret')

        self.event = Event(creator=self.user1, name='test event', location='location', startDateTime=timezone.now())
        self.event.save()

        group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30, participantsMaxNumber=10)
        group1.save()
        group1.add_participant(self.user1)
        group1.add_participant(self.user2)
        group1.add_participant(self.user3)
        group1.add_participant(self.user4)

        group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30, participantsMaxNumber=10)
        group2.save()
        group2.add_participant(self.user5)
        group2.add_participant(self.user6)

    def test_get_all_participants(self):
        self.assertEqual(len(self.event.get_all_participants()), 6)


# Test the model EventGroup
class EventGroupModelCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
        self.user5 = User.objects.create_user(username='bob5', email='bob5@alice.com', password='top_secret')
        self.user6 = User.objects.create_user(username='bob6', email='bob6@alice.com', password='top_secret')
        self.user7 = User.objects.create_user(username='bob7', email='bob7@alice.com', password='top_secret')
        self.user8 = User.objects.create_user(username='bob8', email='bob8@alice.com', password='top_secret')

        self.event = Event(creator=self.user1, name='test event', location='location', startDateTime=timezone.now())
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30, participantsMaxNumber=10)
        self.group1.save()
        self.group1.add_participant(self.user1)
        self.group1.add_participant(self.user2)
        self.group1.add_participant(self.user3)
        self.group1.add_participant(self.user4)

        self.group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30, participantsMaxNumber=2)
        self.group2.save()
        self.group2.add_participant(self.user5)
        self.group2.add_participant(self.user6)

    def test_add_participant(self):
        self.group1.add_participant(self.user7)
        self.assertEqual(self.group1.participants.all().count(), 5)
        with self.assertRaises(Exception):
            self.group1.add_participant(self.user7)
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user7)
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user1)
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user8)


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
