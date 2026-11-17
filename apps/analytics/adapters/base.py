"""Rasmiy xarita platformalari API integratsiyasi uchun bazaviy adapter."""
from dataclasses import dataclass, field


@dataclass
class AdapterStatusResult:
    platform: str
    platform_label: str
    is_configured: bool
    status_code: str  # 'not_configured' | 'ready' | 'error'
    message: str
    details: dict = field(default_factory=dict)


class BasePlatformAdapter:
    """Google va Yandex rasmiy API integratsiya adapterlari uchun umumiy interfeys."""

    platform_code = ""
    platform_label = ""

    def get_status(self) -> AdapterStatusResult:
        raise NotImplementedError

    def fetch_metrics(self, branch, date_from, date_to) -> AdapterStatusResult:
        """
        Tasdiqlangan API ruxsati bo'lganda ko'rsatkichlarni oladi.
        Ruxsat bo'lmaganda hech qanday uydirma raqam qaytarmaydi.
        """
        raise NotImplementedError
