import logging
import math
import random
import sys

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from opentok import OpenTok

from account.models import Account
from account.models import Memo
from .models import Conversation

api_key = settings.TOKBOX_KEY
api_secret = settings.TOKBOX_SECRET

LOGGER = logging.getLogger(__name__)
IS_TESTING = sys.argv[1:2] == ['test']


# Function to generate conversations for all participants in the event
def generate_conversations(event):
    event_groups = list(event.eventgroup_set.all())
    opentok_api = OpenTok(api_key, api_secret)

    # Generate a date matrix for the event
    if event.numGroups == 1:
        # Get group participants
        group = []
        for participant in event_groups[0].get_registered_participants():
            group.append(participant.user)

        __generate_conversations_one_group(event, group, opentok_api)
    elif event.numGroups == 2:
        # Get group a participants
        group_a = []
        for participant in event_groups[0].get_registered_participants():
            group_a.append(participant.user)

        # Get group b participants
        group_b = []
        for participant in event_groups[1].get_registered_participants():
            group_b.append(participant.user)

        # Generate the matrix
        __generate_conversations_two_groups(event, group_a, group_b, opentok_api)


# Function to generate a matrix of dates based on two lists of participants
def __generate_conversations_two_groups(event, group_a, group_b, opentok_api):
    # Get the maximum number of participants
    size = max(len(group_a), len(group_b))

    # Pad the groups to be the same size
    group_a += [None] * (size - len(group_a))
    group_b += [None] * (size - len(group_b))

    # Shuffle the groups to randomize empty spaces
    random.shuffle(group_a)
    random.shuffle(group_b)

    for participant_a_index in range(size):
        participant_a = group_a[participant_a_index]
        for step_number in range(size):
            # Get the paired participant
            participant_b_index = (participant_a_index + step_number) % size
            participant_b = group_b[participant_b_index]

            # Create the conversations
            __create_conversation_pair(event, participant_a, participant_b, step_number, opentok_api)


# Function to generate a matrix of dates based on one list of participants
def __generate_conversations_one_group(event, group, opentok_api):
    size = len(group)
    # Pad the group to have even number of participants
    if size % 2 == 1:
        size += 1
        group += [None]

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

    round_number = 0
    for rnd in round_robin:
        for match in rnd:
            # Create the conversations
            __create_conversation_pair(event, match[0], match[1], round_number, opentok_api)
        round_number += 1


# Create the session for the conversation
def __create_session(opentok_api, user1, user2):
    if user1 is None and user2 is None:
        return None

    # Create the session for the conversation
    if IS_TESTING:
        return get_random_string(length=32)
    else:
        # Create a session that attempts to send streams directly between clients (falling back
        # to use the OpenTok TURN server to relay streams if the clients cannot connect):
        session = opentok_api.create_session()
        # A session that uses the OpenTok Media Router, which is required for archiving
        # session = opentok_api.create_session(media_mode=MediaModes.routed, archive_mode=ArchiveModes.always)
        return session.session_id


def __create_conversation_pair(event, user1, user2, order, opentok_api):
    session_id = __create_session(opentok_api, user1, user2)

    if user1:
        account = None
        memo = None
        if user2:
            account = Account.objects.get(user=user2)
            memo = Memo.objects.get_or_create_memo(user1, user2)

        conversation = Conversation(event=event, user=user1, order=order, sessionID=session_id,
                                    interlocutorUser=user2, interlocutorAccount=account, interlocutorMemo=memo)
        conversation.save()

    if user2:
        account = None
        memo = None
        if user1:
            account = Account.objects.get(user=user1)
            memo = Memo.objects.get_or_create_memo(user2, user1)

        conversation = Conversation(event=event, user=user2, order=order, sessionID=session_id,
                                    interlocutorUser=user1, interlocutorAccount=account, interlocutorMemo=memo)
        conversation.save()


# Get all dates for the given user in the given event
def get_user_dates(user, event):
    conversations = Conversation.objects.filter(event=event, user=user).order_by('order')
    result = []
    for conversation in conversations:
        if conversation.interlocutorUser:
            date = {
                'is_break': False,
                'order': conversation.order,
                'user': conversation.interlocutorUser,
                'account': conversation.interlocutorAccount,
                'memo': conversation.interlocutorMemo,
                'sessionID': conversation.sessionID
            }
        else:
            date = {
                'is_break': True,
                'order': conversation.order,
                'user': None,
                'account': None,
                'memo': None,
                'sessionID': None
            }

        result.append(date)

    logging.info('dates ' + str(result))

    return result


# Based on the timing of the event and the provided user, calculate the person they are supposed to talk to now
def get_current_date(user, event):
    # Get the time
    now = timezone.now()
    # Get number of seconds since the event's start
    time_diff = now - event.startDateTime
    time_diff_seconds = time_diff.total_seconds()
    # Get the duration of a date
    date_and_break_duration = event.dateDuration + event.breakDuration
    # Get the number of the current date based on the time elapsed since event's start
    date_num = math.floor(time_diff_seconds / date_and_break_duration)
    # Get time passed since the date started
    time_passed = time_diff_seconds % date_and_break_duration
    # Is date active or on a break
    is_active = time_passed < event.dateDuration
    # Calculate the time until reload must happen
    time_until_reload = event.dateDuration - time_passed
    if not is_active:
        time_until_reload = date_and_break_duration - time_passed

    # Find conversation object
    try:
        conversation = Conversation.objects.get(event=event, user=user, order=date_num)
        details = ConversationDetails()
        details.is_active = is_active
        details.time_passed = time_passed
        details.conversation_id = conversation.id
    except Conversation.DoesNotExist:
        return None

    # Try to get the next date
    try:
        next_conversation = Conversation.objects.get(event=event, user=user, order=(date_num + 1))
        next_date = ConversationDetails()
        if next_conversation.interlocutorUser:
            next_date.is_break = False
            next_date.user = next_conversation.interlocutorUser
            next_date.account = next_conversation.interlocutorAccount
            next_date.memo = next_conversation.interlocutorMemo
        else:
            next_date.is_break = True
    except Conversation.DoesNotExist:
        next_date = None

    if conversation.interlocutorUser:
        details.is_break = False
        details.user = conversation.interlocutorUser
        details.account = conversation.interlocutorAccount
        details.memo = conversation.interlocutorMemo
        details.session_id = conversation.sessionID
        details.time_until_reload = time_until_reload
        details.next_date = next_date
    else:
        details.is_break = True
        details.user = None
        details.account = None
        details.memo = None
        details.session_id = None
        details.time_until_reload = date_and_break_duration - time_passed
        details.next_date = next_date

    return details


class ConversationDetails:
    pass
