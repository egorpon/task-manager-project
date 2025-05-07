from django.core.management import BaseCommand
from comment.models import Comment
from task.models import Task
from django.contrib.auth.models import User
from django.utils import lorem_ipsum
from random import choice
from django.db import connection


class Command(BaseCommand):
    help = "Creates сomments sample data"

    def handle(self, *args, **options):
        Comment.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='comment_comment';")

        users = User.objects.all()
        tasks = Task.objects.all()
        for i in range(10):
            user = choice(users)
            task = choice(tasks)
            Comment.objects.create(
                text=lorem_ipsum.paragraph(), posted_by=user, task=task
            )
