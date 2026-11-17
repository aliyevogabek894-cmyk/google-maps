"""Filiallar sahifalari va open-redirect'dan himoyalangan xarita yo'naltiruvi."""
import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from apps.analytics.services import record_analytics_event
from apps.core.security import check_rate_limit, get_client_ip_hash
from apps.reviews.models import WebsiteReview
from .models import Branch, MapLink
from .validators import validate_allowed_map_url

logger = logging.getLogger("turon.branches")


def branch_list_view(request):
    """Barcha faol filiallar ro'yxati."""
    branches = Branch.objects.filter(is_active=True).prefetch_related("map_links").order_by("-is_primary", "name")
    return render(request, "branches/branch_list.html", {"branches": branches})


def branch_detail_view(request, slug):
    """Alohida filial sahifasi: manzil, ish vaqti, xarita tugmalari va fikrlar."""
    branch = get_object_or_404(Branch, slug=slug, is_active=True)
    map_links = list(branch.map_links.filter(is_active=True).order_by("sort_order", "id"))
    approved_reviews = WebsiteReview.objects.filter(branch=branch, status="approved")[:5]
    return render(
        request,
        "branches/branch_detail.html",
        {
            "branch": branch,
            "map_links": map_links,
            "approved_reviews": approved_reviews,
        },
    )


def safe_map_redirect_view(request, slug, link_id):
    """
    Xarita tugmasi bosilganda AnalyticsEvent yozadi va foydalanuvchini faqat
    admin tasdiqlagan hamda ruxsat etilgan HTTPS xarita URL manziliga yo'naltiradi.
    Hech qanday query parametrli (?url=/?next=) tashqi yo'naltirish qabul qilinmaydi.
    """
    branch = get_object_or_404(Branch, slug=slug, is_active=True)
    map_link = get_object_or_404(MapLink, pk=link_id, branch=branch, is_active=True)

    try:
        validated_url = validate_allowed_map_url(map_link.target_url, platform=map_link.platform)
    except ValidationError:
        logger.warning(
            "Noto'g'ri yoki ruxsatsiz xarita URL bloklandi: branch=%s, link_id=%s",
            branch.slug,
            link_id,
        )
        return HttpResponseBadRequest("Ushbu xarita havolasi xavfsizlik tekshiruvidan o'tmadi.")

    # Spam kliklardan himoya: analitikaga yozishni cheklash, lekin foydalanuvchi o'tishini buzmaslik
    ip_hash = get_client_ip_hash(request)
    allowed_to_log, _ = check_rate_limit(
        scope=f"map_click:{map_link.pk}",
        identifier=ip_hash,
        limit=20,
        window_seconds=300,
    )
    if allowed_to_log:
        record_analytics_event(
            request,
            event_type="map_click",
            branch=branch,
            map_link=map_link,
            platform=map_link.platform,
            page_path=request.META.get("HTTP_REFERER", "")[:255] or branch.get_absolute_url(),
        )

    response = HttpResponseRedirect(validated_url)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response
