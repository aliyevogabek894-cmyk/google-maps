"""Asosiy sayt sozlamalari, murojaatlar va rate-limit modellari."""
from django.db import models
from django.templatetags.static import static

from .security import validate_image_file

DEFAULT_REVIEW_INVITATION = (
    "Maktabimizdagi tajribangiz haqida xolis fikringizni qoldirishingiz mumkin. "
    "Fikringiz ijobiy yoki tanqidiy bo‘lishidan qat’i nazar, biz uchun muhim."
)

DEFAULT_CONSENT_TEXT = (
    "Fikrimni saytda moderatsiyadan so‘ng e’lon qilishga va shaxsiy ma’lumotlarni "
    "qayta ishlash hamda maxfiylik siyosati shartlariga roziman."
)

DEFAULT_PRIVACY_POLICY = (
    "Turon Odob-Ilm xususiy maktabi foydalanuvchilar va ota-onalarning shaxsiy "
    "ma’lumotlarini himoya qilishga sodiqdir.\n\n"
    "1. Yig‘iladigan ma’lumotlar: Qabul arizasi, aloqa formasi va sayt ichidagi "
    "fikr-mulohazalar orqali yuborilgan ism, telefon raqami va murojaat matni faqat "
    "maktab ma’muriyati bilan bog‘lanish va ta’lim xizmatini yaxshilash maqsadida saqlanadi.\n\n"
    "2. Ommaviylik va maxfiylik: Ota-onalar fikrlari moderatsiyadan o‘tgandan so‘ng "
    "saytda faqat ko‘rsatilgan ism (yoki taxallus), baho va fikr matni bilan e’lon qilinadi. "
    "Telefon raqami va aloqa ma’lumotlari hech qachon ommaga chiqarilmaydi.\n\n"
    "3. Analitika va cookie fayllar: Sayt tashriflar va xarita tugmalari bosilishini "
    "tahlil qilishda shaxsni bevosita aniqlovchi ma’lumotlar yig‘maydigan anonim sessiya "
    "identifikatoridan foydalanadi.\n\n"
    "4. Google Maps va Yandex Maps: Ushbu tugmalar bosilganda siz tegishli tashqi "
    "platformaning rasmiy sahifasiga o‘tasiz va u yerda qoldirilgan sharhlar o‘sha "
    "platformalarning o‘z maxfiylik qoidalariga bo‘ysunadi."
)


class SiteSettings(models.Model):
    """Maktab platformasining umumiy sozlamalari (yagona yozuv)."""

    school_name = models.CharField(
        "Maktab nomi", max_length=150, default="Turon Odob-Ilm xususiy maktabi"
    )
    short_name = models.CharField("Qisqa nom", max_length=60, default="Turon Odob-Ilm")
    tagline = models.CharField(
        "Shior / Tagline",
        max_length=200,
        default="Odob, zamonaviy ilm va mustahkam tarbiya maskani",
    )
    hero_title = models.CharField(
        "Bosh sahifa sarlavhasi",
        max_length=200,
        default="Turon Odob-Ilm — farzandingiz kelajagi uchun ishonchli ta’lim",
    )
    hero_subtitle = models.TextField(
        "Bosh sahifa kirish matni",
        default=(
            "Milliy qadriyatlar, odob-axloq va zamonaviy fanlarni uyg‘unlashtirgan "
            "xususiy maktab. Furqat filiali uchun qabul va rasmiy ma’lumotlar bir joyda."
        ),
    )
    about_short = models.TextField(
        "Maktab haqida qisqacha",
        default=(
            "Turon Odob-Ilm xususiy maktabi o‘quvchilarga chuqur bilim, axloqiy tarbiya, "
            "chet tillari va IT ko‘nikmalarini xavfsiz hamda qulay muhitda beradi."
        ),
    )
    about_history = models.TextField(
        "Maktab tarixi va maqsadi",
        blank=True,
        default=(
            "[DEMO] Maktabimiz yosh avlodga sifatli umumiy o‘rta ta’lim berish hamda "
            "ularda halollik, mas’uliyat va ilmga chanqoqlik fazilatlarini shakllantirish "
            "maqsadida tashkil etilgan."
        ),
    )
    about_values = models.TextField(
        "Asosiy qadriyatlar",
        blank=True,
        default=(
            "Odob va hurmat; chuqur fan bilimlari; shaxsiy yondashuv; ota-onalar bilan "
            "ochiq muloqot; xavfsiz va sog‘lom maktab muhiti."
        ),
    )
    about_infrastructure = models.TextField(
        "Infratuzilma va sharoitlar",
        blank=True,
        default=(
            "[DEMO] Yorug‘ va shinam sinf xonalari, kompyuter va til laboratoriyalari, "
            "kutubxona, sport maydonchasi, tibbiy nazorat va issiq ovqatlanish tizimi."
        ),
    )
    primary_phone = models.CharField("Asosiy telefon", max_length=40, default="+998 (XX) XXX-XX-XX")
    secondary_phone = models.CharField("Qo‘shimcha telefon", max_length=40, blank=True)
    email = models.EmailField("Elektron pochta", default="info@turon-odob-ilm.uz")
    telegram_url = models.URLField("Telegram havolasi", blank=True)
    instagram_url = models.URLField("Instagram havolasi", blank=True)
    youtube_url = models.URLField("YouTube havolasi", blank=True)
    facebook_url = models.URLField("Facebook havolasi", blank=True)
    logo = models.ImageField(
        "Rasmiy logotip",
        upload_to="branding/",
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    static_logo_path = models.CharField("Standart logotip yo‘li", max_length=255, blank=True, default="official_media/logo.png")
    founded_year = models.PositiveSmallIntegerField("Tashkil topgan yil", default=2022)
    license_number = models.CharField("Davlat litsenziyasi", max_length=120, default="Litsenziya № 038782 · 14.09.2022")
    privacy_policy_version = models.CharField("Maxfiylik siyosati versiyasi", max_length=20, default="1.0")
    privacy_policy_text = models.TextField("Maxfiylik siyosati matni", default=DEFAULT_PRIVACY_POLICY)
    review_consent_text = models.TextField("Fikr rozilik matni", default=DEFAULT_CONSENT_TEXT)
    review_invitation_text = models.TextField(
        "Ota-onalarga neytral fikr taklifi", default=DEFAULT_REVIEW_INVITATION
    )
    seo_default_description = models.CharField(
        "SEO meta tavsifi",
        max_length=160,
        default="Turon Odob-Ilm xususiy maktabi rasmiy sayti — ta’lim, qabul, Furqat filiali manzili va ota-onalar fikrlari.",
    )
    is_demo_mode = models.BooleanField(
        "Demo kontent belgisi faol",
        default=True,
        help_text="Tasdiqlangan haqiqiy maktab ma'lumotlari kiritilgach o'chirib qo'ying.",
    )
    updated_at = models.DateTimeField("Yangilangan vaqt", auto_now=True)

    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return self.school_name

    @property
    def resolved_logo_url(self) -> str:
        if self.logo:
            return self.logo.url
        if self.static_logo_path:
            return static(self.static_logo_path)
        return static("img/logo-turon.svg")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    """Aloqa sahifasidan kelgan murojaatlar."""

    STATUS_CHOICES = [
        ("new", "Yangi"),
        ("in_progress", "Ko‘rib chiqilmoqda"),
        ("resolved", "Hal qilindi"),
    ]

    full_name = models.CharField("F.I.Sh.", max_length=120)
    phone = models.CharField("Telefon raqami", max_length=40)
    email = models.EmailField("Elektron pochta", blank=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
        verbose_name="Filial",
    )
    subject = models.CharField("Mavzu", max_length=160)
    message = models.TextField("Murojaat matni", max_length=2000)
    accepted_privacy_policy = models.BooleanField("Maxfiylik roziligi", default=False)
    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    admin_note = models.TextField("Ma’muriyat izohi", blank=True)
    ip_hash = models.CharField("IP xeshi", max_length=64, blank=True)
    created_at = models.DateTimeField("Yuborilgan vaqt", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.subject}"


class RateLimitRecord(models.Model):
    """Formalar va login uchun rate limiting hisoblagichi."""

    key = models.CharField(max_length=128, unique=True)
    count = models.PositiveIntegerField(default=1)
    window_start = models.DateTimeField()

    class Meta:
        verbose_name = "Rate limit yozuvi"
        verbose_name_plural = "Rate limit yozuvlari"

    def __str__(self):
        return f"{self.key} ({self.count})"
