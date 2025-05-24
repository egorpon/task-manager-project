from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_assigned_task_email(task_id, user_emails):
    print(f"Sending email to {user_emails} for task {task_id}")
    subject =  'Assigned Task'
    message = f"You have been assigned task {task_id}, please check it out"
    from_email = settings.DEFAULT_FROM_EMAIL

    return send_mail(subject, message, from_email, recipient_list=user_emails)