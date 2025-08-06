from django.db import models


class Contactme(models.Model):
    name= models.CharField(max_length=50)
    phone_number=models.CharField(max_length=12)
    email=models.EmailField()
    message=models.CharField(max_length=1000)
