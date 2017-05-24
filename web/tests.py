from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Event, EventGroup, Pick
from money.models import Product

# from .forms import EventForm, EventGroupForm


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

        self.event = Event(creator=self.user1, name='test event', location='location', startDateTime=timezone.now(),
                           maxParticipantsInGroup=10, product=self.product1)
        self.event.save()

        group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        group1.save()
        group1.add_participant(self.user1)
        group1.add_participant(self.user2)
        group1.add_participant(self.user3)
        group1.add_participant(self.user4)

        group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30)
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

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', location='location', startDateTime=timezone.now(),
                           maxParticipantsInGroup=3, product=self.product1)
        self.event.save()

        self.group1 = EventGroup(event=self.event, name='group1', ageMin=20, ageMax=30)
        self.group1.save()
        self.group1.add_participant(self.user1)
        self.group1.add_participant(self.user2)
        self.group1.add_participant(self.user3)

        self.group2 = EventGroup(event=self.event, name='group2', ageMin=20, ageMax=30)
        self.group2.save()
        self.group2.add_participant(self.user5)
        self.group2.add_participant(self.user6)

    def test_add_participant(self):
        self.group2.add_participant(self.user7)
        self.assertEqual(self.group1.participants.all().count(), 3)
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user7)
        with self.assertRaises(Exception):
            self.group1.add_participant(self.user1)
        with self.assertRaises(Exception):
            self.group2.add_participant(self.user8)


# Test model Pick
class PickModelCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
        self.user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
        self.user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
        self.user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')

        self.product1 = Product(name='product1', short_code='product1', amount=100)
        self.product1.save()

        self.event = Event(creator=self.user1, name='test event', location='location', startDateTime=timezone.now(),
                           maxParticipantsInGroup=3, product=self.product1)
        self.event.save()

        self.event2 = Event(creator=self.user4, name='test event 2', location='location', startDateTime=timezone.now(),
                            maxParticipantsInGroup=3, product=self.product1)
        self.event2.save()

        self.pick1 = Pick(picker=self.user1, picked=self.user2, event=self.event)
        self.pick1.save()
        self.pick2 = Pick(picker=self.user1, picked=self.user3, event=self.event)
        self.pick2.save()
        self.pick3 = Pick(picker=self.user2, picked=self.user1, event=self.event)
        self.pick3.save()
        self.pick4 = Pick(picker=self.user2, picked=self.user3, event=self.event)
        self.pick4.save()
        self.pick5 = Pick(picker=self.user1, picked=self.user4, event=self.event2)
        self.pick5.save()
        self.pick6 = Pick(picker=self.user4, picked=self.user1, event=self.event2)
        self.pick6.save()

    def test_matches(self):
        # Get all matches for user1
        matches = Pick.objects.get_matches(self.user1, self.event)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user2 in matches)

        # Get all matches for user2
        matches = Pick.objects.get_matches(self.user2, self.event)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user1 in matches)

        # Get all matches for user1, event2
        matches = Pick.objects.get_matches(self.user1, self.event2)
        self.assertEqual(len(matches), 1)
        self.assertTrue(self.user4 in matches)

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
