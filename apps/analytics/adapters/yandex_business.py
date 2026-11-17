"""Yandex Business rasmiy API adapteri."""
from django.conf import settings

from .base import AdapterStatusResult, BasePlatformAdapter


class YandexBusinessAdapter(BasePlatformAdapter):
    """
    Yandex Business API adapteri.
    Rasmiy ruxsat va tashkilot ID bo'lmaganda qo'lda import rejimini ko'rsatadi.
    """

    platform_code = "yandex"
    platform_label = "Yandex Business"

    def get_status(self) -> AdapterStatusResult:
        enabled = getattr(settings, "YANDEX_BUSINESS_API_ENABLED", False)
        token = getattr(settings, "YANDEX_BUSINESS_API_TOKEN", "")
        org_id = getattr(settings, "YANDEX_BUSINESS_ORG_ID", "")

        if not enabled or not token or not org_id:
            return AdapterStatusResult(
                platform=self.platform_code,
                platform_label=self.platform_label,
                is_configured=False,
                status_code="not_configured",
                message=(
                    "Yandex Business API hali ulanmagan. Yandex Business kabinetidan olingan "
                    "rasmiy statistikani qo‘lda import qilish formasi orqali kiriting."
                ),
            )

        return AdapterStatusResult(
            platform=self.platform_code,
            platform_label=self.platform_label,
            is_configured=True,
            status_code="ready",
            message="Yandex Business API sozlamalari kiritilgan.",
            details={"org_id": org_id},
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
                "Yandex Business API ulanishi sozlangan; kabinet ruxsati tasdiqlanganda "
                "ko'rsatkichlar avtomatik yangilanadi."
            ),
            details={"branch": branch.slug, "from": str(date_from), "to": str(date_to)},
        )
