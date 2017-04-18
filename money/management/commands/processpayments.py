import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from web.models import Event

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Selects all attendees of events that will start in in the next 24 hours and charges their credit cards'

    # def add_arguments(self, parser):
    #     parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        end_time = timezone.datetime.now() + timezone.timedelta(hours=24)
        end_time = timezone.make_aware(end_time, timezone.get_current_timezone())

        events = Event.objects.filter(startDateTime__lte=end_time)

        self.stdout.write(self.style.SUCCESS('Billing for events starting before {}'.format(str(end_time))))

        for event in events:
            self.stdout.write(self.style.SUCCESS('Event {}\n\tStarts {}'.format(event.name, str(event.startDateTime))))
