from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from money.models import Product
from web.models import Event, EventGroup
from account.models import Account


def make_products():
    product1 = Product(name='small event', short_code='smallevent', amount=1000)
    product1.save()

    product2 = Product(name='medium event', short_code='mediumevent', amount=1500)
    product2.save()

    product3 = Product(name='large event', short_code='largeevent', amount=2000)
    product3.save()

    print('3 products created')


def make_event_two_groups():
    user1 = User.objects.create_user(username='bob1', email='bob1@alice.com', password='top_secret')
    user2 = User.objects.create_user(username='bob2', email='bob2@alice.com', password='top_secret')
    user3 = User.objects.create_user(username='bob3', email='bob3@alice.com', password='top_secret')
    user4 = User.objects.create_user(username='bob4', email='bob4@alice.com', password='top_secret')
    user5 = User.objects.create_user(username='alice1', email='bob5@alice.com', password='top_secret')
    user6 = User.objects.create_user(username='alice2', email='bob6@alice.com', password='top_secret')
    user7 = User.objects.create_user(username='alice3', email='bob7@alice.com', password='top_secret')
    user8 = User.objects.create_user(username='alice4', email='bob8@alice.com', password='top_secret')

    user_profile1 = Account(user=user1, fullName='bob 1')
    user_profile1.save()
    user_profile2 = Account(user=user2, fullName='bob 2')
    user_profile2.save()
    user_profile3 = Account(user=user3, fullName='bob 3')
    user_profile3.save()
    user_profile4 = Account(user=user4, fullName='bob 4')
    user_profile4.save()
    user_profile5 = Account(user=user5, fullName='alice 1')
    user_profile5.save()
    user_profile6 = Account(user=user6, fullName='alice 2')
    user_profile6.save()
    user_profile7 = Account(user=user7, fullName='alice 3')
    user_profile7.save()
    user_profile8 = Account(user=user8, fullName='alice 4')
    user_profile8.save()

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

    user_profile1 = Account(user=user1, fullName='bob 1')
    user_profile1.save()
    user_profile2 = Account(user=user2, fullName='bob 2')
    user_profile2.save()
    user_profile3 = Account(user=user3, fullName='bob 3')
    user_profile3.save()
    user_profile4 = Account(user=user4, fullName='bob 4')
    user_profile4.save()
    user_profile5 = Account(user=user5, fullName='bob 5')
    user_profile5.save()

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