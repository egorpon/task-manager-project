from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random


def generate_random_datetime(days_ahead=30):
    tz = ZoneInfo("EET")
    days = random.randint(0, days_ahead)
    hours = random.randint(8, 20)
    minutes = random.choice([0, 15, 45, 30])
    return datetime.now(tz=tz) + timedelta(days=days, hours=hours, minutes=minutes)
