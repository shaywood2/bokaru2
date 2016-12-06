from django.test import TestCase
from django.contrib.auth.models import User

from .models import Event, EventGroup
from .forms import EventForm, EventGroupForm


# Testing the forms EventForm and EventGroupForm
class EventFormCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='bob', email='bob@alice.com', password='top_secret')
        # self.user = AnonymousUser()

    def testCreateEventWithOneGroup(self):
        form_data = {'name': 'event name', 'location': 'event location',
                     'startDateTime': '2011-11-11', 'isSingleGroup': 'True'}
        form = EventForm(data=form_data, user=self.user)
        # Validate form
        self.assertTrue(form.is_valid())
        # Save form
        form.save(True)
        event = Event.objects.get(name='event name')
        self.assertEqual(event.location, 'event location')
        self.assertEqual(event.creator, self.user)
        # Create a group
        form_data_group = {'name': 'group 1', 'ageMin': '20', 'ageMax': '30', 'participantsMaxNumber': '20'}
        form_group = EventGroupForm(data=form_data_group, event=event)
        # Validate form
        self.assertTrue(form_group.is_valid())
        # Save form
        form_group.save(True)
        event_group = EventGroup.objects.get(name='group 1')
        self.assertEqual(event_group.ageMin, 20)
        self.assertEqual(event_group.event, event)
        self.assertTrue(event_group in event.eventgroup_set.all())

    def testCreateEventWithTwoGroups(self):
        form_data = {'name': 'event name', 'location': 'event location',
                     'startDateTime': '2011-11-11', 'isSingleGroup': 'True'}
        form = EventForm(data=form_data, user=self.user)
        # Validate form
        self.assertTrue(form.is_valid())
        # Save form
        form.save(True)
        event = Event.objects.get(name='event name')
        self.assertEqual(event.location, 'event location')
        self.assertEqual(event.creator, self.user)
        # Create group 1
        form_data_group = {'name': 'group 1', 'ageMin': '20', 'ageMax': '30', 'participantsMaxNumber': '20'}
        form_group = EventGroupForm(data=form_data_group, event=event)
        # Validate form
        self.assertTrue(form_group.is_valid())
        # Save group 1
        form_group.save(True)
        event_group = EventGroup.objects.get(name='group 1')
        self.assertEqual(event_group.ageMin, 20)
        self.assertEqual(event_group.event, event)
        self.assertTrue(event_group in event.eventgroup_set.all())

    def testCreateEventWithNoUser(self):
        form_data = {'name': 'event name', 'location': 'event location',
                     'startDateTime': '2011-11-11', 'isSingleGroup': 'True'}
        with self.assertRaises(Exception):
            EventForm(data=form_data)

    def testCreateEventGroupWithNoEvent(self):
        form_data_group = {'name': 'group 1', 'ageMin': '20', 'ageMax': '30', 'participantsMaxNumber': '20'}
        with self.assertRaises(Exception):
            EventGroupForm(data=form_data_group)
