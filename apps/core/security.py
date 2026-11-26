"""Xavfsizlik, rate limiting, spam himoyasi va rasm tekshiruvi yordamchilari."""
import hashlib
import os
import time
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import transaction
from django.utils import timezone
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_client_ip(request) -> str:
    """So'rovdan mijoz IP manzilini xavfsiz tarzda oladi."""
    if request is None:
        return ""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "").strip()


def get_client_ip_hash(request) -> str:
    """Xom IP manzilini saqlamaslik uchun tuzlangan SHA-256 xeshini qaytaradi."""
    raw_ip = get_client_ip(request)
    if not raw_ip:
        return ""
    salted = f"{settings.ANALYTICS_SALT}:{raw_ip}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()[:32]


def validate_image_file(file_obj):
    """Yuklanayotgan rasm hajmi, kengaytmasi va haqiqiyligini tekshiradi."""
    if not file_obj:
        return
    max_mb = getattr(settings, "MAX_IMAGE_UPLOAD_MB", 5)
    if file_obj.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Rasm hajmi {max_mb} MB dan oshmasligi kerak.")

    ext = os.path.splitext(file_obj.name or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Faqat JPG, PNG yoki WEBP formatidagi rasmlar qabul qilinadi.")

    pos = file_obj.tell() if hasattr(file_obj, "tell") else None
    try:
        img = Image.open(file_obj)
        img.verify()
    except (UnidentifiedImageError, OSError, Exception) as exc:
        raise ValidationError("Yuklangan fayl haqiqiy rasm emas yoki buzilgan.") from exc
    finally:
        if pos is not None and hasattr(file_obj, "seek"):
            file_obj.seek(pos)


def check_rate_limit(scope: str, identifier: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """
    Ma'lumotlar bazasiga tayangan atomik rate limit tekshiruvi.
    Qaytaradi: (ruxsat_etilganmi: bool, kutish_soniyasi: int)
    """
    from .models import RateLimitRecord

    if not identifier:
        identifier = "unknown"

    raw_key = f"{scope}:{identifier}".encode("utf-8")
    key_hash = hashlib.sha256(raw_key).hexdigest()[:64]
    now = timezone.now()

    with transaction.atomic():
        record, created = RateLimitRecord.objects.select_for_update().get_or_create(
            key=key_hash,
            defaults={"count": 1, "window_start": now},
        )
        if created:
            return True, 0

        elapsed = (now - record.window_start).total_seconds()
        if elapsed >= window_seconds:
            record.count = 1
            record.window_start = now
            record.save(update_fields=["count", "window_start"])
            return True, 0

        if record.count >= limit:
            retry_after = max(1, int(window_seconds - elapsed))
            return False, retry_after

        record.count += 1
        record.save(update_fields=["count"])
        return True, 0


def generate_form_timestamp_token() -> str:
    """Botlardan himoya qilish uchun imzolangan vaqt belgisini yaratadi."""
    signer = TimestampSigner(salt="turon-form-guard")
    return signer.sign(str(int(time.time())))


def verify_form_anti_spam(honeypot_value: str, timestamp_token: str, min_seconds: float = 0.2) -> str | None:
    """
    Honeypot va minimal to'ldirish vaqtini tekshiradi.
    Xato bo'lsa o'zbek tilidagi xabar qaytaradi, aks holda None.
    """
    if honeypot_value and honeypot_value.strip():
        return "Avtomatik spam so'rov aniqlandi."

    if timestamp_token:
        signer = TimestampSigner(salt="turon-form-guard")
        try:
            signed_ts = signer.unsign(timestamp_token, max_age=timedelta(days=30))
            elapsed = time.time() - float(signed_ts)
            if elapsed < min_seconds:
                return "Forma juda tez yuborildi. Iltimos, ma'lumotlarni tekshirib qayta yuboring."
        except SignatureExpired:
            return None
        except (BadSignature, ValueError):
            return "Forma xavfsizlik tekshiruvidan o'tmadi. Sahifani yangilab qayta urinib ko'ring."

    return None
