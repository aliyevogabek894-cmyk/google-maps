"""Filiallar (Branch) va boshqariladigan xarita havolalari (MapLink) modellari."""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .validators import validate_allowed_map_url


class Branch(models.Model):
    """Maktab filiali modeli — birinchi filial Furqat, kelajakda boshqalar qo'shiladi."""

    VERIFICATION_CHOICES = [
        ("unverified", "Tasdiqlanmagan (tekshiruv zarur)"),
        ("pending", "Tasdiqlash jarayonida"),
        ("verified", "Rasman tasdiqlangan"),
    ]

    name = models.CharField("Filial nomi", max_length=150)
    slug = models.SlugField("URL identifikatori", max_length=120, unique=True)
    city_or_district = models.CharField("Tuman / Shahar", max_length=120, default="Furqat tumani")
    address = models.CharField("Manzil", max_length=255)
    landmark = models.CharField("Mo‘ljal", max_length=255, blank=True)
    phone = models.CharField("Telefon raqami", max_length=40)
    secondary_phone = models.CharField("Qo‘shimcha telefon", max_length=40, blank=True)
    email = models.EmailField("Filial elektron pochtasi", blank=True)
    working_hours = models.CharField("Ish vaqti", max_length=150, default="Dushanba–Shanba, 08:00–17:30")
    latitude = models.DecimalField("Kenglik (Latitude)", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Uzunlik (Longitude)", max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField("Filial haqida", blank=True)

    google_verification_status = models.CharField(
        "Google Business holati",
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default="pending",
    )
    yandex_verification_status = models.CharField(
        "Yandex Business holati",
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default="unverified",
    )
    verification_note = models.TextField(
        "Profil tekshiruvi eslatmasi",
        blank=True,
        default=(
            "Eslatma: Google Business'dagi 'FPGX+82H, A-376, Chirkay' manzili Furqat filiali "
            "ekanligini tasdiqlang, dublikat yaratmang va Yandex Business profilini tekshiring."
        ),
    )

    is_primary = models.BooleanField("Asosiy filial", default=False)
    is_active = models.BooleanField("Faol", default=True, db_index=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)
    created_at = models.DateTimeField("Yaratilgan vaqt", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan vaqt", auto_now=True)

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("branches:detail", kwargs={"slug": self.slug})

    def active_map_links(self):
        return self.map_links.filter(is_active=True).order_by("sort_order", "id")

    def review_map_links(self):
        return self.map_links.filter(is_active=True, link_type="review").order_by("sort_order", "id")


class MapLink(models.Model):
    """Admin paneldan boshqariladigan Google Maps va Yandex Maps havolalari."""

    PLATFORM_CHOICES = [
        ("google", "Google Maps"),
        ("yandex", "Yandex Maps"),
    ]

    LINK_TYPE_CHOICES = [
        ("profile", "Xaritada ko‘rish (Profil)"),
        ("directions", "Yo‘nalish olish"),
        ("review", "Fikr qoldirish"),
    ]

    DEFAULT_LABELS = {
        ("google", "profile"): "Google Maps’da ko‘rish",
        ("yandex", "profile"): "Yandex Maps’da ko‘rish",
        ("google", "directions"): "Yo‘nalish olish (Google)",
        ("yandex", "directions"): "Yo‘nalish olish (Yandex)",
        ("google", "review"): "Google’da fikr qoldirish",
        ("yandex", "review"): "Yandex’da fikr qoldirish",
    }

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="map_links",
        verbose_name="Filial",
    )
    platform = models.CharField("Platforma", max_length=20, choices=PLATFORM_CHOICES, db_index=True)
    link_type = models.CharField("Havola turi", max_length=20, choices=LINK_TYPE_CHOICES, db_index=True)
    label = models.CharField("Tugma matni", max_length=120, blank=True)
    target_url = models.URLField(
        "Rasmiy xarita URL manzili",
        max_length=500,
        validators=[validate_allowed_map_url],
        help_text="Faqat tasdiqlangan HTTPS Google yoki Yandex havolasini kiriting.",
    )
    is_verified_profile = models.BooleanField(
        "Profil egasi tasdiqlagan",
        default=False,
        help_text="Google/Yandex Business egaligi tasdiqlangach belgilang.",
    )
    is_active = models.BooleanField("Faol", default=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField("Tartib raqami", default=10)
    updated_at = models.DateTimeField("Yangilangan vaqt", auto_now=True)

    class Meta:
        verbose_name = "Xarita havolasi"
        verbose_name_plural = "Xarita havolalari"
        ordering = ["branch", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "platform", "link_type"],
                name="unique_branch_platform_link_type",
            )
        ]

    def clean(self):
        super().clean()
        if self.target_url:
            try:
                self.target_url = validate_allowed_map_url(self.target_url, platform=self.platform)
            except ValidationError as exc:
                raise ValidationError({"target_url": exc}) from exc
        if not self.label:
            self.label = self.DEFAULT_LABELS.get((self.platform, self.link_type), "Xaritada ochish")

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.DEFAULT_LABELS.get((self.platform, self.link_type), "Xaritada ochish")
        if self.target_url:
            self.target_url = validate_allowed_map_url(self.target_url, platform=self.platform)
        super().save(*args, **kwargs)

    def get_tracked_url(self):
        return reverse(
            "branches:map_redirect",
            kwargs={"slug": self.branch.slug, "link_id": self.pk},
        )

    def __str__(self):
        return f"{self.branch.name} — {self.get_platform_display()} ({self.get_link_type_display()})"
