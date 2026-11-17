"""Tashqi xarita havolalari uchun qat'iy HTTPS domen va open-redirect validatorlari."""
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError

EXACT_ONLY_HOSTS = {"goo.gl", "maps.app.goo.gl", "g.page", "ya.ru"}


def _host_matches_allowlist(hostname: str, allowed_domains: tuple[str, ...]) -> bool:
    host = hostname.lower().rstrip(".")
    for domain in allowed_domains:
        d = domain.lower().rstrip(".")
        if host == d:
            return True
        if d not in EXACT_ONLY_HOSTS and host.endswith(f".{d}"):
            return True
    return False


def validate_allowed_map_url(url: str, platform: str | None = None) -> str:
    """
    Faqat ruxsat etilgan HTTPS Google va Yandex xarita domenlariga ruxsat beradi.
    Open-redirect va xavfli sxemalarni (javascript:, http:, userinfo @) bloklaydi.
    """
    if not url or not isinstance(url, str):
        raise ValidationError("Xarita havolasi bo'sh bo'lishi mumkin emas.")

    cleaned = url.strip()
    if any(ch in cleaned for ch in ("\r", "\n", "\x00", "\\")):
        raise ValidationError("URL tarkibida ruxsat etilmagan belgilar mavjud.")

    parsed = urlsplit(cleaned)
    if parsed.scheme.lower() != "https":
        raise ValidationError("Xarita havolasi faqat HTTPS protokoli bilan boshlanishi shart.")

    if parsed.username or parsed.password:
        raise ValidationError("URL tarkibida foydalanuvchi ma'lumoti (@) bo'lishi mumkin emas.")

    if not parsed.hostname:
        raise ValidationError("URL tarkibida to'g'ri domen nomi topilmadi.")

    google_domains = getattr(settings, "ALLOWED_GOOGLE_MAP_DOMAINS", ())
    yandex_domains = getattr(settings, "ALLOWED_YANDEX_MAP_DOMAINS", ())

    is_google = _host_matches_allowlist(parsed.hostname, google_domains)
    is_yandex = _host_matches_allowlist(parsed.hostname, yandex_domains)

    if platform == "google":
        if not is_google:
            raise ValidationError(
                "Google havolasi faqat rasmiy Google domenlaridan (google.com, maps.google.com, g.page, maps.app.goo.gl) bo'lishi kerak."
            )
    elif platform == "yandex":
        if not is_yandex:
            raise ValidationError(
                "Yandex havolasi faqat rasmiy Yandex domenlaridan (yandex.uz, yandex.com, yandex.ru, ya.ru) bo'lishi kerak."
            )
    else:
        if not (is_google or is_yandex):
            raise ValidationError("Faqat rasmiy Google yoki Yandex HTTPS domenlariga ruxsat etiladi.")

    return cleaned
