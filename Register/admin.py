from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Todo, TodoFolder

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'phone', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Todo)
admin.site.register(TodoFolder)