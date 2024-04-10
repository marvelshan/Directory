from django.urls import path
from . import views


urlpatterns = [
    path(
        "",
        views.ContactList.as_view({"get": "get", "post": "post"}),
        name="contact_list",
    ),
    path(
        "<int:pk>/",
        views.ContactDetail.as_view(
            {"get": "get", "patch": "patch", "put": "put", "delete": "delete"}
        ),
        name="contact_detail",
    ),
    path(
        "search/",
        views.SearchContact.as_view({"get": "get"}),
        name="search_contact",
    ),
    path(
        "export/",
        views.ExportContacts.as_view({"get": "get"}),
        name="export_contacts",
    ),
]
