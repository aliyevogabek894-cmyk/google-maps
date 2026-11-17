from django.contrib import admin

from .models import (
    AdmissionApplication,
    AdmissionStep,
    EducationProgram,
    GalleryItem,
    NewsPost,
    OfficialDocument,
    SchoolService,
    Teacher,
)


@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "grade_range", "sort_order", "is_active", "is_demo")
    list_filter = ("is_active", "is_demo")


@admin.register(SchoolService)
class SchoolServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "schedule_info", "sort_order", "is_active", "is_demo")
    list_filter = ("category", "is_active", "is_demo")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject_or_role", "branch", "experience_years", "is_active", "is_demo")
    list_filter = ("branch", "is_active", "is_demo")
    search_fields = ("full_name", "subject_or_role")


@admin.register(OfficialDocument)
class OfficialDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_number", "is_active", "is_demo")


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "branch", "published_at", "is_published", "is_demo")
    list_filter = ("category", "is_published", "branch", "is_demo")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "branch", "is_published", "sort_order", "is_demo")
    list_filter = ("media_type", "is_published", "branch", "is_demo")


@admin.register(AdmissionStep)
class AdmissionStepAdmin(admin.ModelAdmin):
    list_display = ("title", "step_type", "sort_order", "is_active")
    list_filter = ("step_type", "is_active")


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ("student_name", "parent_name", "phone", "grade_level", "branch", "status", "created_at")
    list_filter = ("status", "branch", "grade_level", "created_at")
    search_fields = ("student_name", "parent_name", "phone")
    readonly_fields = ("ip_hash", "accepted_privacy_policy", "created_at")
