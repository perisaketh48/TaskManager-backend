from django.shortcuts import render 
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json
from .models import CustomUser, Todo, TodoFolder
from rest_framework import status
import secrets
from datetime import datetime

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        data = json.loads(request.body)
        email = data.get('email') 
        password = data.get('password')
        first_name = data.get('first_name') 
        last_name = data.get('last_name') 
        phone = data.get('phone') 

        if not all([email, password, first_name, last_name, phone]):
            return JsonResponse({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=status.HTTP_409_CONFLICT)
        
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        return JsonResponse({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
   
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                token = secrets.token_urlsafe(12)
                user.auth_token = token
                user.save()
                
                return JsonResponse({
                    'message': 'Login successful',
                    'token': token,
                    'user_id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def todo_folders(request, folder_id=None):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Authorization Token required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        user = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        folders = TodoFolder.objects.filter(user=user).order_by('-created_at')
        
        data = [{
            'id': folder.id,
            'user_folder_id': folder.user_folder_id,
            'name': folder.name,
            'description': folder.description,
            'locked': folder.locked,
            'priority': folder.priority,
            'created_at': folder.created_at,
            'updated_at': folder.updated_at,
            'todo_count': folder.todos.count()
        } for folder in folders]

        return JsonResponse(data, safe=False, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            locked = data.get('locked', False)
            password = data.get('password', '') if locked else None
            priority = data.get('priority', 'medium')

            if not name:
                return JsonResponse({'error': 'Folder name is required'}, status=status.HTTP_400_BAD_REQUEST)

            if locked and not password:
                return JsonResponse({'error': 'Password is required for locked folders'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the next user_folder_id
            last_folder = TodoFolder.objects.filter(user=user).order_by('-user_folder_id').first()
            next_user_folder_id = 1 if not last_folder else last_folder.user_folder_id + 1

            folder = TodoFolder.objects.create(
                user=user,
                user_folder_id=next_user_folder_id,
                name=name,
                description=description,
                locked=locked,
                password=password,
                priority=priority
            )

            return JsonResponse({
                'id': folder.id,
                'user_folder_id': folder.user_folder_id,
                'name': folder.name,
                'description': folder.description,
                'locked': folder.locked,
                'priority': folder.priority,
                'created_at': folder.created_at
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            folder_id = data.get('folder_id')
            
            if not folder_id:
                return JsonResponse({'error': 'Folder ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                folder = TodoFolder.objects.get(id=folder_id, user=user)
                
                # Check if folder is locked and password is correct
                if folder.locked:
                    password = data.get('password')
                    if not password or password != folder.password:
                        return JsonResponse(
                            {'error': 'Incorrect password for this folder'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                
                folder.delete()
                return JsonResponse(
                    {'message': 'Folder deleted successfully'}, 
                    status=status.HTTP_204_NO_CONTENT
                )
            except TodoFolder.DoesNotExist:
                return JsonResponse({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            folder_id = data.get('folder_id')
            
            if not folder_id:
                return JsonResponse({'error': 'Folder ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                folder = TodoFolder.objects.get(id=folder_id, user=user)
                
                
                # Update folder properties
                name = data.get('name')
                description = data.get('description')
                locked = data.get('locked')
                new_password = data.get('password')
                priority = data.get('priority')
                
                if name is not None:
                    folder.name = name
                if description is not None:
                    folder.description = description
                if priority is not None:
                    folder.priority = priority
                
                # Handle locking/unlocking logic
                if locked is not None:
                    if locked and not new_password:
                        return JsonResponse(
                            {'error': 'New password is required when locking a folder'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    folder.locked = locked
                    if locked:
                        folder.password = new_password
                    else:
                        folder.password = None
                
                folder.save()
                
                return JsonResponse({
                    'id': folder.id,
                    'user_folder_id': folder.user_folder_id,
                    'name': folder.name,
                    'description': folder.description,
                    'locked': folder.locked,
                    'priority': folder.priority,
                    'updated_at': folder.updated_at
                }, status=status.HTTP_200_OK)
                
            except TodoFolder.DoesNotExist:
                return JsonResponse({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
def verify_folder_password(request, folder_id):
    # Authentication check
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse(
            {'error': 'Authorization Token required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = auth_header.split(' ')[1]
    
    try:
        user = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'error': 'Invalid token'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Only POST method allowed'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        
        try:
            folder = TodoFolder.objects.get(id=folder_id, user=user)
        except TodoFolder.DoesNotExist:
            return JsonResponse(
                {'error': 'Folder not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Parse request data
        data = json.loads(request.body)
        password = data.get('password')
        
        if not password:
            return JsonResponse(
                {'error': 'Password is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify password
        if folder.locked:
            if password == folder.password:
                return JsonResponse(
                    {'message': 'Password verified successfully'}, 
                    status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {'error': 'Incorrect password'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return JsonResponse(
                {'message': 'Folder is not locked, no password required'}, 
                status=status.HTTP_200_OK
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
def todos(request):
    # Authentication check
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse(
            {'error': 'Authorization Token required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = auth_header.split(' ')[1]
    
    try:
        user = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'error': 'Invalid token'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    if request.method == 'GET':
        try:
            todos = Todo.objects.filter(user=user).order_by('-created_at')
            
            data = {
                'todos': [{
                    'id': todo.id,
                    'title': todo.title,
                    'description': todo.description,
                    'status': todo.status,
                    'priority': todo.priority,
                    'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
                    'completed': todo.completed,
                    'created_at': todo.created_at,
                    'updated_at': todo.updated_at
                } for todo in todos]
            }

            return JsonResponse(data, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('name') or data.get('title')  # Accept both field names
            folder_id = data.get('folder_id')
            description = data.get('description', '')
            priority = data.get('status') or data.get('priority', 'medium')  # Accept both
            due_date = data.get('due_date')
            completed = data.get('completed', False)

            # Validation
            if not title:
                return JsonResponse(
                    {'error': 'Title is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if not folder_id:
                return JsonResponse(
                    {'error': 'Folder ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                folder = TodoFolder.objects.get(id=folder_id, user=user)
                
                
                # Parse date
                parsed_due_date = None
                if due_date:
                    try:
                        parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                    except ValueError:
                        return JsonResponse(
                            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Create todo
                todo = Todo.objects.create(
                    user=user,
                    folder=folder,
                    title=title,
                    description=description,
                    status='pending',
                    priority=priority,
                    due_date=parsed_due_date,
                    completed=completed
                )

                return JsonResponse({
                    'id': todo.id,
                    'folder_id': todo.folder.id,
                    'title': todo.title,
                    'description': todo.description,
                    'status': todo.status,
                    'priority': todo.priority,
                    'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
                    'completed': todo.completed,
                    'created_at': todo.created_at
                }, status=status.HTTP_201_CREATED)

            except TodoFolder.DoesNotExist:
                return JsonResponse(
                    {'error': 'Folder not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return JsonResponse(
        {'error': 'Method not allowed'}, 
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

@csrf_exempt
def todo_detail(request, todo_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Authorization Token required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        user = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        todo = Todo.objects.get(id=todo_id, user=user)
    except Todo.DoesNotExist:
        return JsonResponse({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return JsonResponse({
            'id': todo.id,
            'folder_id': todo.folder.id,
            'title': todo.title,
            'description': todo.description,
            'status': todo.status,
            'priority': todo.priority,
            'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
            'completed': todo.completed,
            'created_at': todo.created_at,
            'updated_at': todo.updated_at
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
           
            todo.title = data.get('title', todo.title)
            todo.description = data.get('description', todo.description)
            todo.status = data.get('status', todo.status)
            todo.priority = data.get('priority', todo.priority)
            todo.completed = data.get('completed', todo.completed)
            
            # Handle due_date update
            due_date = data.get('due_date')
            if due_date:
                try:
                    todo.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse(
                        {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            todo.save()

            return JsonResponse({
                'id': todo.id,
                'folder_id': todo.folder.id,
                'title': todo.title,
                'description': todo.description,
                'status': todo.status,
                'priority': todo.priority,
                'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
                'completed': todo.completed,
                'updated_at': todo.updated_at
            }, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        # Check if folder is locked and password is correct
        if todo.folder.locked:
            try:
                data = json.loads(request.body)
                password = data.get('password')
                if not password or password != todo.folder.password:
                    return JsonResponse(
                        {'error': 'Incorrect password for this folder'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Password is required in request body for locked folder'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        todo.delete()
        return JsonResponse(
            {'message': 'Todo deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )

    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def todos_by_folder(request, folder_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Authorization Token required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = auth_header.split(' ')[1]
    
    try:
        user = CustomUser.objects.get(auth_token=token)
        folder = TodoFolder.objects.get(id=folder_id, user=user)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except TodoFolder.DoesNotExist:
        return JsonResponse({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # For GET requests, don't require password even for locked folders
        # Since we're just reading todos, not modifying them
        todos = Todo.objects.filter(user=user, folder=folder).order_by('-created_at')
        
        data = {
            'todos': [{
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'status': todo.status,
                'priority': todo.priority,
                'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
                'completed': todo.completed,
                'created_at': todo.created_at,
                'updated_at': todo.updated_at
            } for todo in todos]
        }

        return JsonResponse(data, safe=False, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # For POST requests (when creating/updating), still require password for locked folders
        if folder.locked:
            try:
                data = json.loads(request.body)
                password = data.get('password')
                if not password or password != folder.password:
                    return JsonResponse(
                        {'error': 'Incorrect password for this folder'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Password is required in request body for locked folder'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        todos = Todo.objects.filter(user=user, folder=folder).order_by('-created_at')
        
        data = {
            'todos': [{
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'status': todo.status,
                'priority': todo.priority,
                'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None,
                'completed': todo.completed,
                'created_at': todo.created_at,
                'updated_at': todo.updated_at
            } for todo in todos]
        }

        return JsonResponse(data, safe=False, status=status.HTTP_200_OK)

    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)