import logging

from .models import Product

LOGGER = logging.getLogger(__name__)

# Constants, must match product IDs in database
SMALL_EVENT_ID = 'smallevent'
MEDIUM_EVENT_ID = 'mediumevent'
LARGE_EVENT_ID = 'largeevent'


# Return a product based on the number of participants in the event
def get_product_by_participant_number(participant_number):
    try:
        if participant_number <= 10:
            return Product.objects.get(short_code=SMALL_EVENT_ID)
        elif participant_number <= 20:
            return Product.objects.get(short_code=MEDIUM_EVENT_ID)
        else:
            return Product.objects.get(short_code=LARGE_EVENT_ID)

    except Product.DoesNotExist:
        raise Exception('Product was not defined')
