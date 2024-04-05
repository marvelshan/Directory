from django.urls import path
from . import views


urlpatterns = [
    path("", views.contact_list),
    path("<int:pk>/", views.contact_detail),
    path("search/", views.search_contact),
    path("export/", views.export_contacts),
]
