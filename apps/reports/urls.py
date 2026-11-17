from django.urls import path

from .views import (
    analytics_detail_view,
    audit_logs_view,
    branches_manage_view,
    content_manage_view,
    dashboard_view,
    export_csv_view,
    export_xlsx_view,
    platform_metrics_view,
    printable_report_view,
    reviews_moderation_view,
)

app_name = "reports"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("statistika/", analytics_detail_view, name="analytics"),
    path("platforma-statistikasi/", platform_metrics_view, name="platform_metrics"),
    path("fikrlar/", reviews_moderation_view, name="moderation"),
    path("filiallar/", branches_manage_view, name="branches"),
    path("kontent/", content_manage_view, name="content"),
    path("eksport/xlsx/", export_xlsx_view, name="export_xlsx"),
    path("eksport/csv/", export_csv_view, name="export_csv"),
    path("hisobot/chop-etish/", printable_report_view, name="printable_report"),
    path("audit/", audit_logs_view, name="audit"),
]
