from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager



class CustomManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email= self.normalize_email(email)
        user=self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractUser):

    auth_token = models.CharField(max_length=32, blank=True, null=True)
    email=models.EmailField(unique=True)
    username= models.CharField(max_length=200)
    first_name= models.CharField(max_length=200)
    last_name= models.CharField(max_length=200)
    phone= models.CharField(max_length=12)
    is_active= models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['phone']
    objects = CustomManager()

class TodoFolder(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_folder_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    locked = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    priority = models.CharField(max_length=10,blank=True,null=True, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'user_folder_id')

    def __str__(self):
        return f"{self.user.username}'s folder: {self.name}"

class Todo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    folder = models.ForeignKey(TodoFolder,null=True, blank=True, on_delete=models.CASCADE, related_name='todos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title