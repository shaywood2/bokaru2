from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from account.models import Account
from event.models import Event, EventGroup
from money.models import Product


def make_user(name, gender, birth_date):
    user = User.objects.create_user(username=name, email='bob1@alice.com', password='top_secret')
    user_profile = Account(user=user, fullName=name, sexualIdentity=gender, birthDate=birth_date)
    user_profile.save()
    return user


def make_products():
    product1 = Product(name='small event', short_code='smallevent', amount=1000)
    product1.save()

    product2 = Product(name='medium event', short_code='mediumevent', amount=1500)
    product2.save()

    product3 = Product(name='large event', short_code='largeevent', amount=2000)
    product3.save()

    print('3 products created')


def make_event_two_groups():
    user1 = make_user('bob1', 'male', '1980-01-01')
    user2 = make_user('bob2', 'male', '1980-01-01')
    user3 = make_user('bob3', 'male', '1980-01-01')
    user4 = make_user('bob4', 'male', '1980-01-01')
    user5 = make_user('alice1', 'female', '1980-01-01')
    user6 = make_user('alice2', 'female', '1980-01-01')
    user7 = make_user('alice3', 'female', '1980-01-01')
    user8 = make_user('alice4', 'female', '1980-01-01')

    product = Product.objects.get(short_code='smallevent')

    event = Event(creator=user1, name='test event 1', locationName='location',
                  startDateTime=timezone.now() + timedelta(days=20),
                  maxParticipantsInGroup=5, numGroups=2, product=product)
    event.save()

    group1 = EventGroup(event=event, sexualIdentity=EventGroup.MALE, ageMin=20, ageMax=60)
    group1.save()

    group2 = EventGroup(event=event, sexualIdentity=EventGroup.FEMALE, ageMin=20, ageMax=60)
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
    user1 = make_user('bill1', 'male', '1980-01-01')
    user2 = make_user('bill2', 'male', '1980-01-01')
    user3 = make_user('bill3', 'male', '1980-01-01')
    user4 = make_user('bill4', 'male', '1980-01-01')
    user5 = make_user('bill5', 'male', '1980-01-01')

    product = Product.objects.get(short_code='smallevent')

    event = Event(creator=user1, name='test event 2', locationName='location',
                  startDateTime=timezone.now() + timedelta(days=10),
                  maxParticipantsInGroup=5, numGroups=1, product=product)
    event.save()

    group1 = EventGroup(event=event, sexualIdentity=EventGroup.MALE, ageMin=20, ageMax=60)
    group1.save()

    group1.add_participant(user1)
    group1.add_participant(user2)
    group1.add_participant(user3)
    group1.add_participant(user4)
    group1.add_participant(user5)

    print('Event created: ' + str(event.id))
