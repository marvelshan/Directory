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
