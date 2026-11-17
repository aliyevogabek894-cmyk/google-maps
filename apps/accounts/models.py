"""Foydalanuvchi rollari, 2FA tayyorligi va administrator amallari jurnali."""
from django.conf import settings
from django.db import models


ROLE_SUPERADMIN = "Superadmin"
ROLE_EDITOR = "Muharrir"
ROLE_MODERATOR = "Fikr moderatori"

ALL_STAFF_ROLES = (ROLE_SUPERADMIN, ROLE_EDITOR, ROLE_MODERATOR)


class StaffProfile(models.Model):
    """Xodimlar profili va qo'shimcha xavfsizlik ko'rsatkichlari."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
        verbose_name="Foydalanuvchi",
    )
    phone = models.CharField("Telefon raqami", max_length=30, blank=True)
    two_factor_enabled = models.BooleanField(
        "2FA (Ikki bosqichli tasdiqlash) faol",
        default=False,
        help_text="Xodim akkauntida TOTP/2FA yoqilganligini bildiradi.",
    )
    notes = models.CharField("Izoh", max_length=255, blank=True)
    updated_at = models.DateTimeField("Yangilangan vaqt", auto_now=True)

    class Meta:
        verbose_name = "Xodim profili"
        verbose_name_plural = "Xodimlar profillari"

    def __str__(self):
        return f"{self.user.get_username()} profili"


class AdminAuditLog(models.Model):
    """Administrator va moderator amallarining o'zgarmas audit jurnali."""

    ACTION_CHOICES = [
        ("user_login", "Tizimga kirish"),
        ("user_logout", "Tizimdan chiqish"),
        ("login_failed", "Muvaffaqiyatsiz kirish urinishi"),
        ("review_approved", "Fikr tasdiqlandi"),
        ("review_rejected", "Fikr rad etildi"),
        ("review_replied", "Fikrga javob yozildi"),
        ("branch_created", "Filial yaratildi"),
        ("branch_updated", "Filial yangilandi"),
        ("map_link_updated", "Xarita havolasi yangilandi"),
        ("content_updated", "Kontent yangilandi"),
        ("admission_updated", "Qabul arizasi holati o'zgartirildi"),
        ("contact_updated", "Murojaat holati o'zgartirildi"),
        ("platform_stat_imported", "Rasmiy platforma statistikasi import qilindi"),
        ("report_exported", "Hisobot eksport qilindi"),
        ("settings_updated", "Sayt sozlamalari yangilandi"),
        ("role_updated", "Foydalanuvchi roli yangilandi"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Bajaruvchi",
    )
    actor_username = models.CharField("Foydalanuvchi nomi", max_length=150, blank=True)
    action = models.CharField("Amal turi", max_length=50, choices=ACTION_CHOICES, db_index=True)
    target_model = models.CharField("Obyekt turi", max_length=100, blank=True)
    target_id = models.CharField("Obyekt ID", max_length=64, blank=True)
    summary = models.CharField("Qisqa tavsif", max_length=255)
    details = models.JSONField("Tafsilotlar", default=dict, blank=True)
    ip_hash = models.CharField("IP xeshi", max_length=64, blank=True)
    created_at = models.DateTimeField("Sana va vaqt", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Audit yozuvi"
        verbose_name_plural = "Audit jurnali"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.actor_username or 'Tizim'}: {self.summary}"
