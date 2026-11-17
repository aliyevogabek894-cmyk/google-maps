"""Boshlang'ich demo ma'lumotlar va standart rollarni yaratish buyrug'i."""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.services import ensure_default_roles
from apps.branches.models import Branch, MapLink
from apps.content.models import (
    AdmissionStep,
    EducationProgram,
    GalleryItem,
    NewsPost,
    OfficialDocument,
    SchoolService,
    Teacher,
)
from apps.core.models import SiteSettings
from apps.reviews.models import ReviewConsent, WebsiteReview


class Command(BaseCommand):
    help = "Turon Odob-Ilm (Furqat filiali) uchun rollar va aniq [DEMO] belgili boshlang'ich ma'lumotlarni yaratadi."

    def handle(self, *args, **options):
        created_roles = ensure_default_roles()
        self.stdout.write(self.style.SUCCESS(f"Rollar tekshirildi. Yangi yaratilganlari: {created_roles or 'barchasi mavjud'}"))

        site_settings = SiteSettings.get_solo()

        furqat, _ = Branch.objects.get_or_create(
            slug="furqat",
            defaults={
                "name": "Turon Odob-Ilm — Furqat filiali",
                "city_or_district": "Furqat tumani",
                "address": "[DEMO] Furqat tumani, tasdiqlanayotgan rasmiy manzil (tekshirish: FPGX+82H, A-376, Chirkay)",
                "landmark": "[DEMO] Asosiy yo‘l bo‘yi (ma’muriyat tomonidan aniqlashtiriladi)",
                "phone": "+998 (XX) XXX-XX-XX",
                "email": "furqat@turon-odob-ilm.uz",
                "working_hours": "Dushanba–Shanba, 08:00–17:30",
                "google_verification_status": "pending",
                "yandex_verification_status": "unverified",
                "description": (
                    "[DEMO] Turon Odob-Ilm xususiy maktabining birinchi va asosiy filiali. "
                    "Boshlang‘ich va yuqori sinflar, zamonaviy fanlar hamda milliy odob-axloq tarbiyasi."
                ),
                "is_primary": True,
                "is_active": True,
                "is_demo": True,
            },
        )

        # Hujjatda ko'rsatilgan tekshiriladigan boshlang'ich havolalar (admin paneldan yangilanadi)
        default_links = [
            (
                "google",
                "profile",
                "Google Maps’da ko‘rish",
                "https://www.google.com/maps/search/?api=1&query=Turon+Odob+Ilm+Furqat",
                10,
            ),
            (
                "google",
                "directions",
                "Yo‘nalish olish (Google)",
                "https://www.google.com/maps/dir/?api=1&destination=Turon+Odob+Ilm+Furqat",
                20,
            ),
            (
                "google",
                "review",
                "Google’da fikr qoldirish",
                "https://www.google.com/maps/search/?api=1&query=Turon+Odob+Ilm+Furqat",
                30,
            ),
            (
                "yandex",
                "profile",
                "Yandex Maps’da ko‘rish",
                "https://yandex.uz/maps/?text=Turon+Odob+Ilm+Furqat",
                40,
            ),
            (
                "yandex",
                "directions",
                "Yo‘nalish olish (Yandex)",
                "https://yandex.uz/maps/?rtext=~&rtt=auto&text=Turon+Odob+Ilm+Furqat",
                50,
            ),
            (
                "yandex",
                "review",
                "Yandex’da fikr qoldirish",
                "https://yandex.uz/maps/?text=Turon+Odob+Ilm+Furqat",
                60,
            ),
        ]
        for platform, link_type, label, url, order in default_links:
            MapLink.objects.get_or_create(
                branch=furqat,
                platform=platform,
                link_type=link_type,
                defaults={
                    "label": label,
                    "target_url": url,
                    "is_verified_profile": False,
                    "is_active": True,
                    "sort_order": order,
                },
            )

        if not EducationProgram.objects.exists():
            EducationProgram.objects.bulk_create([
                EducationProgram(
                    title="Boshlang‘ich ta’lim va odob maktabi",
                    grade_range="1–4-sinflar",
                    subjects_summary="Ona tili, matematika, o‘qish, odobnoma, ingliz tili, mantiq",
                    description="[DEMO] Bola shaxsiyatini mehr, tartib va mustaqil fikrlash asosida shakllantirish bosqichi.",
                    sort_order=10,
                    is_demo=True,
                ),
                EducationProgram(
                    title="Asosiy umumta’lim yo‘nalishi",
                    grade_range="5–9-sinflar",
                    subjects_summary="Matematika, fizika, kimyo, biologiya, tarix, ingliz va rus tillari, IT",
                    description="[DEMO] Chuqurlashtirilgan aniq va tabiiy fanlar hamda olimpiada tayyorgarligi.",
                    sort_order=20,
                    is_demo=True,
                ),
                EducationProgram(
                    title="Akademik va OTMga tayyorlov bosqichi",
                    grade_range="10–11-sinflar",
                    subjects_summary="IELTS, SAT/DTM fanlari, dasturlash, loyiha ishlari, kasbga yo‘naltirish",
                    description="[DEMO] Yuqori sinf o‘quvchilarini mahalliy va xalqaro universitetlarga maqsadli tayyorlash.",
                    sort_order=30,
                    is_demo=True,
                ),
            ])

        if not SchoolService.objects.exists():
            SchoolService.objects.bulk_create([
                SchoolService(
                    category="club",
                    title="Robototexnika, dasturlash va shaxmat to‘garaklari",
                    summary="[DEMO] Darsdan tashqari vaqtlarda mantiqiy fikrlash va amaliy ko‘nikmalarni rivojlantiruvchi mashg‘ulotlar.",
                    schedule_info="Dushanba, Chorshanba, Juma • 14:30–16:30",
                    sort_order=10,
                    is_demo=True,
                ),
                SchoolService(
                    category="schedule",
                    title="To‘liq kunlik o‘quv tartibi",
                    summary="[DEMO] Ertalabki saflanish, asosiy darslar, tushlik, uy vazifalarini ustoz nazoratida bajarish va to‘garaklar.",
                    schedule_info="08:00 – 17:00",
                    sort_order=20,
                    is_demo=True,
                ),
                SchoolService(
                    category="nutrition",
                    title="Halol va muvozanatli 3 mahal ovqatlanish",
                    summary="[DEMO] Bolalar yoshiga mos ravishda tayyorlangan issiq nonushta, tushlik va peshin tamaddisi.",
                    schedule_info="Har kuni oshxona nazorati",
                    sort_order=30,
                    is_demo=True,
                ),
                SchoolService(
                    category="transport",
                    title="Xavfsiz maktab avtobusi (ixtiyoriy)",
                    summary="[DEMO] Furqat tumani va yaqin hududlar bo‘yicha tasdiqlangan yo‘nalishlarda qatnov xizmati.",
                    schedule_info="Yo‘nalishlar ma’muriyat orqali aniqlanadi",
                    sort_order=40,
                    is_demo=True,
                ),
            ])

        if not Teacher.objects.exists():
            Teacher.objects.bulk_create([
                Teacher(
                    full_name="[DEMO] Ustoz namunasi — Matematika fani",
                    subject_or_role="Matematika va olimpiada murabbiyi",
                    experience_years=9,
                    bio="[DEMO] Haqiqiy o‘qituvchi ma’lumotlari admin panel orqali kiritiladi.",
                    branch=furqat,
                    sort_order=10,
                    is_demo=True,
                ),
                Teacher(
                    full_name="[DEMO] Ustoz namunasi — Ingliz tili fani",
                    subject_or_role="Ingliz tili o‘qituvchisi",
                    experience_years=7,
                    bio="[DEMO] Haqiqiy o‘qituvchi ma’lumotlari admin panel orqali kiritiladi.",
                    branch=furqat,
                    sort_order=20,
                    is_demo=True,
                ),
                Teacher(
                    full_name="[DEMO] Ustoz namunasi — Boshlang‘ich ta’lim",
                    subject_or_role="Boshlang‘ich sinf va tarbiya ustozi",
                    experience_years=11,
                    bio="[DEMO] Haqiqiy o‘qituvchi ma’lumotlari admin panel orqali kiritiladi.",
                    branch=furqat,
                    sort_order=30,
                    is_demo=True,
                ),
            ])

        if not OfficialDocument.objects.exists():
            OfficialDocument.objects.create(
                title="[DEMO] Ta’lim faoliyati litsenziyasi va maktab ustavi",
                document_number="Tasdiqlangan nusxa admin orqali yuklanadi",
                description="[DEMO] Maktabning rasmiy hujjat nusxalari shu bo‘limda e’lon qilinadi.",
                sort_order=10,
                is_demo=True,
            )

        if not NewsPost.objects.exists():
            now = timezone.now()
            NewsPost.objects.bulk_create([
                NewsPost(
                    title="[DEMO] Furqat filialida yangi o‘quv yili uchun qabul boshlandi",
                    slug="demo-furqat-filiali-qabul-boshlandi",
                    category="announcement",
                    branch=furqat,
                    excerpt="[DEMO] 1–11-sinflar hamda tayyorlov guruhlariga suhbat asosida qabul davom etmoqda.",
                    body=(
                        "[DEMO] Ushbu e’lon demo ma’lumot hisoblanadi. Haqiqiy qabul sanalari, "
                        "imtihon/suhbat jadvali va shartlari maktab ma’muriyati tomonidan admin panelda yangilanadi."
                    ),
                    published_at=now - timedelta(days=1),
                    is_published=True,
                    is_demo=True,
                ),
                NewsPost(
                    title="[DEMO] Maktabimiz o‘quvchilari fan olimpiadasiga tayyorlanmoqda",
                    slug="demo-fan-olimpiadasi-tayyorgarlik",
                    category="olympiad",
                    branch=furqat,
                    excerpt="[DEMO] Matematika, ona tili va ingliz tili yo‘nalishlarida qo‘shimcha mashg‘ulotlar yo‘lga qo‘yildi.",
                    body=(
                        "[DEMO] Olimpiada mashg‘ulotlari va maktab tadbirlari haqidagi haqiqiy yangiliklar "
                        "muharrirlar tomonidan chop etiladi."
                    ),
                    published_at=now - timedelta(days=4),
                    is_published=True,
                    is_demo=True,
                ),
            ])

        if not GalleryItem.objects.exists():
            GalleryItem.objects.bulk_create([
                GalleryItem(
                    title="[DEMO] Maktab sinf xonalari va o‘quv muhiti",
                    media_type="photo",
                    branch=furqat,
                    caption="[DEMO] Haqiqiy maktab fotosuratlari admin paneldan yuklangach ko‘rsatiladi.",
                    sort_order=10,
                    is_demo=True,
                ),
                GalleryItem(
                    title="[DEMO] Kutubxona va amaliy mashg‘ulotlar",
                    media_type="photo",
                    branch=furqat,
                    caption="[DEMO] Haqiqiy maktab fotosuratlari admin paneldan yuklangach ko‘rsatiladi.",
                    sort_order=20,
                    is_demo=True,
                ),
            ])

        if not AdmissionStep.objects.exists():
            AdmissionStep.objects.bulk_create([
                AdmissionStep(
                    step_type="condition",
                    title="Suhbat va bilim darajasini aniqlash",
                    description="O‘quvchining yoshiga mos tayyorgarligi va qiziqishlari ustozlar ishtirokida suhbat orqali baholanadi.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="document",
                    title="Tug‘ilganlik haqida guvohnoma nusxasi",
                    description="O‘quvchining shaxsini tasdiqlovchi hujjat nusxasi hamda ota-ona pasporti/ID kartasi nusxasi.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="document",
                    title="Tibbiy ma’lumotnoma (086-shakl) va 3×4 rasm",
                    description="Maktab shifokori ko‘rigi uchun zarur tibbiy varaqalar hamda 4 dona fotosurat.",
                    sort_order=20,
                ),
                AdmissionStep(
                    step_type="step",
                    title="1-qadam: Onlayn ariza yuboring",
                    description="Quyidagi qabul formasini to‘ldiring yoki telefon orqali bog‘laning.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="step",
                    title="2-qadam: Maktabga tashrif va suhbat",
                    description="Furqat filialimizga kelib sinflar bilan tanishing va farzandingiz suhbatdan o‘tsin.",
                    sort_order=20,
                ),
            ])

        if not WebsiteReview.objects.exists():
            r1 = WebsiteReview.objects.create(
                branch=furqat,
                author_name="N. Tursunova (Demo)",
                display_name="N. Tursunova (Demo namuna)",
                rating=5,
                comment=(
                    "[DEMO] Bu shablon uchun namunaviy fikr yozuvi. Haqiqiy ota-onalar fikrlari "
                    "saytdagi forma orqali yuborilib, moderatsiyadan keyin chiqariladi."
                ),
                status="approved",
                admin_reply="Rahmat! Haqiqiy fikrlar moderatsiyadan so‘ng shu yerda e’lon qilinadi.",
                is_demo=True,
            )
            ReviewConsent.objects.create(
                review=r1,
                accepted_privacy_policy=True,
                policy_version=site_settings.privacy_policy_version,
                consent_text_snapshot=site_settings.review_consent_text,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo ma'lumotlar muvaffaqiyatli yaratildi. Eslatma: Haqiqiy rasmiy Google/Yandex statistikasi uydirilmadi!"
            )
        )
