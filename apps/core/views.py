"""Asosiy ommaviy sahifalar va SEO ko'rinishlari."""
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.analytics.services import record_analytics_event
from apps.branches.models import Branch
from apps.content.models import EducationProgram, NewsPost, OfficialDocument, SchoolService, Teacher
from apps.reviews.models import WebsiteReview
from .forms import ContactMessageForm
from .models import SiteSettings
from .security import check_rate_limit, get_client_ip_hash


def home_view(request):
    """Bosh sahifa: banner, afzalliklar, Furqat filiali xarita kartasi, fikrlar va yangiliklar."""
    site_settings = SiteSettings.get_solo()
    primary_branch = (
        Branch.objects.filter(is_active=True)
        .prefetch_related("map_links")
        .order_by("-is_primary", "name")
        .first()
    )
    programs = EducationProgram.objects.filter(is_active=True)[:4]
    services = SchoolService.objects.filter(is_active=True)[:4]
    latest_news = NewsPost.objects.filter(is_published=True)[:3]
    approved_reviews = WebsiteReview.objects.filter(status="approved").select_related("branch")[:3]
    review_stats = WebsiteReview.objects.filter(status="approved").aggregate(
        total=Count("id"), avg=Avg("rating")
    )

    map_links = []
    if primary_branch:
        map_links = list(primary_branch.map_links.filter(is_active=True).order_by("sort_order", "id"))

    return render(
        request,
        "core/home.html",
        {
            "site_settings": site_settings,
            "primary_branch": primary_branch,
            "map_links": map_links,
            "programs": programs,
            "services": services,
            "latest_news": latest_news,
            "approved_reviews": approved_reviews,
            "review_stats": review_stats,
        },
    )


def about_view(request):
    """Maktab haqida: tarix, qadriyatlar, o'qituvchilar, infratuzilma va hujjatlar."""
    site_settings = SiteSettings.get_solo()
    teachers = Teacher.objects.filter(is_active=True).select_related("branch")
    documents = OfficialDocument.objects.filter(is_active=True)
    programs = EducationProgram.objects.filter(is_active=True)
    return render(
        request,
        "core/about.html",
        {
            "site_settings": site_settings,
            "teachers": teachers,
            "documents": documents,
            "programs": programs,
        },
    )


def contact_view(request):
    """Aloqa sahifasi va murojaat formasi."""
    site_settings = SiteSettings.get_solo()
    branches = Branch.objects.filter(is_active=True).prefetch_related("map_links").order_by("-is_primary", "name")
    form = ContactMessageForm(request.POST or None)

    if request.method == "POST":
        ip_hash = get_client_ip_hash(request)
        allowed, retry_after = check_rate_limit(
            scope="contact_submit",
            identifier=ip_hash,
            limit=5,
            window_seconds=600,
        )
        if not allowed:
            messages.error(
                request,
                f"Juda ko‘p murojaat yuborildi. Iltimos, {max(1, retry_after // 60)} daqiqadan keyin urinib ko‘ring.",
            )
            return render(
                request,
                "core/contact.html",
                {"site_settings": site_settings, "branches": branches, "form": form},
                status=429,
            )

        if form.is_valid():
            msg = form.save(commit=False)
            msg.ip_hash = ip_hash
            msg.save()
            record_analytics_event(
                request,
                event_type="contact_submit",
                branch=msg.branch,
                platform="website",
                page_path=request.path,
            )
            messages.success(
                request,
                "Murojaatingiz qabul qilindi! Maktab ma’muriyati tez orada siz bilan bog‘lanadi.",
            )
            return redirect("core:contact")

    return render(
        request,
        "core/contact.html",
        {"site_settings": site_settings, "branches": branches, "form": form},
    )


def privacy_policy_view(request):
    """Maxfiylik siyosati va analitika/cookie tushuntirishi."""
    site_settings = SiteSettings.get_solo()
    return render(request, "core/privacy.html", {"site_settings": site_settings})


def robots_txt_view(request):
    """Qidiruv tizimlari uchun robots.txt."""
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /boshqaruv/",
        "Disallow: /admin/",
        "Disallow: /api/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def custom_403_view(request, exception):
    return render(request, "errors/403.html", status=403)


def custom_404_view(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_500_view(request):
    return render(request, "errors/500.html", status=500)
