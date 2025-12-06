from django.contrib import admin
from .models import ContactMessage
import csv
from django.http import HttpResponse


@admin.action(description="Export selected to CSV")
def export_selected(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=selected_messages.csv"
    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Email", "Phone", "Message", "Created At"])
    for m in queryset:
        writer.writerow([m.id, m.name, m.email, m.phone_number, m.message, m.created_at])
    return response


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "created_at")
    search_fields = ("name", "email", "phone_number", "message")
    list_filter = ("created_at",)
    actions = [export_selected]



# perisaketh545@gmail.com
# password