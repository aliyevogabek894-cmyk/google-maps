from django.contrib import admin

from .models import Branch, MapLink


class MapLinkInline(admin.TabularInline):
    model = MapLink
    extra = 0
    fields = ("platform", "link_type", "label", "target_url", "is_verified_profile", "is_active", "sort_order")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city_or_district",
        "phone",
        "google_verification_status",
        "yandex_verification_status",
        "is_primary",
        "is_active",
        "is_demo",
    )
    list_filter = ("is_active", "is_primary", "google_verification_status", "yandex_verification_status", "is_demo")
    search_fields = ("name", "address", "phone")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MapLinkInline]


@admin.register(MapLink)
class MapLinkAdmin(admin.ModelAdmin):
    list_display = ("branch", "platform", "link_type", "label", "is_verified_profile", "is_active", "sort_order")
    list_filter = ("platform", "link_type", "is_verified_profile", "is_active", "branch")
    search_fields = ("branch__name", "label", "target_url")
