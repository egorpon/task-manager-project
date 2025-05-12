from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from task.models import Task, AssignedUser
from comment.models import Comment
from project.models import Project
from django.urls import reverse
from utils.random_due_date import generate_random_datetime
from rest_framework import status
from django.utils import timezone
from pprint import pprint


# Create your tests here.
class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="test"
        )
        self.owner = User.objects.create_user(username="mr_fox", password="test")
        self.normal_user = User.objects.create_user(
            username="normal_user", password="test"
        )
        self.project = Project.objects.create(
            name="Website Redesign",
            description="Updating company's website design",
            owner=self.owner,
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

    def test_admin_can_leave_comment_on_any_task(self):
        data = {"task_id": self.task.id, "text": "TEXT"}
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("TEXT", response.data["text"])

    def test_owner_can_leave_comment_on_own_task(self):
        data = {"task_id": self.task.id, "text": "TEXT"}
        self.client.login(username=self.owner.username, password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("TEXT", response.data["text"])

    def test_assigned_user_can_leave_comment_on_task(self):
        data = {"task_id": self.task.id, "text": "TEXT"}
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("TEXT", response.data["text"])

    def test_unauthenticated_user_cannot_leave_comments(self):
        data = {"task_id": self.task.id, "text": "Admin petuh"}

        self.client.logout()
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_delete_any_comments_on_own_task(self):
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_owner_can_delete_any_comments_on_own_task(self):
        self.client.login(username=self.owner.username, password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_assigned_user_cannot_delete_any_comments_on_task(self):
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_admin_can_update_comments_on_any_task(self):
        data = {"text": "Admin krasavchik"}
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, response.data["text"])

    def test__assigned_user_can_update_comments_on_task(self):
        data = {"text": "Admin krasavchik"}
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, response.data["text"])

    def test_owner_can_update_comments_on_ow_task(self):
        comment = Comment.objects.create(
            task=self.task, posted_by=self.owner, text="Some Comment"
        )
        data = {"text": "Admin krasavchik"}
        self.client.login(username=self.owner.username, password="test")
        response = self.client.put(f"/comments/{comment.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, response.data["text"])

    def test_admin_can_view_all_comments(self):
        comment = Comment.objects.create(
            task=self.task, posted_by=self.owner, text="Comment"
        )
        self.client.login(username=self.admin_user.username, password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["text"], self.comment.text)
        self.assertEqual(response.data["results"][1]["text"], comment.text)

    def test_owner_can_view_all_comments_on_own_and_assigned_task(self):
        project = Project.objects.create(
            name="Website Redesign",
            description="Updating company's website design",
            owner=self.normal_user,
            due_date=generate_random_datetime(),
        )

        task = Task.objects.create(
            name="Design homepage mockup",
            description="Test Description",
            priority=Task.PriorityChoices.LOW,
            project=project,
            due_date=project.due_date - timezone.timedelta(days=2),
        )

        AssignedUser.objects.create(task=task, user=self.owner)
        AssignedUser.objects.create(task=task, user=self.normal_user)

        comment = Comment.objects.create(
            task=self.task, posted_by=self.normal_user, text="Comment"
        )
        self.client.login(username=self.owner.username, password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["text"], self.comment.text)
        self.assertEqual(response.data["results"][1]["text"], comment.text)

    def test_normal_user_can_view_comments_on_assigned_task(self):
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["text"], self.comment.text)

    def test_normal_user_cannot_comment_on_task_from_not_owned_project_or_unassigned_task(
        self,
    ):
        project = Project.objects.create(
            name="Website Redesign",
            description="Updating company's website design",
            owner=self.admin_user,
        )

        task = Task.objects.create(
            name="test",
            description="test description",
            priority=Task.PriorityChoices.HIGH,
            project_id=project.id,
        )
        comment = {"task_id": task.id, "text": "text"}
        self.client.login(username=self.normal_user.username, password="test")
        response = self.client.post(
            self.create_url,
            comment,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "You cannot write comment on other task", response.data["task_id"][0]
        )
