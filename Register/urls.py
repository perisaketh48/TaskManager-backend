from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.Login, name='login'),
    
    path('folders/', views.todo_folders, name='todo-folders'),  # GET all folders, POST new folder
    path('folders/<int:folder_id>/', views.todo_folders, name='folder-detail'),  # DELETE folder
    
    path('todos/', views.todos, name='todo-list'),  # GET all todos, POST new todo
    path('todos/<int:todo_id>/', views.todo_detail, name='todo-detail'),  # GET, PUT, DELETE specific todo
    
    path('folders/<int:folder_id>/todos/', views.todos_by_folder, name='todos-by-folder'),
]