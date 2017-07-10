import datetime
import logging
import math
import random

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import utc

from account.models import Account
from web.models import Event

LOGGER = logging.getLogger(__name__)


# Function to generate a matrix of dates based on two lists of participants
def generate_date_matrix_two_groups(group_a, group_b):
    # Get the maximum number of participants
    size = max(len(group_a), len(group_b))

    # Add all participants to the matrix
    result = {}
    for participant in group_a:
        result[participant] = {}
    for participant in group_b:
        result[participant] = {}

    # Pad the groups to be the same size
    group_a += [''] * (size - len(group_a))
    group_b += [''] * (size - len(group_b))

    # Shuffle the groups to randomize empty spaces
    random.shuffle(group_a)
    random.shuffle(group_b)

    for participant_a_index in range(size):
        participant_a = group_a[participant_a_index]
        for step_number in range(size):
            # Get the paired participant
            participant_b_index = (participant_a_index + step_number) % size
            participant_b = group_b[participant_b_index]

            # Add the pairings to the matrix
            if participant_a != '':
                result[participant_a][step_number] = participant_b
            if participant_b != '':
                result[participant_b][step_number] = participant_a

    return result


# Function to generate a matrix of dates based on one list of participants
def generate_date_matrix_one_group(group):
    size = len(group)
    # Pad the group to have even number of participants
    if size % 2 == 1:
        size += 1
        group += ['']

    # Shuffle the group to randomize empty space
    random.shuffle(group)

    # Use round robin algorithm to generate date matrix
    round_robin = []

    for step_number in range(size - 1):
        mid = int(size / 2)
        l1 = group[:mid]
        l2 = group[mid:]
        l2.reverse()

        # Switch sides after each round
        if step_number % 2 == 1:
            round_robin = round_robin + [zip(l1, l2)]
        else:
            round_robin = round_robin + [zip(l2, l1)]

        group.insert(1, group.pop())

    # Add all participants to the result matrix
    result = {}
    for participant in group:
        result[participant] = {}

    round_number = 0
    for round_ in round_robin:
        for match in round_:
            # Add the pairings to the matrix
            result[match[0]][round_number] = match[1]
            result[match[1]][round_number] = match[0]
        round_number += 1

    return result


# Get the date matrix for the specified event
def get_date_matrix(event_id):
    result = cache.get(str(event_id))

    # Check if the matrix was cached
    if result is not None:
        LOGGER.debug('Cache hit for event id ' + str(event_id))
        return result

    LOGGER.debug('Generating a date matrix for event ' + str(event_id))

    # Get the event
    event = Event.objects.get(pk=event_id)
    event_groups = list(event.eventgroup_set.all())

    if event.numGroups == 1:
        # Get group participants
        group = []
        for participant in event_groups[0].get_registered_participants():
            group.append(participant.user.id)

        result = generate_date_matrix_one_group(group)
    elif event.numGroups == 2:
        # Get group a participants
        group_a = []
        for participant in event_groups[0].get_registered_participants():
            group_a.append(participant.user.id)

        # Get group b participants
        group_b = []
        for participant in event_groups[1].get_registered_participants():
            group_b.append(participant.user.id)

        # Generate the matrix
        result = generate_date_matrix_two_groups(group_a, group_b)
    else:
        result = {}

    # Store the matrix in cache for 2 hours
    cache.set(str(event_id), result, 60 * 60 * 2)

    return result


def get_user_dates(user_id, event_id):
    date_matrix = get_date_matrix(event_id)
    if user_id in date_matrix:
        result = {}
        for date_num in date_matrix[user_id]:
            date = date_matrix[user_id][date_num]
            # Check if the date is a gap
            if date == '':
                result[date_num] = {'fullName': 'wait', 'username': 'wait', 'id': -1}
            else:
                # Get user
                user = User.objects.get(pk=int(date))
                account = Account.objects.get(user=user)
                result[date_num] = {'fullName': account.fullName, 'username': user.username, 'id': user.id}

        return result
    else:
        return None


# Based on the timing of the event and the provided user, calculate the person they are supposed to talk to now
def get_current_date(user_id, event_id):
    try:
        # Try to find the event
        event = Event.objects.get(pk=event_id)
        # Get the time
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        # Check if the event is in progress
        if event.startDateTime > now or event.endDateTime < now:
            return None
        # Get the date matrix
        date_matrix = get_date_matrix(event_id)
        # Get number of seconds since the event's start
        time_diff = now - event.startDateTime
        time_diff_seconds = time_diff.seconds
        # Get the duration of a date
        date_duration = event.dateDuration + event.breakDuration
        # Get the number of the current date based on the time elapsed since event's start
        date_num = math.floor(time_diff_seconds / date_duration)

        # Check if the date number is not in the matrix
        if date_num not in date_matrix[user_id]:
            return None

        # Get the paired user based on the date matrix
        date = date_matrix[user_id][date_num]
        # Check if the date is a gap
        if date == '':
            return {'fullName': 'wait', 'username': 'wait', 'id': -1}

        # Get the user
        user = User.objects.get(pk=int(date))
        # Get the user's account
        account = Account.objects.get(user=user)
        return {'fullName': account.fullName, 'username': user.username, 'id': user.id}
    except Event.DoesNotExist:
        return None

# matrix = generate_date_matrix_two_groups(['bill', 'bob', 'bower', 'bottom'], ['alice', 'anna', 'akko'])
# print(matrix)
# print(matrix['bill'])
# print(matrix['bill'][0])
# print(matrix['bill'][1])
# print(matrix['bill'][2])
# print(matrix['bill'][3])
# print(matrix['alice'][0])

# matrix = generate_date_matrix_one_group(['a', 'b', 'c', 'd', 'e'])
# print (matrix)
