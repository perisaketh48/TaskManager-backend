from django.urls import path
from . import views

urlpatterns = [
   path('data-get/',views.send_contact_message, name="send_contact_message"),
    # --------------------------
    # ADMIN APIs
    # --------------------------
    path("admin/messages/", views.get_all_messages, name="get_all_messages"),
    path("admin/messages/<int:msg_id>/", views.get_message, name="get_message"),
    path("admin/messages/<int:msg_id>/delete/", views.delete_message, name="delete_message"),
    path("admin/messages/export/csv/", views.export_messages_csv, name="export_messages_csv"),
]
