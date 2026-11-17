from django.contrib import admin

from .models import ContactMessage, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("school_name", "primary_phone", "privacy_policy_version", "is_demo_mode", "updated_at")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "branch", "subject", "status", "created_at")
    list_filter = ("status", "branch", "created_at")
    search_fields = ("full_name", "phone", "subject", "message")
    readonly_fields = ("ip_hash", "created_at", "accepted_privacy_policy")
