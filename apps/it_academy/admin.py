from django.contrib import admin

from .models import ITCourse, ITProject


@admin.register(ITCourse)
class ITCourseAdmin(admin.ModelAdmin):
    list_display = ("title", "grade_level", "sort_order", "is_active", "is_demo")
    list_filter = ("is_active", "is_demo")


@admin.register(ITProject)
class ITProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "branch", "has_parent_consent", "permission_status", "is_published", "is_demo")
    list_filter = ("permission_status", "has_parent_consent", "is_published", "is_demo")
