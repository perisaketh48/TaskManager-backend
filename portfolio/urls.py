from django.urls import path
from . import views

urlpatterns = [
   path('data-get/',views.send_whatsapp_message, name='send_whatsapp_message' )

]
