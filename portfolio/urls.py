from django.urls import path
from . import views

urlpatterns = [
   path('data-get/',views.sendmail, name='send-email' )

]
