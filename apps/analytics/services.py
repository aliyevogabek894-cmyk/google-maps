"""Maxfiylikka mos anonim analitika yig'ish servislari."""
import hashlib
import logging
from urllib.parse import urlsplit

from django.conf import settings
from django.utils import timezone

from apps.core.security import get_client_ip_hash
from .models import AnalyticsEvent

logger = logging.getLogger("turon.analytics")

BOT_UA_KEYWORDS = (
    "bot",
    "crawler",
    "spider",
    "slurp",
    "bingpreview",
    "facebookexternalhit",
    "headless",
    "lighthouse",
    "curl/",
    "wget/",
)


def is_likely_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    if not ua:
        return False
    return any(keyword in ua for keyword in BOT_UA_KEYWORDS)


def detect_device_type(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if not ua:
        return "other"
    if "ipad" in ua or "tablet" in ua or ("android" in ua and "mobile" not in ua):
        return "tablet"
    if "mobile" in ua or "iphone" in ua or "android" in ua:
        return "mobile"
    if "windows" in ua or "macintosh" in ua or "linux" in ua or "x11" in ua:
        return "desktop"
    return "other"


def extract_referrer_domain(request) -> str:
    referer = request.META.get("HTTP_REFERER", "").strip()
    if not referer:
        return "direct"
    try:
        parsed = urlsplit(referer)
        host = (parsed.hostname or "").lower()
        current_host = request.get_host().split(":")[0].lower()
        if not host or host == current_host:
            return "internal"
        return host[:120]
    except Exception:
        return ""


def get_anonymous_session_id(request) -> str:
    """
    Foydalanuvchi shaxsini aniqlamasdan tashriflar sonini hisoblash uchun
    kunlik tuzlangan anonim sessiya xeshini yaratadi.
    """
    session_key = ""
    if hasattr(request, "session") and request.session.session_key:
        session_key = request.session.session_key

    day_str = timezone.localdate().isoformat()
    if session_key:
        seed = f"{settings.ANALYTICS_SALT}:sess:{day_str}:{session_key}"
    else:
        ip_hash = get_client_ip_hash(request)
        ua = request.META.get("HTTP_USER_AGENT", "")[:80]
        seed = f"{settings.ANALYTICS_SALT}:anon:{day_str}:{ip_hash}:{ua}"

    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]


def record_analytics_event(
    request,
    *,
    event_type: str,
    branch=None,
    map_link=None,
    platform: str = "website",
    cta_label: str = "",
    page_path: str = "",
):
    """Analitika hodisasini xavfsiz tarzda yozadi."""
    try:
        resolved_path = (page_path or request.path or "/")[:255]
        ua = request.META.get("HTTP_USER_AGENT", "")
        return AnalyticsEvent.objects.create(
            event_type=event_type,
            branch=branch,
            map_link=map_link,
            platform=platform,
            cta_label=cta_label[:120],
            page_path=resolved_path,
            referrer_domain=extract_referrer_domain(request),
            utm_source=(request.GET.get("utm_source") or "")[:80],
            utm_campaign=(request.GET.get("utm_campaign") or "")[:80],
            device_type=detect_device_type(ua),
            anonymous_session_id=get_anonymous_session_id(request),
        )
    except Exception:
        logger.exception("AnalyticsEvent yozishda xatolik: %s", event_type)
        return None
