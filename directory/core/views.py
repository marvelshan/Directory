from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer, UpdateContactSerializer
from .tasks import send_contact_list_email


class ContactList(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request):
        contacts = Contact.objects.filter(is_deleted=False)
        serializer = self.serializer_class(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetail(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    update_serializer_class = UpdateContactSerializer

    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        contact = self.get_object(pk)
        serializer = self.serializer_class(contact)
        return Response(serializer.data)

    def put(self, request, pk):
        contact = self.get_object(pk)
        serializer = self.update_serializer_class(
            contact, data=request.data, partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        contact = self.get_object(pk)
        serializer = self.update_serializer_class(
            contact, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = self.get_object(pk)
        contact.soft_delete()
        serializer = self.serializer_class(contact)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class SearchContact(viewsets.ModelViewSet):
    serializer_class = ContactSerializer

    def get(self, request):
        name = request.query_params.get("name")
        phone_number = request.query_params.get("phone_number")

        contacts = Contact.objects.filter(
            is_deleted=False,
            name__icontains=name,
            phone_number__icontains=phone_number,
        )
        serializer = self.serializer_class(contacts, many=True)
        return Response(serializer.data)


class ExportContacts(viewsets.ModelViewSet):
    serializer_class = ContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(is_deleted=False)

    def get(self, request):
        contacts = self.get_queryset()
        serializer = self.serializer_class(contacts, many=True)

        # Sending email using Celery task
        send_contact_list_email.delay(serializer.data)

        return Response(
            {
                "message": "Exporting contact list. An email will be sent shortly."
            },
            status=status.HTTP_200_OK,
        )
