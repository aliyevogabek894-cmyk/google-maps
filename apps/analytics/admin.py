from django.contrib import admin

from .models import AnalyticsEvent, PlatformStatSnapshot


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "platform", "branch", "page_path", "device_type", "referrer_domain")
    list_filter = ("event_type", "platform", "device_type", "branch", "created_at")
    search_fields = ("page_path", "cta_label", "referrer_domain")
    readonly_fields = (
        "event_type",
        "branch",
        "map_link",
        "platform",
        "cta_label",
        "page_path",
        "referrer_domain",
        "utm_source",
        "utm_campaign",
        "device_type",
        "anonymous_session_id",
        "created_at",
    )


@admin.register(PlatformStatSnapshot)
class PlatformStatSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "branch",
        "platform",
        "source_type",
        "period_start",
        "period_end",
        "impressions",
        "direction_clicks",
        "synced_at",
    )
    list_filter = ("platform", "source_type", "branch")
