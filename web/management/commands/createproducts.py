from django.core.management.base import BaseCommand, CommandError

from money.models import Product


class Command(BaseCommand):
    help = 'Creates the 3 default products'

    def handle(self, *args, **options):
        if not Product.objects.filter(short_code='smallevent').exists():
            product1 = Product(name='Small Event', short_code='smallevent', amount=2000)
            product1.save()
            self.stdout.write(self.style.SUCCESS('Created product: {}'.format(str(product1))))

        if not Product.objects.filter(short_code='mediumevent').exists():
            product2 = Product(name='Medium Event', short_code='mediumevent', amount=3000)
            product2.save()
            self.stdout.write(self.style.SUCCESS('Created product: {}'.format(str(product2))))

        if not Product.objects.filter(short_code='largeevent').exists():
            product3 = Product(name='Large Event', short_code='largeevent', amount=4000)
            product3.save()
            self.stdout.write(self.style.SUCCESS('Created product: {}'.format(str(product3))))
