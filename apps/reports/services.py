"""Dashboard agregatsiyasi, Chart.js ma'lumotlari va XLSX/CSV eksport servislari."""
import csv
import io
from datetime import date, datetime, time, timedelta

import openpyxl
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from openpyxl.styles import Alignment, Font, PatternFill

from apps.analytics.models import AnalyticsEvent, PlatformStatSnapshot
from apps.branches.models import Branch, MapLink
from apps.content.models import AdmissionApplication
from apps.core.models import ContactMessage
from apps.reviews.models import WebsiteReview


def _parse_iso_date(val: str | None) -> date | None:
    if not val:
        return None
    try:
        return date.fromisoformat(val.strip())
    except ValueError:
        return None


def parse_filter_params(request) -> dict:
    """Sana oralig'i, davr (kun/hafta/oy), filial va platforma filtrlarini tahlil qiladi."""
    today = timezone.localdate()
    default_from = today - timedelta(days=29)

    date_from = _parse_iso_date(request.GET.get("date_from")) or default_from
    date_to = _parse_iso_date(request.GET.get("date_to")) or today
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    granularity = request.GET.get("granularity", "day")
    if granularity not in ("day", "week", "month"):
        granularity = "day"

    branch_id = request.GET.get("branch", "").strip()
    selected_branch = None
    if branch_id.isdigit():
        selected_branch = Branch.objects.filter(pk=int(branch_id)).first()

    platform = request.GET.get("platform", "all").strip()
    if platform not in ("all", "website", "google", "yandex"):
        platform = "all"

    page_path = request.GET.get("page_path", "").strip()[:255]

    return {
        "date_from": date_from,
        "date_to": date_to,
        "granularity": granularity,
        "selected_branch": selected_branch,
        "branch_id": str(selected_branch.pk) if selected_branch else "",
        "platform": platform,
        "page_path": page_path,
    }


def _make_aware_range(date_from: date, date_to: date):
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min), tz)
    end_dt = timezone.make_aware(datetime.combine(date_to, time.max), tz)
    return start_dt, end_dt


def filter_analytics_events(filters: dict):
    start_dt, end_dt = _make_aware_range(filters["date_from"], filters["date_to"])
    qs = AnalyticsEvent.objects.filter(created_at__range=(start_dt, end_dt))
    if filters["selected_branch"]:
        qs = qs.filter(branch=filters["selected_branch"])
    if filters["platform"] != "all":
        qs = qs.filter(platform=filters["platform"])
    if filters["page_path"]:
        qs = qs.filter(page_path__icontains=filters["page_path"])
    return qs


def filter_reviews(filters: dict):
    start_dt, end_dt = _make_aware_range(filters["date_from"], filters["date_to"])
    qs = WebsiteReview.objects.filter(created_at__range=(start_dt, end_dt))
    if filters["selected_branch"]:
        qs = qs.filter(branch=filters["selected_branch"])
    return qs


def build_dashboard_summary(filters: dict) -> dict:
    """Dashboard va statistika sahifalari uchun barcha agregat raqamlar va grafiklarni tayyorlaydi."""
    events_qs = filter_analytics_events(filters)

    page_views_qs = events_qs.filter(event_type="page_view")
    total_page_views = page_views_qs.count()
    total_visits = page_views_qs.values("anonymous_session_id").distinct().count()

    map_clicks_qs = events_qs.filter(event_type="map_click")
    google_clicks = map_clicks_qs.filter(platform="google").count()
    yandex_clicks = map_clicks_qs.filter(platform="yandex").count()
    cta_clicks = events_qs.filter(event_type="cta_click").count()

    # Vaqt bo'yicha grafik seriyalari
    granularity = filters["granularity"]
    if granularity == "month":
        trunc_fn = TruncMonth("created_at")
        fmt = "%Y-%m"
    elif granularity == "week":
        trunc_fn = TruncWeek("created_at")
        fmt = "%d.%m.%Y"
    else:
        trunc_fn = TruncDate("created_at")
        fmt = "%d.%m"

    grouped = (
        events_qs.annotate(bucket=trunc_fn)
        .values("bucket")
        .annotate(
            page_views=Count("id", filter=Q(event_type="page_view")),
            visits=Count("anonymous_session_id", distinct=True, filter=Q(event_type="page_view")),
            google_clicks=Count("id", filter=Q(event_type="map_click", platform="google")),
            yandex_clicks=Count("id", filter=Q(event_type="map_click", platform="yandex")),
        )
        .order_by("bucket")
    )

    chart_labels = []
    chart_page_views = []
    chart_visits = []
    chart_google_clicks = []
    chart_yandex_clicks = []

    for row in grouped:
        bucket = row["bucket"]
        chart_labels.append(bucket.strftime(fmt) if bucket else "")
        chart_page_views.append(row["page_views"])
        chart_visits.append(row["visits"])
        chart_google_clicks.append(row["google_clicks"])
        chart_yandex_clicks.append(row["yandex_clicks"])

    # Fikrlar statistikasi (umumiy va filtrlangan)
    all_reviews = WebsiteReview.objects.all()
    if filters["selected_branch"]:
        all_reviews = all_reviews.filter(branch=filters["selected_branch"])

    review_counts = all_reviews.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        approved=Count("id", filter=Q(status="approved")),
        rejected=Count("id", filter=Q(status="rejected")),
        avg_rating=Avg("rating", filter=Q(status="approved")),
    )
    filtered_review_count = filter_reviews(filters).count()

    # Qurilmalar, sahifalar va manbalar
    device_rows = list(
        page_views_qs.values("device_type").annotate(count=Count("id")).order_by("-count")
    )
    device_labels_map = dict(AnalyticsEvent.DEVICE_CHOICES)
    for r in device_rows:
        r["label"] = device_labels_map.get(r["device_type"], r["device_type"])

    top_pages = list(
        page_views_qs.values("page_path").annotate(count=Count("id")).order_by("-count")[:8]
    )
    top_referrers = list(
        page_views_qs.values("referrer_domain").annotate(count=Count("id")).order_by("-count")[:8]
    )

    map_link_stats = list(
        map_clicks_qs.values(
            "map_link__label",
            "platform",
            "map_link__link_type",
            "branch__name",
        )
        .annotate(clicks=Count("id"))
        .order_by("-clicks")
    )

    # Rasmiy platforma ko'rsatkichlari (alohida jadvaldan!)
    snapshots_qs = PlatformStatSnapshot.objects.select_related("branch", "imported_by")
    if filters["selected_branch"]:
        snapshots_qs = snapshots_qs.filter(branch=filters["selected_branch"])
    official_snapshots = list(snapshots_qs[:10])

    admissions_new = AdmissionApplication.objects.filter(status="new").count()
    contacts_new = ContactMessage.objects.filter(status="new").count()

    return {
        "total_visits": total_visits,
        "total_page_views": total_page_views,
        "google_clicks": google_clicks,
        "yandex_clicks": yandex_clicks,
        "total_map_clicks": google_clicks + yandex_clicks,
        "cta_clicks": cta_clicks,
        "review_counts": review_counts,
        "filtered_review_count": filtered_review_count,
        "device_rows": device_rows,
        "top_pages": top_pages,
        "top_referrers": top_referrers,
        "map_link_stats": map_link_stats,
        "official_snapshots": official_snapshots,
        "admissions_new": admissions_new,
        "contacts_new": contacts_new,
        "chart_data": {
            "labels": chart_labels,
            "page_views": chart_page_views,
            "visits": chart_visits,
            "google_clicks": chart_google_clicks,
            "yandex_clicks": chart_yandex_clicks,
        },
    }


def _csv_safe(value) -> str:
    """CSV formula injection (=, +, -, @) xavfidan himoya qiladi."""
    s = "" if value is None else str(value)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{s}"
    return s


def generate_csv_bytes(filters: dict) -> bytes:
    """Filtrlangan statistika va hodisalar bo'yicha UTF-8 BOM CSV fayl yaratadi."""
    summary = build_dashboard_summary(filters)
    events = filter_analytics_events(filters).select_related("branch", "map_link")[:5000]

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Turon Odob-Ilm — Sayt va Xarita Tugmalari Hisoboti"])
    writer.writerow(["Davr", f"{filters['date_from']} — {filters['date_to']}"])
    writer.writerow(["Eslatma", "Xarita tugma bosishlari faqat sayt ichidagi kliklar bo'lib, rasmiy Google/Yandex qidiruv ko'rsatkichlari emas."])
    writer.writerow([])
    writer.writerow(["Ko'rsatkich", "Qiymat"])
    writer.writerow(["Unikal tashriflar (anonim sessiyalar)", summary["total_visits"]])
    writer.writerow(["Sahifalar ko'rishlari", summary["total_page_views"]])
    writer.writerow(["Google tugmasi bosishlari (saytdan)", summary["google_clicks"]])
    writer.writerow(["Yandex tugmasi bosishlari (saytdan)", summary["yandex_clicks"]])
    writer.writerow(["CTA tugma bosishlari", summary["cta_clicks"]])
    writer.writerow(["Tasdiqlangan sayt fikrlari (jami)", summary["review_counts"]["approved"]])
    writer.writerow(["Moderatsiyadagi fikrlar", summary["review_counts"]["pending"]])
    writer.writerow([])
    writer.writerow(["Sana/Vaqt", "Hodisa", "Platforma", "Filial", "Tugma/Sahifa", "Qurilma", "Manba"])

    for ev in events:
        writer.writerow([
            timezone.localtime(ev.created_at).strftime("%Y-%m-%d %H:%M"),
            _csv_safe(ev.get_event_type_display()),
            _csv_safe(ev.get_platform_display()),
            _csv_safe(ev.branch.name if ev.branch else "Umumiy"),
            _csv_safe(ev.map_link.label if ev.map_link else (ev.cta_label or ev.page_path)),
            _csv_safe(ev.get_device_type_display()),
            _csv_safe(ev.referrer_domain),
        ])

    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def generate_xlsx_bytes(filters: dict) -> bytes:
    """Ko'p varaqli professional XLSX hisobot yaratadi."""
    summary = build_dashboard_summary(filters)
    events = filter_analytics_events(filters).select_related("branch", "map_link")[:5000]
    reviews = filter_reviews(filters).select_related("branch")
    snapshots = PlatformStatSnapshot.objects.select_related("branch")
    if filters["selected_branch"]:
        snapshots = snapshots.filter(branch=filters["selected_branch"])

    wb = openpyxl.Workbook()
    header_fill = PatternFill("solid", fgColor="0B1F3A")
    header_font = Font(color="FFFFFF", bold=True)
    title_font = Font(color="0B1F3A", bold=True, size=13)

    # 1-varaq: Umumiy ko'rsatkichlar
    ws1 = wb.active
    ws1.title = "Umumiy ko'rsatkichlar"
    ws1["A1"] = "Turon Odob-Ilm — Raqamli Platforma Hisoboti"
    ws1["A1"].font = title_font
    ws1["A2"] = f"Davr: {filters['date_from']} — {filters['date_to']}"
    ws1["A3"] = "Izoh: Sayt tugma bosishlari rasmiy Google/Yandex kabinet ko'rsatkichlaridan alohida yuritiladi."

    ws1.append([])
    ws1.append(["Ko'rsatkich", "Qiymat"])
    for cell in ws1[5]:
        cell.fill = header_fill
        cell.font = header_font

    kpi_rows = [
        ("Unikal tashriflar (anonim sessiyalar)", summary["total_visits"]),
        ("Sahifalar ko'rishlari", summary["total_page_views"]),
        ("Google xarita tugmasi bosishlari (saytdan)", summary["google_clicks"]),
        ("Yandex xarita tugmasi bosishlari (saytdan)", summary["yandex_clicks"]),
        ("CTA tugma bosishlari", summary["cta_clicks"]),
        ("Jami sayt fikrlari", summary["review_counts"]["total"]),
        ("Tasdiqlangan sayt fikrlari", summary["review_counts"]["approved"]),
        ("Moderatsiyada turgan fikrlar", summary["review_counts"]["pending"]),
        (
            "Sayt fikrlari o'rtacha bahosi",
            round(float(summary["review_counts"]["avg_rating"]), 2)
            if summary["review_counts"]["avg_rating"]
            else "Mavjud emas",
        ),
    ]
    for k, v in kpi_rows:
        ws1.append([k, v])

    ws1.column_dimensions["A"].width = 48
    ws1.column_dimensions["B"].width = 24

    # 2-varaq: Xarita tugma bosishlari
    ws2 = wb.create_sheet("Xarita tugmalari")
    ws2.append(["Filial", "Platforma", "Havola turi", "Tugma nomi", "Bosishlar soni"])
    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
    link_type_map = dict(MapLink.LINK_TYPE_CHOICES)
    platform_map = dict(MapLink.PLATFORM_CHOICES)
    for row in summary["map_link_stats"]:
        ws2.append([
            _csv_safe(row["branch__name"] or "Umumiy"),
            _csv_safe(platform_map.get(row["platform"], row["platform"])),
            _csv_safe(link_type_map.get(row["map_link__link_type"], row["map_link__link_type"])),
            _csv_safe(row["map_link__label"] or "-"),
            row["clicks"],
        ])
    for col in ("A", "B", "C", "D", "E"):
        ws2.column_dimensions[col].width = 26

    # 3-varaq: Ota-onalar fikrlari (sayt ichidagi)
    ws3 = wb.create_sheet("Sayt fikrlari")
    ws3.append(["Sana", "Filial", "Ko'rinadigan ism", "Baho", "Holat", "Fikr matni", "Demo"])
    for cell in ws3[1]:
        cell.fill = header_fill
        cell.font = header_font
    for rev in reviews:
        ws3.append([
            timezone.localtime(rev.created_at).strftime("%Y-%m-%d %H:%M"),
            _csv_safe(rev.branch.name),
            _csv_safe(rev.public_author_label),
            rev.rating,
            _csv_safe(rev.get_status_display()),
            _csv_safe(rev.comment),
            "Ha" if rev.is_demo else "Yo'q",
        ])
    ws3.column_dimensions["A"].width = 18
    ws3.column_dimensions["B"].width = 22
    ws3.column_dimensions["C"].width = 22
    ws3.column_dimensions["D"].width = 10
    ws3.column_dimensions["E"].width = 18
    ws3.column_dimensions["F"].width = 55

    # 4-varaq: Rasmiy platforma ko'rsatkichlari
    ws4 = wb.create_sheet("Rasmiy platforma statistikasi")
    ws4.append([
        "Filial",
        "Platforma",
        "Manba usuli",
        "Manba nomi",
        "Davr boshlanishi",
        "Davr tugashi",
        "Ko'rinishlar",
        "Profil ko'rishlari",
        "Yo'nalishlar",
        "Qo'ng'iroqlar",
        "Saytga o'tishlar",
        "O'rtacha baho",
        "Sharhlar soni",
        "Yangilangan vaqt",
    ])
    for cell in ws4[1]:
        cell.fill = header_fill
        cell.font = header_font
    for snap in snapshots:
        ws4.append([
            _csv_safe(snap.branch.name),
            _csv_safe(snap.get_platform_display()),
            _csv_safe(snap.get_source_type_display()),
            _csv_safe(snap.source_label),
            snap.period_start.isoformat(),
            snap.period_end.isoformat(),
            snap.impressions,
            snap.profile_views,
            snap.direction_clicks,
            snap.call_clicks,
            snap.website_clicks,
            float(snap.average_rating) if snap.average_rating is not None else "",
            snap.review_count,
            timezone.localtime(snap.synced_at).strftime("%Y-%m-%d %H:%M"),
        ])

    # 5-varaq: Hodisalar jurnali
    ws5 = wb.create_sheet("Sayt hodisalari")
    ws5.append(["Sana/Vaqt", "Hodisa", "Platforma", "Filial", "Sahifa/Tugma", "Qurilma", "Trafik manbasi"])
    for cell in ws5[1]:
        cell.fill = header_fill
        cell.font = header_font
    for ev in events:
        ws5.append([
            timezone.localtime(ev.created_at).strftime("%Y-%m-%d %H:%M"),
            _csv_safe(ev.get_event_type_display()),
            _csv_safe(ev.get_platform_display()),
            _csv_safe(ev.branch.name if ev.branch else "Umumiy"),
            _csv_safe(ev.map_link.label if ev.map_link else (ev.cta_label or ev.page_path)),
            _csv_safe(ev.get_device_type_display()),
            _csv_safe(ev.referrer_domain),
        ])
    for col in ("A", "B", "C", "D", "E", "F", "G"):
        ws5.column_dimensions[col].width = 22
    ws5["A1"].alignment = Alignment(horizontal="left")

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
