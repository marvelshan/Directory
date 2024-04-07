from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer, UpdateContactSerializer
from .tasks import send_contact_list_email


class ContactList(APIView):
    def get(self, request):
        contacts = Contact.objects.filter(is_deleted=False)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetail(APIView):
    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def put(self, request, pk):
        contact = self.get_object(pk)
        serializer = UpdateContactSerializer(
            contact, data=request.data, partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        contact = self.get_object(pk)
        serializer = UpdateContactSerializer(
            contact, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = self.get_object(pk)
        contact.soft_delete()
        serializer = ContactSerializer(contact)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class SearchContact(APIView):
    def get(self, request):
        name = request.query_params.get("name")
        phone_number = request.query_params.get("phone_number")

        contacts = Contact.objects.filter(
            is_deleted=False,
            name__icontains=name,
            phone_number__icontains=phone_number,
        )
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)


class ExportContacts(APIView):
    def get(self, request):
        contacts = Contact.objects.filter(is_deleted=False)
        serializer = ContactSerializer(contacts, many=True)

        # Sending email using Celery task
        send_contact_list_email.delay(serializer.data)

        return Response(
            {
                "message": "Exporting contact list. An email will be sent shortly."
            },
            status=status.HTTP_200_OK,
        )
