from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from task.models import Task, AssignedUser
from comment.models import Comment
from project.models import Project
from django.urls import reverse
from utils.random_due_date import generate_random_datetime
from rest_framework import status
from django.utils import timezone


# Create your tests here.
class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="test"
        )
        self.normal_user = User.objects.create_user(username="mr_fox", password="test")
        self.project = Project.objects.create(
            name="Website Redesign",
            description="Updating company's website design",
            due_date=generate_random_datetime(),
        )

        self.task = Task.objects.create(
            name="Design homepage mockup",
            description="Test Description",
            priority=Task.PriorityChoices.LOW,
            project=self.project,
            due_date=self.project.due_date - timezone.timedelta(days=2),
        )
        AssignedUser.objects.create(user=self.normal_user, task=self.task)

        self.comment = Comment.objects.create(
            task=self.task, text="Some Comment", posted_by=self.normal_user
        )

        self.list_url = reverse("comment-list")
        self.create_url = reverse("comment-create")
        self.detail_url = reverse(
            "comment-detail", kwargs={"comment_id": self.comment.id}
        )
        self.update_url = reverse(
            "comment-update", kwargs={"comment_id": self.comment.id}
        )
        self.delete_url = reverse(
            "comment-delete", kwargs={"comment_id": self.comment.id}
        )

    def test_authenticated_user_can_leave_comments(self):
        data = {"task_id": self.task.id, "text": "Admin petuh"}

        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Admin petuh", response.data["text"])

        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Admin petuh", response.data["text"])

    def test_unauthenticated_user_cannot_leave_comments(self):
        data = {"task_id": self.task.id, "text": "Admin petuh"}

        self.client.logout()
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get_comments_list(self):
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_get_comments_list(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_can_update_comment(self):
        data = {"text": "Admin krasavchik"}
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.put(self.update_url, data)
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Admin krasavchik", data["text"])
        self.assertEqual(self.comment.text, data["text"])

    def test_normal_user_can_update_comment(self):
        data = {"text": "Admin krasavchik"}
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Admin krasavchik", data["text"])
        self.assertEqual(self.comment.text, data["text"])

    def test_authenticated_user_cannot_update_comment(self):
        data = {"text": "Admin krasavchik"}
        self.client.logout()
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_delete_comment(self):
        self.client.login(username="admin", password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_normal_user_can_delete_comment(self):
        self.client.login(username="mr_fox", password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_unauthenticated_user_cannot_delete_comment(self):
        self.client.logout()
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
