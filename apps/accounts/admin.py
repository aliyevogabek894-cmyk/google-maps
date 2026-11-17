from django.contrib import admin

from .models import AdminAuditLog, StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "two_factor_enabled", "updated_at")
    list_filter = ("two_factor_enabled",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone")


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor_username", "action", "target_model", "summary")
    list_filter = ("action", "target_model", "created_at")
    search_fields = ("actor_username", "summary", "target_id")
    readonly_fields = (
        "actor",
        "actor_username",
        "action",
        "target_model",
        "target_id",
        "summary",
        "details",
        "ip_hash",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
