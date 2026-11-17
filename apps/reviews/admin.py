from django.contrib import admin

from .models import ReviewConsent, WebsiteReview


class ReviewConsentInline(admin.StackedInline):
    model = ReviewConsent
    extra = 0
    readonly_fields = ("accepted_privacy_policy", "policy_version", "consent_text_snapshot", "ip_hash", "created_at")
    can_delete = False


@admin.register(WebsiteReview)
class WebsiteReviewAdmin(admin.ModelAdmin):
    list_display = ("public_author_label", "branch", "rating", "status", "is_demo", "created_at")
    list_filter = ("status", "rating", "branch", "is_demo", "created_at")
    search_fields = ("author_name", "display_name", "comment")
    readonly_fields = ("created_at",)
    inlines = [ReviewConsentInline]
