from django.urls import path
from . import views
from .views import RegisterView,LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    path('folders/', views.todo_folders, name='todo-folders'),  # GET all folders, POST new folder
    path('folders/<int:folder_id>/', views.todo_folders, name='folder-detail'),  # DELETE folder
    
    path('todos/', views.todos, name='todo-list'),  # GET all todos, POST new todo
    path('todos/<int:todo_id>/', views.todo_detail, name='todo-detail'),  # GET, PUT, DELETE specific todo
    path('folders/<int:folder_id>/verify/', views.verify_folder_password, name='verify_folder_password'), 
    
    path('folders/<int:folder_id>/todos/', views.todos_by_folder, name='todos-by-folder'),
]