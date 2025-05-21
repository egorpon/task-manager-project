from django.core.management import BaseCommand
from comment.models import Comment
from task.models import Task
from django.contrib.auth.models import User
from django.utils import lorem_ipsum
from random import choice
from django.db import connection
from django.conf import settings



class Command(BaseCommand):
    help = "Creates comments sample data"

    def handle(self, *args, **options):
        Comment.objects.all().delete()

        engine = settings.DATABASES['default']['ENGINE']
        with connection.cursor() as cursor:
            if 'postgresql' in engine:
                cursor.execute("SELECT setval(pg_get_serial_sequence('comment_comment', 'id'), 1, false);")

        users = User.objects.all()
        tasks = Task.objects.all()
        for i in range(10):
            user = choice(users)
            task = choice(tasks)
            Comment.objects.create(
                text=lorem_ipsum.paragraph(), posted_by=user, task=task
            )
