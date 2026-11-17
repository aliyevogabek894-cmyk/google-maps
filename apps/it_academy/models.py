"""IT va dasturlash yo'nalishi, kurslar hamda o'quvchi loyihalari modellari."""
from django.db import models
from django.templatetags.static import static

from apps.core.security import validate_image_file


class ITCourse(models.Model):
    """Maktabda real o'qitiladigan IT va dasturlash yo'nalishlari."""

    title = models.CharField("Kurs / fan nomi", max_length=160)
    grade_level = models.CharField("Sinflar", max_length=80)
    tools_stack = models.CharField(
        "Texnologiyalar / mavzular",
        max_length=255,
        help_text="Masalan: Kompyuter savodxonligi, Algoritmlar, Scratch, HTML/CSS, Python",
    )
    description = models.TextField("Tavsif")
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)

    class Meta:
        verbose_name = "IT yo‘nalishi"
        verbose_name_plural = "IT va dasturlash kurslari"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.title} ({self.grade_level})"


class ITProject(models.Model):
    """O'quvchilarning ruxsat etilgan IT loyihalari va laboratoriya namunalari."""

    PERMISSION_CHOICES = [
        ("verified_official", "Maktab rasmiy ruxsati tasdiqlangan"),
        ("pending_consent", "Ota-ona / muallif roziligi kutilmoqda"),
    ]

    title = models.CharField("Loyiha nomi", max_length=160)
    course = models.ForeignKey(
        ITCourse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="Yo‘nalish",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="it_projects",
        verbose_name="Filial",
    )
    author_display = models.CharField(
        "Muallif (faqat rozilik bilan)",
        max_length=120,
        blank=True,
        help_text="Ota-ona roziligi bo'lmasa bo'sh qoldiring.",
    )
    has_parent_consent = models.BooleanField("Ota-ona roziligi bor", default=False)
    summary = models.TextField("Loyiha haqida")
    image = models.ImageField(
        "Loyiha rasmi",
        upload_to="it_projects/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    static_image_path = models.CharField("Standart statik rasm yo‘li", max_length=255, blank=True)
    alt_text = models.CharField("Alt matn (accessibility)", max_length=255, blank=True)
    source_url = models.URLField("Manba havolasi", blank=True)
    permission_status = models.CharField(
        "Ruxsat holati", max_length=30, choices=PERMISSION_CHOICES, default="pending_consent"
    )
    project_url = models.URLField("Loyiha havolasi (ixtiyoriy, HTTPS)", blank=True)
    is_published = models.BooleanField("Saytda ko‘rsatilsin", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "IT loyiha"
        verbose_name_plural = "IT loyihalar"
        ordering = ["sort_order", "-created_at"]

    @property
    def resolved_image_url(self) -> str:
        if self.image:
            return self.image.url
        if self.static_image_path:
            return static(self.static_image_path)
        return ""

    @property
    def public_author_label(self) -> str:
        if self.has_parent_consent and self.author_display:
            return self.author_display
        return "Turon IT laboratoriyasi"

    def __str__(self):
        return self.title
