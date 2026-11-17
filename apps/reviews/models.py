"""Sayt ichidagi ota-onalar fikrlari va maxfiylik roziligi modellari."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WebsiteReview(models.Model):
    """Sayt ichida qoldirilgan ota-onalar fikri (faqat moderatsiyadan keyin chiqadi)."""

    STATUS_CHOICES = [
        ("pending", "Moderatsiyada"),
        ("approved", "Tasdiqlangan"),
        ("rejected", "Rad etilgan"),
    ]

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="website_reviews",
        verbose_name="Filial",
    )
    author_name = models.CharField("Ism", max_length=100)
    display_name = models.CharField(
        "Saytda ko‘rinadigan ism (ixtiyoriy)",
        max_length=100,
        blank=True,
        help_text="Bo'sh qoldirilsa, asosiy ism ko'rinadi.",
    )
    phone = models.CharField(
        "Aloqa telefoni (ommaga chiqmaydi)",
        max_length=40,
        blank=True,
        help_text="Faqat zaruriyat bo'lganda ma'muriyat bog'lanishi uchun; saytda hech qachon ko'rsatilmaydi.",
    )
    rating = models.PositiveSmallIntegerField(
        "Baho (1–5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Fikr matni", max_length=1500)
    status = models.CharField("Holat", max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    admin_reply = models.TextField("Maktab javobi (ixtiyoriy)", blank=True)
    moderation_note = models.TextField("Ichki moderatsiya izohi", blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_reviews",
        verbose_name="Moderator",
    )
    moderated_at = models.DateTimeField("Moderatsiya vaqti", null=True, blank=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)
    created_at = models.DateTimeField("Yuborilgan vaqt", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Sayt fikri"
        verbose_name_plural = "Sayt ichidagi ota-onalar fikrlari"
        ordering = ["-created_at"]

    @property
    def public_author_label(self) -> str:
        """Ommaviy sahifalarda faqat ruxsat etilgan ko'rinadigan ismni qaytaradi."""
        return (self.display_name or self.author_name).strip()

    def __str__(self):
        return f"{self.public_author_label} ({self.rating}/5) — {self.get_status_display()}"


class ReviewConsent(models.Model):
    """Fikr yuborishda ota-ona tomonidan berilgan maxfiylik roziligi yozuvi."""

    review = models.OneToOneField(
        WebsiteReview,
        on_delete=models.CASCADE,
        related_name="consent",
        verbose_name="Fikr",
    )
    accepted_privacy_policy = models.BooleanField("Maxfiylik siyosatiga rozilik", default=False)
    policy_version = models.CharField("Siyosat versiyasi", max_length=20, default="1.0")
    consent_text_snapshot = models.TextField("Rozilik matni nusxasi")
    ip_hash = models.CharField("IP xeshi", max_length=64, blank=True)
    created_at = models.DateTimeField("Tasdiqlangan vaqt", auto_now_add=True)

    class Meta:
        verbose_name = "Fikr roziligi"
        verbose_name_plural = "Fikr roziliklari"

    def __str__(self):
        return f"Rozilik #{self.review_id} (v{self.policy_version})"
