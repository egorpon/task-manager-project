from django.core.management import BaseCommand
from project.models import Project
from django.contrib.auth.models import User
from utils.random_due_date import generate_random_datetime
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = "Creates project sample data"

    def handle(self, *args, **options):

        Project.objects.all().delete()
        User.objects.all().delete()

        engine = settings.DATABASES['default']['ENGINE']
        with connection.cursor() as cursor:
            if 'postgresql' in engine:
                cursor.execute("SELECT setval(pg_get_serial_sequence('project_project', 'id'), 1, false);")
                cursor.execute("SELECT setval(pg_get_serial_sequence('auth_user', 'id'), 1, false);")

                
        User.objects.create_superuser(username="admin", password="test")

        User.objects.create_user(username="johnwick", password="test")
        User.objects.create_user(username="clarawild", password="test")
        User.objects.create_user(username="germanfricz", password="test")

        project = [
            Project(
                name="Website Redesign",
                description="Updating company's website design",
                due_date=generate_random_datetime(),
            ),
            Project(
                name="CRM Integration",
                description="Integrating with CRM-system",
                due_date=generate_random_datetime(),
            ),
            Project(
                name="Internal Tools",
                description="Developing tools for iternal use",
                due_date=generate_random_datetime(),
            ),
        ]

        Project.objects.bulk_create(project)
