"""Ichki anonim hodisalar va rasmiy Google/Yandex kabinet ko'rsatkichlari modellari."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class AnalyticsEvent(models.Model):
    """
    Sayt ichidagi faollik hodisalari.
    Shaxsni bevosita aniqlovchi ma'lumot (ism, telefon, xom IP) yig'ilmaydi.
    """

    EVENT_CHOICES = [
        ("page_view", "Sahifa ko‘rildi"),
        ("map_click", "Xarita tugmasi bosildi"),
        ("cta_click", "Harakat tugmasi (CTA) bosildi"),
        ("review_submit", "Saytda fikr yuborildi"),
        ("admission_submit", "Qabul arizasi yuborildi"),
        ("contact_submit", "Aloqa murojaati yuborildi"),
    ]

    PLATFORM_CHOICES = [
        ("website", "Rasmiy sayt"),
        ("google", "Google Maps"),
        ("yandex", "Yandex Maps"),
    ]

    DEVICE_CHOICES = [
        ("mobile", "Mobil telefon"),
        ("tablet", "Planshet"),
        ("desktop", "Kompyuter"),
        ("other", "Boshqa"),
    ]

    event_type = models.CharField("Hodisa turi", max_length=30, choices=EVENT_CHOICES, db_index=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
        verbose_name="Filial",
    )
    map_link = models.ForeignKey(
        "branches.MapLink",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
        verbose_name="Xarita havolasi",
    )
    platform = models.CharField("Platforma", max_length=20, choices=PLATFORM_CHOICES, default="website", db_index=True)
    cta_label = models.CharField("Tugma nomi", max_length=120, blank=True)
    page_path = models.CharField("Sahifa yo‘li", max_length=255, db_index=True)
    referrer_domain = models.CharField("Trafik manbasi (domen)", max_length=120, blank=True, db_index=True)
    utm_source = models.CharField("UTM manba", max_length=80, blank=True)
    utm_campaign = models.CharField("UTM kampaniya", max_length=80, blank=True)
    device_type = models.CharField("Qurilma turi", max_length=20, choices=DEVICE_CHOICES, default="other", db_index=True)
    anonymous_session_id = models.CharField("Anonim sessiya ID", max_length=64, db_index=True)
    created_at = models.DateTimeField("Sana va vaqt", default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Analitika hodisasi"
        verbose_name_plural = "Analitika hodisalari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["platform", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} ({self.platform}) — {self.page_path}"


class PlatformStatSnapshot(models.Model):
    """
    Google Business Profile yoki Yandex Business kabinetidan olingan rasmiy ko'rsatkichlar.
    Sayt ichidagi tugma bosishlaridan qat'iy ravishda alohida saqlanadi.
    """

    PLATFORM_CHOICES = [
        ("google", "Google Business Profile"),
        ("yandex", "Yandex Business"),
    ]

    SOURCE_TYPE_CHOICES = [
        ("api", "Tasdiqlangan rasmiy API"),
        ("manual_csv", "Admin CSV importi"),
        ("manual_form", "Admin qo‘lda kiritgan hisobot"),
    ]

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="platform_stats",
        verbose_name="Filial",
    )
    platform = models.CharField("Platforma", max_length=20, choices=PLATFORM_CHOICES, db_index=True)
    source_type = models.CharField("Manba usuli", max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual_form")
    source_label = models.CharField(
        "Ma’lumot manbasi",
        max_length=180,
        help_text="Masalan: Google Business Profile kabineti eksporti",
    )
    period_start = models.DateField("Davr boshlanishi")
    period_end = models.DateField("Davr tugashi")
    impressions = models.PositiveIntegerField("Qidiruv va xaritada ko‘rinishlar", default=0)
    profile_views = models.PositiveIntegerField("Profil ko‘rishlari", default=0)
    direction_clicks = models.PositiveIntegerField("Xaritada yo‘nalish so‘rovlari", default=0)
    call_clicks = models.PositiveIntegerField("Xaritadan qo‘ng‘iroqlar", default=0)
    website_clicks = models.PositiveIntegerField("Xaritadan saytga o‘tishlar", default=0)
    average_rating = models.DecimalField(
        "Platformadagi o‘rtacha baho",
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField("Platformadagi sharhlar soni", default=0)
    synced_at = models.DateTimeField("Oxirgi yangilangan vaqt", default=timezone.now)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_platform_stats",
        verbose_name="Kiritgan administrator",
    )
    notes = models.TextField("Izoh", blank=True)
    raw_payload = models.JSONField("Xom ma'lumot (ixtiyoriy)", default=dict, blank=True)

    class Meta:
        verbose_name = "Rasmiy platforma ko‘rsatkichi"
        verbose_name_plural = "Rasmiy platforma ko‘rsatkichlari"
        ordering = ["-period_end", "-synced_at"]

    def __str__(self):
        return f"{self.branch.name} — {self.get_platform_display()} ({self.period_start} .. {self.period_end})"
