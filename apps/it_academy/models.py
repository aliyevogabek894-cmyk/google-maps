"""IT va dasturlash yo'nalishi, kurslar, o'yin modullari va AI kelajak kasblari modellari."""
from django.core.validators import FileExtensionValidator
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


class GameModule(models.Model):
    """IT WORLD o'yin yordamida o'qitish metodikasi va interaktiv o'yin modullari."""

    CATEGORY_CHOICES = [
        ("sim3d", "3D Simulyator va Laboratoriya"),
        ("coding", "Dasturlash va Web Studio"),
        ("cyber_ai", "Kiberxavfsizlik va Sun’iy intellekt"),
        ("skills", "Klaviatura, Sichqoncha va Ofis"),
    ]

    title = models.CharField("O‘yin / modul nomi", max_length=150)
    subtitle = models.CharField("Qisqa sarlavha", max_length=160, blank=True)
    category = models.CharField("Turkum", max_length=20, choices=CATEGORY_CHOICES, default="sim3d", db_index=True)
    grade_range = models.CharField("Sinflar", max_length=50, default="1–11-sinflar")
    icon_emoji = models.CharField("Belgi", max_length=16, default="🎮")
    methodology = models.TextField("O‘qitish metodikasi va o‘rganiladigan ko‘nikmalar")
    image = models.ImageField(
        "O‘yin rasmi / skrinshot",
        upload_to="it_games/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    static_image_path = models.CharField("Standart rasm yo‘li", max_length=255, blank=True)
    live_url = models.URLField("O‘yin havolasi", default="https://aliyev-turon.netlify.app/")
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_featured = models.BooleanField("Bosh sahifada ko‘rsatilsin", default=True)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "IT o‘yin moduli"
        verbose_name_plural = "IT WORLD o‘yin modullari"
        ordering = ["sort_order", "id"]

    @property
    def resolved_image_url(self) -> str:
        if self.image:
            return self.image.url
        if self.static_image_path:
            return static(self.static_image_path)
        return ""

    def __str__(self):
        return f"{self.title} ({self.grade_range})"


class FutureCareerVideo(models.Model):
    """IT va Sun'iy intellekt yordamida kelajak kasblariga yo'l videolari."""

    title = models.CharField("Sarlavha", max_length=150)
    career_badge = models.CharField("Kasb nomi", max_length=80)
    quote_text = models.CharField("Video iqtibosi", max_length=240)
    description = models.TextField("Izoh")
    video_file = models.FileField(
        "MP4 Video fayl",
        upload_to="it_career_videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp4", "webm"])],
    )
    static_video_path = models.CharField("Standart video yo‘li", max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Kelajak kasbi videosi"
        verbose_name_plural = "IT & AI kelajak kasblari videolari"
        ordering = ["sort_order", "id"]

    @property
    def resolved_video_url(self) -> str:
        if self.video_file:
            return self.video_file.url
        if self.static_video_path:
            return static(self.static_video_path)
        return ""

    def __str__(self):
        return f"{self.career_badge}: {self.title}"
