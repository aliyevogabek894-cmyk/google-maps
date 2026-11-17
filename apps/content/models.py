"""Ta'lim yo'nalishlari, xizmatlar, o'qituvchilar, yangiliklar, galereya va qabul modellari."""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from apps.core.security import validate_image_file


def validate_document_file(file_obj):
    if not file_obj:
        return
    if file_obj.size > 10 * 1024 * 1024:
        raise ValidationError("Hujjat hajmi 10 MB dan oshmasligi kerak.")


class EducationProgram(models.Model):
    """Sinf bosqichlari va asosiy ta'lim yo'nalishlari."""

    title = models.CharField("Yo‘nalish nomi", max_length=150)
    grade_range = models.CharField("Sinflar / Yosh guruhi", max_length=80)
    subjects_summary = models.CharField("Asosiy fanlar", max_length=255)
    description = models.TextField("Batafsil tavsif")
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)

    class Meta:
        verbose_name = "Ta'lim yo‘nalishi"
        verbose_name_plural = "Ta'lim yo‘nalishlari"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.title} ({self.grade_range})"


class SchoolService(models.Model):
    """Qo'shimcha mashg'ulotlar, to'garaklar, kun tartibi, ovqatlanish va transport."""

    CATEGORY_CHOICES = [
        ("club", "To‘garaklar va qo‘shimcha mashg‘ulotlar"),
        ("schedule", "Kun tartibi"),
        ("nutrition", "Ovqatlanish"),
        ("transport", "Maktab transporti"),
        ("other", "Boshqa xizmat"),
    ]

    category = models.CharField("Turkum", max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    title = models.CharField("Sarlavha", max_length=150)
    summary = models.TextField("Tavsif")
    schedule_info = models.CharField("Vaqt / jadval ma'lumoti", max_length=150, blank=True)
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)

    class Meta:
        verbose_name = "Maktab xizmati"
        verbose_name_plural = "Maktab xizmatlari"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"


class Teacher(models.Model):
    """O'qituvchilar jamoasi."""

    full_name = models.CharField("F.I.Sh.", max_length=150)
    subject_or_role = models.CharField("Fani / Lavozimi", max_length=150)
    experience_years = models.PositiveSmallIntegerField("Tajriba (yil)", default=1)
    bio = models.TextField("Qisqa ma'lumot", blank=True)
    photo = models.ImageField(
        "Surati",
        upload_to="teachers/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Filial",
    )
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)

    class Meta:
        verbose_name = "O‘qituvchi"
        verbose_name_plural = "O‘qituvchilar"
        ordering = ["sort_order", "full_name"]

    def __str__(self):
        return f"{self.full_name} — {self.subject_or_role}"


class OfficialDocument(models.Model):
    """Litsenziya, ustav va boshqa rasmiy hujjatlar."""

    title = models.CharField("Hujjat nomi", max_length=180)
    document_number = models.CharField("Hujjat raqami / sanasi", max_length=120, blank=True)
    description = models.TextField("Izoh", blank=True)
    file = models.FileField(
        "Fayl (PDF/JPG/PNG)",
        upload_to="documents/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"]), validate_document_file],
    )
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)

    class Meta:
        verbose_name = "Rasmiy hujjat"
        verbose_name_plural = "Rasmiy hujjatlar"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    """Yangiliklar, olimpiada, tadbirlar va e'lonlar."""

    CATEGORY_CHOICES = [
        ("news", "Yangilik"),
        ("event", "Tadbir"),
        ("olympiad", "Olimpiada va musobaqa"),
        ("achievement", "Yutuq"),
        ("announcement", "E’lon"),
    ]

    title = models.CharField("Sarlavha", max_length=200)
    slug = models.SlugField("URL identifikatori", max_length=180, unique=True)
    category = models.CharField("Turkum", max_length=20, choices=CATEGORY_CHOICES, default="news", db_index=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news_posts",
        verbose_name="Filial",
    )
    excerpt = models.CharField("Qisqa mazmun", max_length=300)
    body = models.TextField("Asosiy matn")
    image = models.ImageField(
        "Asosiy rasm",
        upload_to="news/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    published_at = models.DateTimeField("E’lon sanasi", db_index=True)
    is_published = models.BooleanField("Chop etilgan", default=True, db_index=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar va tadbirlar"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("content:news_detail", kwargs={"slug": self.slug})


class GalleryItem(models.Model):
    """Foto va video galereya elementi."""

    MEDIA_TYPE_CHOICES = [
        ("photo", "Fotosurat"),
        ("video", "Video havola"),
    ]

    title = models.CharField("Sarlavha", max_length=160)
    media_type = models.CharField("Turi", max_length=10, choices=MEDIA_TYPE_CHOICES, default="photo")
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_items",
        verbose_name="Filial",
    )
    image = models.ImageField(
        "Rasm",
        upload_to="gallery/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    video_url = models.URLField("Video havola (ixtiyoriy, HTTPS)", blank=True)
    caption = models.CharField("Izoh", max_length=255, blank=True)
    is_published = models.BooleanField("Ko‘rsatilsin", default=True, db_index=True)
    is_demo = models.BooleanField("Demo ma'lumot", default=False)
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Galereya elementi"
        verbose_name_plural = "Foto va video galereya"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title


class AdmissionStep(models.Model):
    """Qabul shartlari va kerakli hujjatlar bosqichlari."""

    STEP_TYPE_CHOICES = [
        ("condition", "Qabul sharti"),
        ("document", "Kerakli hujjat"),
        ("step", "Qabul bosqichi"),
    ]

    step_type = models.CharField("Turi", max_length=20, choices=STEP_TYPE_CHOICES, default="step")
    title = models.CharField("Sarlavha", max_length=160)
    description = models.TextField("Tavsif")
    sort_order = models.PositiveSmallIntegerField("Tartib", default=10)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Qabul ma'lumoti"
        verbose_name_plural = "Qabul shartlari va hujjatlar"
        ordering = ["step_type", "sort_order", "id"]

    def __str__(self):
        return self.title


class AdmissionApplication(models.Model):
    """Qabul sahifasidan yuborilgan ota-ona arizalari."""

    STATUS_CHOICES = [
        ("new", "Yangi ariza"),
        ("contacted", "Bog‘lanildi"),
        ("scheduled", "Suhbat belgilandi"),
        ("enrolled", "Qabul qilindi"),
        ("archived", "Arxivlandi"),
    ]

    parent_name = models.CharField("Ota-ona ismi", max_length=120)
    phone = models.CharField("Telefon raqami", max_length=40)
    student_name = models.CharField("O‘quvchi ismi", max_length=120)
    grade_level = models.CharField("Sinf (yoki tayyorlov)", max_length=60)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admission_applications",
        verbose_name="Filial",
    )
    notes = models.TextField("Qo‘shimcha izoh", blank=True, max_length=1000)
    accepted_privacy_policy = models.BooleanField("Maxfiylik roziligi", default=False)
    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    admin_note = models.TextField("Ma’muriyat izohi", blank=True)
    ip_hash = models.CharField("IP xeshi", max_length=64, blank=True)
    created_at = models.DateTimeField("Ariza sanasi", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Qabul arizasi"
        verbose_name_plural = "Qabul arizalari"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_name} ({self.grade_level}) — {self.parent_name}"
