from django.utils import timezone
import random


def generate_random_datetime(days_ahead=30):
    days = random.randint(0, days_ahead)
    hours = random.randint(8, 20)
    minutes = random.choice([0, 15, 45, 30])
    return timezone.now() + timezone.timedelta(days=days, hours=hours, minutes=minutes)
