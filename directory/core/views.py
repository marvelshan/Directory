from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer, UpdateContactSerializer
from .tasks import send_contact_list_email


@api_view(["GET", "POST"])
def contact_list(request):
    if request.method == "GET":
        contacts = Contact.objects.filter(is_deleted=False)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def contact_detail(request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        serializer = UpdateContactSerializer(
            contact, data=request.data, partial=request.method == "PATCH"
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        contact.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def search_contact(request):
    name = request.query_params.get("name")
    phone_number = request.query_params.get("phone_number")

    contacts = Contact.objects.filter(
        is_deleted=False,
        name__icontains=name,
        phone_number__icontains=phone_number,
    )
    serializer = ContactSerializer(contacts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def export_contacts(request):
    contacts = Contact.objects.filter(is_deleted=False)
    serializer = ContactSerializer(contacts, many=True)

    # Sending email using Celery task
    send_contact_list_email.delay(serializer.data)

    return Response(
        {"message": "Exporting contact list. An email will be sent shortly."},
        status=status.HTTP_200_OK,
    )
