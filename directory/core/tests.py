from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Contact


class ContactAPITestCase(APITestCase):
    def setUp(self):
        self.contact_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890",
        }
        self.contact = Contact.objects.create(**self.contact_data)

    def test_get_contact_detail(self):
        url = reverse("contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data_filtered = [
            {
                k: v
                for k, v in item.items()
                if k not in ["id", "created_at", "updated_at", "is_deleted"]
            }
            for item in response.data
        ]
        self.assertEqual(response_data_filtered[0], self.contact_data)

    def test_update_contact(self):
        updated_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "phone_number": "9876543210",
        }
        url = reverse("contact_detail", kwargs={"pk": self.contact.pk})
        response = self.client.put(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, updated_data)

    def test_partial_update_contact(self):
        partial_data = {"phone_number": "9876543210"}
        url = reverse("contact_detail", kwargs={"pk": self.contact.pk})
        response = self.client.patch(url, partial_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertEqual(
            self.contact.phone_number, partial_data["phone_number"]
        )

    def test_delete_contact(self):
        url = reverse("contact_detail", kwargs={"pk": self.contact.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["is_deleted"], True)

    def test_search_contact(self):
        url = reverse("search_contact")
        search_params = {"name": "John Doe", "phone_number": "1234567890"}
        response = self.client.get(url, search_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data_filtered = [
            {
                k: v
                for k, v in item.items()
                if k not in ["id", "created_at", "updated_at", "is_deleted"]
            }
            for item in response.data
        ]
        self.assertEqual(response_data_filtered[0], self.contact_data)
