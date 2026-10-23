"""Idempotent local demonstration data. All dealerships are fictional samples."""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dealership.models import Dealer, Review, CarMake, CarModel

DEALERS = [
    ('DriveWise Kansas City', '100 Demo Plaza', 'Kansas City', 'KS', '66101'),
    ('Sunflower Auto Center', '18 Sample Avenue', 'Wichita', 'KS', '67202'),
    ('Prairie Motor Group', '45 Training Boulevard', 'Topeka', 'KS', '66603'),
    ('Rocky Mountain Cars', '300 Sample Road', 'Denver', 'CO', '80202'),
    ('Lone Star Auto Gallery', '220 Example Street', 'Dallas', 'TX', '75201'),
    ('Golden Gate Motors', '7 Demo Lane', 'San Francisco', 'CA', '94102'),
    ('Desert Drive Center', '52 Example Way', 'Phoenix', 'AZ', '85001'),
    ('Lakefront Auto House', '69 Test Street', 'Chicago', 'IL', '60601'),
]
MAKES = {
    'Toyota': ['Camry', 'Corolla', 'RAV4'],
    'Honda': ['Civic', 'Accord', 'CR-V'],
    'Ford': ['Mustang', 'Escape', 'F-150'],
    'Hyundai': ['Elantra', 'Tucson'],
}

class Command(BaseCommand):
    help = 'Create safe, fictional sample dealerships, makes, models and a local demo user.'

    def handle(self, *args, **kwargs):
        user, created = get_user_model().objects.get_or_create(username='demo', defaults={
            'email': 'demo@example.invalid', 'first_name': 'Demo', 'last_name': 'User',
        })
        if created:
            user.set_password(os.environ.get('DRIVEWISE_DEMO_PASSWORD', 'DemoPass2026!'))
            user.save()
        for i, (name, address, city, state, zipcode) in enumerate(DEALERS):
            dealer, _ = Dealer.objects.get_or_create(name=name, defaults={
                'address': address, 'city': city, 'state': state, 'zipcode': zipcode,
                'phone': f'555-010{i + 1}',
                'description': 'Fictional showroom for testing and coursework demonstrations.',
            })
            if i in (0, 1, 3) and not Review.objects.filter(dealer=dealer, author=user).exists():
                Review.objects.create(
                    dealer=dealer, author=user, rating=5 - (i % 3),
                    review='Great service and a friendly team. This is a sample review.',
                )
        for make_name, model_names in MAKES.items():
            make, _ = CarMake.objects.get_or_create(name=make_name)
            for model_name in model_names:
                CarModel.objects.get_or_create(make=make, name=model_name)
        self.stdout.write(self.style.SUCCESS('Seed complete: fictional dealers, vehicles, local demo user.'))
