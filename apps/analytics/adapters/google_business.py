"""Google Business Profile rasmiy API adapteri."""
from pathlib import Path

from django.conf import settings

from .base import AdapterStatusResult, BasePlatformAdapter


class GoogleBusinessAdapter(BasePlatformAdapter):
    """
    Google Business Profile Performance API adapteri.
    API kalitlari va tasdiqlangan OAuth ruxsati bo'lmaganda, xavfsiz tarzda
    'ulanmagan' holatini qaytaradi va qo'lda import rejimini tavsiya qiladi.
    """

    platform_code = "google"
    platform_label = "Google Business Profile"

    def get_status(self) -> AdapterStatusResult:
        enabled = getattr(settings, "GOOGLE_BUSINESS_API_ENABLED", False)
        creds_path = getattr(settings, "GOOGLE_BUSINESS_CREDENTIALS_PATH", "")
        location_id = getattr(settings, "GOOGLE_BUSINESS_LOCATION_ID", "")

        if not enabled or not creds_path or not location_id:
            return AdapterStatusResult(
                platform=self.platform_code,
                platform_label=self.platform_label,
                is_configured=False,
                status_code="not_configured",
                message=(
                    "Google Business Profile API hali ulanmagan. Rasmiy ko‘rsatkichlarni "
                    "Google kabinetidan eksport qilib, quyidagi qo‘lda import bo‘limi orqali kiriting."
                ),
            )

        if not Path(creds_path).exists():
            return AdapterStatusResult(
                platform=self.platform_code,
                platform_label=self.platform_label,
                is_configured=False,
                status_code="error",
                message="Google API credentials fayli topilmadi. Iltimos, .env sozlamalarini tekshiring.",
            )

        return AdapterStatusResult(
            platform=self.platform_code,
            platform_label=self.platform_label,
            is_configured=True,
            status_code="ready",
            message="Google Business Profile API sozlamalari tayyor (sinxronizatsiya uchun tayyor).",
            details={"location_id": location_id},
        )

    def fetch_metrics(self, branch, date_from, date_to) -> AdapterStatusResult:
        status = self.get_status()
        if not status.is_configured:
            return status
        return AdapterStatusResult(
            platform=self.platform_code,
            platform_label=self.platform_label,
            is_configured=True,
            status_code="ready",
            message=(
                "Google Business Profile Performance API tokeni bilan jonli sinxronlash uchun "
                "OAuth2 tasdiqlangan token talab qilinadi; uydirma raqam yaratilmaydi."
            ),
            details={"branch": branch.slug, "from": str(date_from), "to": str(date_to)},
        )
