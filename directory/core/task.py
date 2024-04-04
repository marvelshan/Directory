from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_contact_list_email(contact_data):
    # Convert contact data to string format for email body
    email_body = "\n".join(
        [f"{contact['name']}: {contact['email']}" for contact in contact_data]
    )

    # Send email
    send_mail(
        "Contact List",
        email_body,
        "from@example.com",
        ["to@example.com"],
        fail_silently=False,
    )
