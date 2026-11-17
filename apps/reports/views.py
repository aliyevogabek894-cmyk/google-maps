"""Boshqaruv paneli (Admin Monitoring Portal) ko'rinishlari."""
import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.models import ALL_STAFF_ROLES, ROLE_EDITOR, ROLE_MODERATOR, ROLE_SUPERADMIN, AdminAuditLog
from apps.accounts.permissions import has_any_role, role_required
from apps.accounts.services import log_admin_action
from apps.analytics.adapters import GoogleBusinessAdapter, YandexBusinessAdapter
from apps.analytics.models import PlatformStatSnapshot
from apps.branches.models import Branch, MapLink
from apps.content.models import AdmissionApplication
from apps.core.models import ContactMessage, SiteSettings
from apps.reviews.models import WebsiteReview
from .forms import (
    BranchManageForm,
    MapLinkManageForm,
    PlatformStatCSVUploadForm,
    PlatformStatManualForm,
    SiteQuickSettingsForm,
)
from .services import (
    build_dashboard_summary,
    generate_csv_bytes,
    generate_xlsx_bytes,
    parse_filter_params,
)


@role_required(*ALL_STAFF_ROLES)
def dashboard_view(request):
    """Asosiy monitoring dashboard: tashriflar, xarita tugmalari, fikrlar va grafiklar."""
    filters = parse_filter_params(request)
    summary = build_dashboard_summary(filters)
    branches = Branch.objects.all().order_by("-is_primary", "name")
    recent_audit = AdminAuditLog.objects.all()[:6]
    google_adapter = GoogleBusinessAdapter().get_status()
    yandex_adapter = YandexBusinessAdapter().get_status()

    security_status = {
        "https_redirect": getattr(settings, "SECURE_SSL_REDIRECT", False),
        "debug": settings.DEBUG,
        "two_factor_enforced": getattr(settings, "ENABLE_2FA_ENFORCEMENT", False),
        "user_2fa": getattr(getattr(request.user, "staff_profile", None), "two_factor_enabled", False),
    }

    return render(
        request,
        "reports/dashboard.html",
        {
            "filters": filters,
            "summary": summary,
            "branches": branches,
            "recent_audit": recent_audit,
            "google_adapter": google_adapter,
            "yandex_adapter": yandex_adapter,
            "security_status": security_status,
        },
    )


@role_required(*ALL_STAFF_ROLES)
def analytics_detail_view(request):
    """Batafsil sayt trafiki, qurilmalar, sahifalar va xarita tugma bosishlari."""
    filters = parse_filter_params(request)
    summary = build_dashboard_summary(filters)
    branches = Branch.objects.all().order_by("-is_primary", "name")
    return render(
        request,
        "reports/analytics.html",
        {
            "filters": filters,
            "summary": summary,
            "branches": branches,
        },
    )


@role_required(*ALL_STAFF_ROLES)
def platform_metrics_view(request):
    """
    Rasmiy Google Business Profile va Yandex Business ko'rsatkichlari.
    API ulanmagan bo'lsa, adapter holatini ko'rsatadi va Superadmin uchun qo'lda import beradi.
    """
    google_status = GoogleBusinessAdapter().get_status()
    yandex_status = YandexBusinessAdapter().get_status()
    snapshots = PlatformStatSnapshot.objects.select_related("branch", "imported_by")[:30]
    manual_form = PlatformStatManualForm()
    csv_form = PlatformStatCSVUploadForm()

    if request.method == "POST":
        if not has_any_role(request.user, (ROLE_SUPERADMIN,)):
            messages.error(request, "Rasmiy platforma ko‘rsatkichlarini import qilish uchun Superadmin huquqi kerak.")
            return redirect("reports:platform_metrics")

        action_type = request.POST.get("import_mode", "manual")
        if action_type == "manual":
            manual_form = PlatformStatManualForm(request.POST)
            if manual_form.is_valid():
                snap = manual_form.save(commit=False)
                snap.source_type = "manual_form"
                snap.imported_by = request.user
                snap.synced_at = timezone.now()
                snap.save()
                log_admin_action(
                    request,
                    action="platform_stat_imported",
                    target_model="PlatformStatSnapshot",
                    target_id=snap.pk,
                    summary=f"{snap.branch.name} uchun {snap.get_platform_display()} statistikasi qo'lda kiritildi",
                )
                messages.success(request, "Rasmiy platforma ko‘rsatkichlari saqlandi.")
                return redirect("reports:platform_metrics")

        elif action_type == "csv":
            csv_form = PlatformStatCSVUploadForm(request.POST, request.FILES)
            if csv_form.is_valid():
                uploaded = csv_form.cleaned_data["csv_file"]
                if uploaded.size > 2 * 1024 * 1024:
                    messages.error(request, "CSV fayl hajmi 2 MB dan oshmasligi kerak.")
                else:
                    try:
                        decoded = uploaded.read().decode("utf-8-sig")
                        reader = csv.DictReader(io.StringIO(decoded))
                        created_count = 0
                        for row in reader:
                            p_start = date.fromisoformat((row.get("period_start") or "").strip())
                            p_end = date.fromisoformat((row.get("period_end") or "").strip())
                            avg_raw = (row.get("average_rating") or "").strip()
                            avg_val = None
                            if avg_raw:
                                try:
                                    avg_val = Decimal(avg_raw)
                                except InvalidOperation:
                                    avg_val = None
                            PlatformStatSnapshot.objects.create(
                                branch=csv_form.cleaned_data["branch"],
                                platform=csv_form.cleaned_data["platform"],
                                source_type="manual_csv",
                                source_label=csv_form.cleaned_data["source_label"],
                                period_start=p_start,
                                period_end=p_end,
                                impressions=int(row.get("impressions") or 0),
                                profile_views=int(row.get("profile_views") or 0),
                                direction_clicks=int(row.get("direction_clicks") or 0),
                                call_clicks=int(row.get("call_clicks") or 0),
                                website_clicks=int(row.get("website_clicks") or 0),
                                average_rating=avg_val,
                                review_count=int(row.get("review_count") or 0),
                                imported_by=request.user,
                                notes=(row.get("notes") or "")[:300],
                            )
                            created_count += 1
                        log_admin_action(
                            request,
                            action="platform_stat_imported",
                            target_model="PlatformStatSnapshot",
                            summary=f"CSV orqali {created_count} ta rasmiy ko'rsatkich import qilindi",
                        )
                        messages.success(request, f"{created_count} ta rasmiy ko‘rsatkich qatori import qilindi.")
                        return redirect("reports:platform_metrics")
                    except Exception as exc:
                        messages.error(request, f"CSV faylni o‘qishda xatolik: {exc}")

    return render(
        request,
        "reports/platform_metrics.html",
        {
            "google_status": google_status,
            "yandex_status": yandex_status,
            "snapshots": snapshots,
            "manual_form": manual_form,
            "csv_form": csv_form,
        },
    )


@role_required(ROLE_SUPERADMIN, ROLE_MODERATOR)
def reviews_moderation_view(request):
    """Sayt ichidagi ota-onalar fikrlarini moderatsiya qilish navbati."""
    status_filter = request.GET.get("holat", "pending")
    if status_filter not in ("pending", "approved", "rejected", "all"):
        status_filter = "pending"

    if request.method == "POST":
        review_id = request.POST.get("review_id")
        decision = request.POST.get("decision")
        admin_reply = (request.POST.get("admin_reply") or "").strip()
        moderation_note = (request.POST.get("moderation_note") or "").strip()

        review = get_object_or_404(WebsiteReview, pk=review_id)
        if decision in ("approved", "rejected", "pending"):
            review.status = decision
            review.admin_reply = admin_reply
            review.moderation_note = moderation_note
            review.moderated_by = request.user
            review.moderated_at = timezone.now()
            review.save()

            action_code = "review_approved" if decision == "approved" else "review_rejected"
            if decision == "pending" and admin_reply:
                action_code = "review_replied"
            log_admin_action(
                request,
                action=action_code,
                target_model="WebsiteReview",
                target_id=review.pk,
                summary=f"Fikr #{review.pk} ({review.public_author_label}) holati: {review.get_status_display()}",
            )
            messages.success(request, f"Fikr #{review.pk} holati yangilandi.")
        return redirect(f"{request.path}?holat={status_filter}")

    qs = WebsiteReview.objects.select_related("branch", "consent", "moderated_by")
    if status_filter != "all":
        qs = qs.filter(status=status_filter)

    counts = {
        "pending": WebsiteReview.objects.filter(status="pending").count(),
        "approved": WebsiteReview.objects.filter(status="approved").count(),
        "rejected": WebsiteReview.objects.filter(status="rejected").count(),
        "all": WebsiteReview.objects.count(),
    }

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("sahifa"))
    return render(
        request,
        "reports/moderation.html",
        {
            "page_obj": page_obj,
            "status_filter": status_filter,
            "counts": counts,
        },
    )


@role_required(ROLE_SUPERADMIN)
def branches_manage_view(request):
    """Filiallar va Google/Yandex xarita havolalarini boshqarish."""
    branches = Branch.objects.prefetch_related("map_links").order_by("-is_primary", "name")
    edit_branch_id = request.GET.get("branch_id")
    branch_instance = Branch.objects.filter(pk=edit_branch_id).first() if edit_branch_id else None
    branch_form = BranchManageForm(instance=branch_instance)
    map_form = MapLinkManageForm()

    if request.method == "POST":
        form_kind = request.POST.get("form_kind")
        if form_kind == "branch":
            target_id = request.POST.get("branch_pk")
            instance = Branch.objects.filter(pk=target_id).first() if target_id else None
            branch_form = BranchManageForm(request.POST, instance=instance)
            if branch_form.is_valid():
                saved = branch_form.save()
                log_admin_action(
                    request,
                    action="branch_updated" if instance else "branch_created",
                    target_model="Branch",
                    target_id=saved.pk,
                    summary=f"Filial saqlandi: {saved.name}",
                )
                messages.success(request, f"'{saved.name}' filiali ma'lumotlari saqlandi.")
                return redirect("reports:branches")
        elif form_kind == "map_link":
            link_pk = request.POST.get("link_pk")
            link_inst = MapLink.objects.filter(pk=link_pk).first() if link_pk else None
            map_form = MapLinkManageForm(request.POST, instance=link_inst)
            if map_form.is_valid():
                saved_link = map_form.save()
                log_admin_action(
                    request,
                    action="map_link_updated",
                    target_model="MapLink",
                    target_id=saved_link.pk,
                    summary=f"Xarita havolasi saqlandi: {saved_link}",
                )
                messages.success(request, "Xarita havolasi xavfsiz tekshiruvdan o‘tdi va saqlandi.")
                return redirect("reports:branches")

    return render(
        request,
        "reports/branches.html",
        {
            "branches": branches,
            "branch_form": branch_form,
            "branch_instance": branch_instance,
            "map_form": map_form,
        },
    )


@role_required(ROLE_SUPERADMIN, ROLE_EDITOR)
def content_manage_view(request):
    """Qabul arizalari, aloqa murojaatlari va tezkor sayt sozlamalari."""
    site_settings = SiteSettings.get_solo()
    settings_form = SiteQuickSettingsForm(instance=site_settings)

    if request.method == "POST":
        kind = request.POST.get("kind")
        if kind == "site_settings" and has_any_role(request.user, (ROLE_SUPERADMIN,)):
            settings_form = SiteQuickSettingsForm(request.POST, instance=site_settings)
            if settings_form.is_valid():
                settings_form.save()
                log_admin_action(
                    request,
                    action="settings_updated",
                    target_model="SiteSettings",
                    target_id=site_settings.pk,
                    summary="Asosiy sayt sozlamalari yangilandi",
                )
                messages.success(request, "Sayt sozlamalari saqlandi.")
                return redirect("reports:content")
        elif kind == "admission_status":
            app_obj = get_object_or_404(AdmissionApplication, pk=request.POST.get("app_id"))
            new_status = request.POST.get("status")
            if new_status in dict(AdmissionApplication.STATUS_CHOICES):
                app_obj.status = new_status
                app_obj.admin_note = (request.POST.get("admin_note") or "").strip()
                app_obj.save()
                log_admin_action(
                    request,
                    action="admission_updated",
                    target_model="AdmissionApplication",
                    target_id=app_obj.pk,
                    summary=f"Qabul arizasi #{app_obj.pk} holati: {app_obj.get_status_display()}",
                )
                messages.success(request, "Qabul arizasi holati yangilandi.")
                return redirect("reports:content")
        elif kind == "contact_status":
            msg_obj = get_object_or_404(ContactMessage, pk=request.POST.get("msg_id"))
            new_status = request.POST.get("status")
            if new_status in dict(ContactMessage.STATUS_CHOICES):
                msg_obj.status = new_status
                msg_obj.admin_note = (request.POST.get("admin_note") or "").strip()
                msg_obj.save()
                log_admin_action(
                    request,
                    action="contact_updated",
                    target_model="ContactMessage",
                    target_id=msg_obj.pk,
                    summary=f"Murojaat #{msg_obj.pk} holati: {msg_obj.get_status_display()}",
                )
                messages.success(request, "Murojaat holati yangilandi.")
                return redirect("reports:content")

    admissions = AdmissionApplication.objects.select_related("branch")[:25]
    contacts = ContactMessage.objects.select_related("branch")[:25]

    return render(
        request,
        "reports/content_manage.html",
        {
            "settings_form": settings_form,
            "admissions": admissions,
            "contacts": contacts,
            "admission_statuses": AdmissionApplication.STATUS_CHOICES,
            "contact_statuses": ContactMessage.STATUS_CHOICES,
        },
    )


@role_required(*ALL_STAFF_ROLES)
def export_xlsx_view(request):
    """Filtrlangan XLSX hisobot yuklab olish."""
    filters = parse_filter_params(request)
    content = generate_xlsx_bytes(filters)
    log_admin_action(
        request,
        action="report_exported",
        target_model="XLSX",
        summary=f"XLSX hisobot yuklab olindi ({filters['date_from']}..{filters['date_to']})",
    )
    filename = f"turon_hisobot_{filters['date_from']}_{filters['date_to']}.xlsx"
    response = HttpResponse(
        content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@role_required(*ALL_STAFF_ROLES)
def export_csv_view(request):
    """Filtrlangan CSV hisobot yuklab olish."""
    filters = parse_filter_params(request)
    content = generate_csv_bytes(filters)
    log_admin_action(
        request,
        action="report_exported",
        target_model="CSV",
        summary=f"CSV hisobot yuklab olindi ({filters['date_from']}..{filters['date_to']})",
    )
    filename = f"turon_hisobot_{filters['date_from']}_{filters['date_to']}.csv"
    response = HttpResponse(content, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@role_required(*ALL_STAFF_ROLES)
def printable_report_view(request):
    """Chop etish (PDF saqlash) uchun optimallashtirilgan hisobot sahifasi."""
    filters = parse_filter_params(request)
    summary = build_dashboard_summary(filters)
    return render(
        request,
        "reports/printable_report.html",
        {
            "filters": filters,
            "summary": summary,
            "generated_at": timezone.now(),
        },
    )


@role_required(ROLE_SUPERADMIN)
def audit_logs_view(request):
    """Administrator va moderator amallari jurnali."""
    action_filter = request.GET.get("amal", "").strip()
    qs = AdminAuditLog.objects.select_related("actor")
    if action_filter:
        qs = qs.filter(action=action_filter)
    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("sahifa"))
    return render(
        request,
        "reports/audit_logs.html",
        {
            "page_obj": page_obj,
            "action_filter": action_filter,
            "action_choices": AdminAuditLog.ACTION_CHOICES,
        },
    )
