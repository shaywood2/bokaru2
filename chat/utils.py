import logging
import random

from django.core.cache import caches

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


# Get the date matrix for the specified event
def get_date_matrix(event_id):
    # Look up the matrix in cache
    cache = caches['date_matrices']
    result = cache.get(str(event_id))

    if result is None:
        LOGGER.debug('Generating a date matrix for event ' + str(event_id))
        # Generate the matrix
        result = generate_date_matrix_two_groups(['bill', 'bob', 'bower', 'bottom'], ['alice', 'anna', 'akko'])
        # Store the matrix in cache
        cache.set(str(event_id), result, 60 * 60 * 2)
    else:
        LOGGER.debug('Cache hit for event id ' + str(event_id))

    return result


matrix = get_date_matrix(123)
print(matrix)
print(matrix['bill'])
print(matrix['bill'][0])
print(matrix['bill'][1])
print(matrix['bill'][2])
print(matrix['bill'][3])
print(matrix['alice'][0])
