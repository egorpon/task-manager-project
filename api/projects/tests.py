from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from task.models import Task, AssignedUser
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

        self.list_url = reverse("project-list")
        self.create_url = reverse("project-create")
        self.detail_url = reverse(
            "project-detail", kwargs={"project_id": self.project.id}
        )
        self.update_url = reverse(
            "project-update", kwargs={"project_id": self.project.id}
        )
        self.delete_url = reverse(
            "project-delete", kwargs={"project_id": self.project.id}
        )

    def test_only_authenticated_user_can_view_project_list(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username="mr_fox", password="test")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_can_create_project(self):
        data = {
            "name": "test",
            "description": "test description",
            "due_date": generate_random_datetime(),
        }

        self.client.login(username="admin", password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.login(username="mr_fox", password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_due_date_in_past_raises_error(self):
        data = {
            "name": "test",
            "description": "test description",
            "due_date": timezone.now() - timezone.timedelta(days=5),
        }

        self.client.login(username="admin", password="test")
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["due_date"][0], "Date cannot be earlier than current time"
        )

    def test_only_authenticated_can_view_project_detail(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username="mr_fox", password="test")
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_can_update_project(self):
        data = {
            "name": "Updated test",
            "description": "Updated test description",
            "due_date": generate_random_datetime(),
        }

        self.client.login(username="admin", password="test")
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.project.refresh_from_db()

        self.assertEqual(self.project.name, data["name"])
        self.assertEqual(self.project.description, data["description"])
        self.assertEqual(self.project.due_date, data["due_date"])

        self.client.login(username="mr_fox", password="test")
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_can_partial_update_project(self):
        data = {
            "name": "Partial Updated test",
        }

        self.client.login(username="admin", password="test")
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, data["name"])

        self.client.login(username="mr_fox", password="test")
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_delete_project(self):
        self.client.login(username="admin", password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_normal_user_cannot_delete_project(self):
        self.client.login(username="mr_fox", password="test")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_unauthenticated_user_cannot_delete_project(self):
        self.client.logout()
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
