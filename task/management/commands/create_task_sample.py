from django.core.management import BaseCommand
from task.models import Task, AssignedUser, Project, User
from utils.random_due_date import generate_random_datetime
from django.utils import lorem_ipsum
from random import choice
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = "Creates task sample data"

    def handle(self, *args, **options):
        Task.objects.all().delete()
        AssignedUser.objects.all().delete()

        engine = settings.DATABASES['default']['ENGINE']
        with connection.cursor() as cursor:
            if 'postgresql' in engine:
                cursor.execute("SELECT setval(pg_get_serial_sequence('task_task', 'id'), 1, false);")
                cursor.execute("SELECT setval(pg_get_serial_sequence('task_assigneduser', 'id'), 1, false);")

        high = Task.PriorityChoices.HIGH
        medium = Task.PriorityChoices.MEDIUM
        low = Task.PriorityChoices.LOW

        pending = Task.StatusChoices.PENDING
        in_progress = Task.StatusChoices.IN_PROGRESS
        completed = Task.StatusChoices.COMPLETED

        task = [
            Task(
                name="Design homepage mockup",
                description=lorem_ipsum.paragraph(),
                priority=choice([high, medium, low]),
                status=choice([pending, in_progress, completed]),
                project=Project.objects.get(name="Website Redesign"),
                due_date=generate_random_datetime(),
            ),
            Task(
                name="Connect backend to CRM",
                description=lorem_ipsum.paragraph(),
                priority=choice([high, medium, low]),
                status=choice([pending, in_progress, completed]),
                project=Project.objects.get(name__icontains="CRM Integration"),
                due_date=generate_random_datetime(),
            ),
            Task(
                name="Add filters to admin panel",
                description=lorem_ipsum.paragraph(),
                priority=choice([high, medium, low]),
                status=choice([pending, in_progress, completed]),
                project=Project.objects.get(name__icontains="Internal Tools"),
                due_date=generate_random_datetime(),
            ),
            Task(
                name="Optimize image loading",
                description=lorem_ipsum.paragraph(),
                priority=choice([high, medium, low]),
                status=choice([pending, in_progress, completed]),
                project=Project.objects.get(name__icontains="Website Redesign"),
                due_date=generate_random_datetime(),
            ),
            Task(
                name="Add email notifications",
                description=lorem_ipsum.paragraph(),
                priority=choice([high, medium, low]),
                status=choice([pending, in_progress, completed]),
                project=Project.objects.get(name__icontains="Internal Tools"),
                due_date=generate_random_datetime(),
            ),
        ]

        Task.objects.bulk_create(task)

        tasks = Task.objects.all()
        users = User.objects.all()
        assigned_pairs = set()

        for i in range(8):
            user = choice(users)
            while True:
                task = choice(tasks)
                if (user.id, task.id) not in assigned_pairs:
                    break

            AssignedUser.objects.create(user=user, task=task)
            assigned_pairs.add((user.id, task.id))
