"""Ota-onalar fikrlari sahifasi (sayt ichidagi fikrlar + Google/Yandex rasmiy havolalari)."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import redirect, render

from apps.analytics.services import record_analytics_event
from apps.branches.models import Branch, MapLink
from apps.core.models import SiteSettings
from apps.core.security import check_rate_limit, get_client_ip_hash
from .forms import WebsiteReviewForm
from .models import ReviewConsent, WebsiteReview


def reviews_page_view(request):
    """
    Ikki alohida fikr oqimini ko'rsatadi:
    1) Sayt ichidagi moderatsiyadan o'tgan fikrlar va yangi fikr formasi
    2) Google Maps va Yandex Maps'dagi rasmiy sharh sahifalariga neytral havolalar
    """
    site_settings = SiteSettings.get_solo()
    selected_branch_slug = request.GET.get("filial", "").strip()

    branches = Branch.objects.filter(is_active=True).prefetch_related("map_links").order_by("-is_primary", "name")
    approved_qs = WebsiteReview.objects.filter(status="approved").select_related("branch")
    if selected_branch_slug:
        approved_qs = approved_qs.filter(branch__slug=selected_branch_slug)

    stats = approved_qs.aggregate(total=Count("id"), avg=Avg("rating"))
    paginator = Paginator(approved_qs, 8)
    page_obj = paginator.get_page(request.GET.get("sahifa"))

    review_map_links = MapLink.objects.filter(
        branch__is_active=True, is_active=True, link_type="review"
    ).select_related("branch").order_by("-branch__is_primary", "sort_order")

    form = WebsiteReviewForm(request.POST or None)

    if request.method == "POST":
        ip_hash = get_client_ip_hash(request)
        allowed, retry_after = check_rate_limit(
            scope="review_submit",
            identifier=ip_hash,
            limit=3,
            window_seconds=3600,
        )
        if not allowed:
            messages.error(
                request,
                f"Fikr yuborish cheklovidan oshdingiz. Iltimos, {max(1, retry_after // 60)} daqiqadan keyin urinib ko‘ring.",
            )
            return render(
                request,
                "reviews/reviews.html",
                {
                    "site_settings": site_settings,
                    "branches": branches,
                    "selected_branch_slug": selected_branch_slug,
                    "page_obj": page_obj,
                    "stats": stats,
                    "review_map_links": review_map_links,
                    "form": form,
                },
                status=429,
            )

        if form.is_valid():
            with transaction.atomic():
                review = form.save(commit=False)
                review.status = "pending"
                review.save()
                ReviewConsent.objects.create(
                    review=review,
                    accepted_privacy_policy=True,
                    policy_version=site_settings.privacy_policy_version,
                    consent_text_snapshot=site_settings.review_consent_text,
                    ip_hash=ip_hash,
                )

            record_analytics_event(
                request,
                event_type="review_submit",
                branch=review.branch,
                platform="website",
                page_path=request.path,
            )
            messages.success(
                request,
                "Fikringiz uchun rahmat! Xolis mulohazangiz moderatsiyadan so‘ng saytda e’lon qilinadi.",
            )
            return redirect("reviews:list")

    return render(
        request,
        "reviews/reviews.html",
        {
            "site_settings": site_settings,
            "branches": branches,
            "selected_branch_slug": selected_branch_slug,
            "page_obj": page_obj,
            "stats": stats,
            "review_map_links": review_map_links,
            "form": form,
        },
    )
