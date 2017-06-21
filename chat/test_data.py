from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from money.models import Product
from web.models import Event, EventGroup


def make_event_two_groups():
    user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
    user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
    user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
    user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
    user5 = User.objects.create_user(username='alice1', email='bob5@alice.com', password='top_secret')
    user6 = User.objects.create_user(username='alice2', email='bob6@alice.com', password='top_secret')
    user7 = User.objects.create_user(username='alice3', email='bob7@alice.com', password='top_secret')
    user8 = User.objects.create_user(username='alice4', email='bob8@alice.com', password='top_secret')

    product1 = Product(name='product1_test', short_code='product1_test', amount=100)
    product1.save()

    event = Event(creator=user1, name='test event 1', locationName='location',
                  startDateTime=datetime.now(timezone.utc) + timedelta(days=20),
                  maxParticipantsInGroup=5, numGroups=2, product=product1)
    event.save()

    group1 = EventGroup(event=event, name='group1', ageMin=20, ageMax=30)
    group1.save()

    group2 = EventGroup(event=event, name='group2', ageMin=20, ageMax=30)
    group2.save()

    group1.add_participant(user1)
    group1.add_participant(user2)
    group1.add_participant(user3)
    group1.add_participant(user4)

    group2.add_participant(user5)
    group2.add_participant(user6)
    group2.add_participant(user7)
    group2.add_participant(user8)

    print('Event created: ' + str(event.id))


def make_event_one_group():
    user1 = User.objects.create_user(username='bill1', email='bob1@alice2.com', password='top_secret')
    user2 = User.objects.create_user(username='bill2', email='bob2@alice2.com', password='top_secret')
    user3 = User.objects.create_user(username='bill3', email='bob3@alice2.com', password='top_secret')
    user4 = User.objects.create_user(username='bill4', email='bob4@alice2.com', password='top_secret')
    user5 = User.objects.create_user(username='bill5', email='bob5@alice2.com', password='top_secret')

    product1 = Product(name='product2_test', short_code='product2_test', amount=100)
    product1.save()

    event = Event(creator=user1, name='test event 2', locationName='location',
                  startDateTime=datetime.now(timezone.utc) + timedelta(days=2),
                  maxParticipantsInGroup=5, numGroups=1, product=product1)
    event.save()

    group1 = EventGroup(event=event, name='group1', ageMin=20, ageMax=30)
    group1.save()

    group1.add_participant(user1)
    group1.add_participant(user2)
    group1.add_participant(user3)
    group1.add_participant(user4)
    group1.add_participant(user5)

    print('Event created: ' + str(event.id))
