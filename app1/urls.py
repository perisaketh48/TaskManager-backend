from django.urls import path
from . import views  # Make sure you have views.py with some views

urlpatterns = [
    path('', views.home, name='home'),  # Example path
]