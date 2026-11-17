"""Ta'lim, yangiliklar, galereya va qabul ommaviy sahifalari."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.analytics.services import record_analytics_event
from apps.core.models import SiteSettings
from apps.core.security import check_rate_limit, get_client_ip_hash
from .forms import AdmissionApplicationForm
from .models import (
    AdmissionStep,
    EducationProgram,
    GalleryItem,
    NewsPost,
    SchoolService,
)


def education_view(request):
    """Ta'lim va xizmatlar sahifasi."""
    programs = EducationProgram.objects.filter(is_active=True)
    services = SchoolService.objects.filter(is_active=True)
    grouped_services = {
        "club": services.filter(category="club"),
        "schedule": services.filter(category="schedule"),
        "nutrition": services.filter(category="nutrition"),
        "transport": services.filter(category="transport"),
        "other": services.filter(category="other"),
    }
    return render(
        request,
        "content/education.html",
        {"programs": programs, "grouped_services": grouped_services},
    )


def news_list_view(request):
    """Yangiliklar va tadbirlar ro'yxati."""
    category = request.GET.get("turkum", "").strip()
    qs = NewsPost.objects.filter(is_published=True).select_related("branch")
    valid_categories = {c[0] for c in NewsPost.CATEGORY_CHOICES}
    if category in valid_categories:
        qs = qs.filter(category=category)
    else:
        category = ""

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get("sahifa"))
    return render(
        request,
        "content/news_list.html",
        {
            "page_obj": page_obj,
            "active_category": category,
            "categories": NewsPost.CATEGORY_CHOICES,
        },
    )


def news_detail_view(request, slug):
    """Yangilik tafsilotlari sahifasi."""
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    recent_posts = NewsPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(
        request,
        "content/news_detail.html",
        {"post": post, "recent_posts": recent_posts},
    )


def gallery_view(request):
    """Foto va video galereya (tur va bo'lim filtrlari bilan)."""
    media_type = request.GET.get("turi", "").strip()
    category = request.GET.get("bolim", "").strip()
    qs = GalleryItem.objects.filter(is_published=True).select_related("branch")
    if media_type in ("photo", "video"):
        qs = qs.filter(media_type=media_type)
    else:
        media_type = ""

    valid_cats = {c[0] for c in GalleryItem.CATEGORY_CHOICES}
    if category in valid_cats:
        qs = qs.filter(category=category)
    else:
        category = ""

    return render(
        request,
        "content/gallery.html",
        {
            "items": qs,
            "active_type": media_type,
            "active_category": category,
            "categories": GalleryItem.CATEGORY_CHOICES,
        },
    )


def admission_view(request):
    """Qabul shartlari, kerakli hujjatlar va onlayn ariza formasi."""
    site_settings = SiteSettings.get_solo()
    steps = AdmissionStep.objects.filter(is_active=True)
    form = AdmissionApplicationForm(request.POST or None)

    if request.method == "POST":
        ip_hash = get_client_ip_hash(request)
        allowed, retry_after = check_rate_limit(
            scope="admission_submit",
            identifier=ip_hash,
            limit=5,
            window_seconds=900,
        )
        if not allowed:
            messages.error(
                request,
                f"Juda ko‘p ariza yuborildi. Iltimos, {max(1, retry_after // 60)} daqiqadan keyin urinib ko‘ring.",
            )
            return render(
                request,
                "content/admission.html",
                {
                    "site_settings": site_settings,
                    "conditions": steps.filter(step_type="condition"),
                    "documents": steps.filter(step_type="document"),
                    "process_steps": steps.filter(step_type="step"),
                    "form": form,
                },
                status=429,
            )

        if form.is_valid():
            application = form.save(commit=False)
            application.ip_hash = ip_hash
            application.save()
            record_analytics_event(
                request,
                event_type="admission_submit",
                branch=application.branch,
                platform="website",
                page_path=request.path,
            )
            messages.success(
                request,
                "Qabul arizangiz muvaffaqiyatli yuborildi! Qabul komissiyasi tez orada siz bilan bog‘lanadi.",
            )
            return redirect("content:admission")

    return render(
        request,
        "content/admission.html",
        {
            "site_settings": site_settings,
            "conditions": steps.filter(step_type="condition"),
            "documents": steps.filter(step_type="document"),
            "process_steps": steps.filter(step_type="step"),
            "form": form,
        },
    )
