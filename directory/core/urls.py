from django.urls import path
from . import views


urlpatterns = [
    path("", views.ContactList.as_view(), name="contact_list"),
    path("<int:pk>/", views.ContactDetail.as_view(), name="contact_detail"),
    path("search/", views.SearchContact.as_view(), name="search_contact"),
    path("export/", views.ExportContacts.as_view(), name="export_contacts"),
]
