"""Turon Odob-Ilm (Furqat filiali) uchun tasdiqlangan rasmiy ma'lumotlar, media katalog va rollarni yuklash."""
from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal

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
from apps.it_academy.models import FutureCareerVideo, GameModule, ITCourse, ITProject
from apps.reviews.models import ReviewConsent, WebsiteReview


class Command(BaseCommand):
    help = "Turon Odob-Ilm rasmiy sayti, Telegram va YouTube manbalari asosida ma'lumotlarni yuklaydi."

    def handle(self, *args, **options):
        created_roles = ensure_default_roles()
        self.stdout.write(
            self.style.SUCCESS(f"Rollar tekshirildi: {created_roles or 'barchasi mavjud'}")
        )

        site_settings = SiteSettings.get_solo()
        site_settings.school_name = "Turon Odob-Ilm xususiy maktabi"
        site_settings.short_name = "Turon Odob-Ilm"
        site_settings.tagline = "Bilim, odob va kelajak — bir maktabda."
        site_settings.hero_title = "Bilim, odob va kelajak — bir maktabda."
        site_settings.hero_subtitle = (
            "Turon Odob-Ilm — Furqat tumanidagi litsenziyalangan xususiy o‘rta ta’lim muassasasi. "
            "Ingliz tili, IT va dasturlashga ixtisoslashgan, o‘zbek va rus ta’lim oqimlarini taklif etamiz."
        )
        site_settings.about_short = (
            "An’ana va zamonaviy ta’limning uyg‘unligi. Bolalarga akademik bilim bilan birga "
            "odob, mas’uliyat va mustaqil fikrlashni o‘rgatamiz."
        )
        site_settings.about_history = (
            "Maktabimiz 2022-yilda Furqat tumanida ochildi (Davlat litsenziyasi № 038782, 14.09.2022). "
            "Maqsadimiz — har bir o‘quvchiga sifatli ta’lim, axloqiy tarbiya va kelajak uchun zarur "
            "ko‘nikmalarni berish."
        )
        site_settings.about_values = (
            "Odob va mas’uliyat • Kichik sinflarda individual e’tibor • Kuchaytirilgan ingliz tili • "
            "Majburiy IT va dasturlash • Ota-onalar bilan ochiq muloqot."
        )
        site_settings.about_infrastructure = (
            "Zamonaviy bino, brendlangan sinfxonalar, faol IT va dasturlash laboratoriyasi, "
            "o‘zbek va rus ta’lim oqimlari, shuningdek 10 ta yo‘nalishda maktab avtobusi xizmati."
        )
        site_settings.primary_phone = "+998 55 808 55 75"
        site_settings.email = "info@turonodobilm.uz"
        site_settings.telegram_url = "https://t.me/turonodobilm"
        site_settings.instagram_url = "https://www.instagram.com/turonodobilm"
        site_settings.youtube_url = "https://www.youtube.com/@turonodobilm"
        site_settings.static_logo_path = "official_media/logo.png"
        site_settings.founded_year = 2022
        site_settings.license_number = "Litsenziya № 038782 · 14.09.2022"
        site_settings.is_demo_mode = False
        site_settings.save()

        furqat, _ = Branch.objects.update_or_create(
            slug="furqat",
            defaults={
                "name": "Turon Odob-Ilm — Furqat filiali",
                "city_or_district": "Farg‘ona viloyati, Furqat tumani",
                "address": "Farg‘ona viloyati, Furqat tumani, Yangi MFY, Surpa, dom 405",
                "landmark": "A-376 yo‘li bo‘yida, Chirkay / Navbahor hududi (Google Maps Plus-kod: FPGX+82H)",
                "phone": "+998 55 808 55 75",
                "email": "info@turonodobilm.uz",
                "working_hours": "Dushanba–Juma: 08:00–17:00 • Shanba: 08:00–13:00",
                "latitude": Decimal("40.475827"),
                "longitude": Decimal("70.746438"),
                "google_verification_status": "verified",
                "yandex_verification_status": "verified",
                "verification_note": (
                    "Google Business Profile (aliyevogabek894@gmail.com) va Yandex Business (97373032363) "
                    "to'liq tasdiqlangan (100% Verified). Xarita koordinatalari: 40.475827, 70.746438 (FPGX+82H)."
                ),
                "description": (
                    "Turon Odob-Ilm xususiy maktabining asosiy filiali. 1–11-sinflar, o‘zbek va rus "
                    "ta’lim oqimlari, ingliz tili hamda IT va dasturlash laboratoriyasi."
                ),
                "is_primary": True,
                "is_active": True,
                "is_demo": False,
            },
        )

        map_links_data = [
            (
                "yandex",
                "profile",
                "Yandex Maps’da ko‘rish",
                "https://yandex.uz/maps/org/turon_odob_ilm_xususiy_maktabi/97373032363/",
                True,
                10,
            ),
            (
                "yandex",
                "directions",
                "Yo‘nalish olish (Yandex)",
                "https://yandex.uz/maps/org/turon_odob_ilm_xususiy_maktabi/97373032363/",
                True,
                20,
            ),
            (
                "yandex",
                "review",
                "Yandex’da fikr qoldirish",
                "https://yandex.uz/maps/org/turon_odob_ilm_xususiy_maktabi/97373032363/reviews/",
                True,
                30,
            ),
            (
                "google",
                "profile",
                "Google Maps’da ko‘rish",
                "https://www.google.com/maps/place/Turon+odob-ilm+xususiy+maktabi/@40.4758271,70.7464378,17z/data=!3m1!4b1!4m6!3m5!1s0x38ba934614489b8d:0x845f65f9529b8a06!8m2!3d40.4758271!4d70.7464378!16s%2Fg%2F11tdf6s1yk?hl=uz",
                True,
                40,
            ),
            (
                "google",
                "directions",
                "Yo‘nalish olish (Google)",
                "https://www.google.com/maps/dir/?api=1&destination=40.4758271,70.7464378",
                True,
                50,
            ),
            (
                "google",
                "review",
                "Google’da fikr qoldirish",
                "https://g.page/r/CQaKm1L5ZV-EEBM/review",
                True,
                60,
            ),
        ]
        for platform, link_type, label, url, verified, order in map_links_data:
            MapLink.objects.update_or_create(
                branch=furqat,
                platform=platform,
                link_type=link_type,
                defaults={
                    "label": label,
                    "target_url": url,
                    "is_verified_profile": verified,
                    "is_active": True,
                    "sort_order": order,
                },
            )

        # Ta'lim dasturlari (turonodob-ilm.uz ma'lumotlari asosida)
        EducationProgram.objects.filter(is_demo=True).delete()
        programs_data = [
            (
                "Boshlang‘ich ta’lim",
                "1–4-sinflar",
                "O‘qish, yozish, matematika, ingliz tili, kompyuter savodxonligi, odobnoma",
                "Bolaning shaxsiyatini shakllantirish, o‘qish-yozish va asosiy ko‘nikmalarni mehr hamda tartib bilan o‘rgatish.",
                10,
            ),
            (
                "Umumiy o‘rta ta’lim",
                "5–9-sinflar",
                "Matematika, fizika, ona tili, rus tili, ingliz tili, IT va dasturlash",
                "Kuchli akademik baza, kuchaytirilgan ingliz tili va IT yo‘nalishi bo‘yicha chuqurlashgan o‘quv dasturi.",
                20,
            ),
            (
                "O‘rta maxsus va OTMga tayyorlov",
                "10–11-sinflar",
                "Majburiy fanlar, chuqurlashtirilgan yo‘nalish fanlari, IT loyihalar, ingliz tili",
                "Oliy ta’limga maqsadli tayyorlov, 60 ta variantli mukammal test mashg‘ulotlari va kasb tanlash yo‘l-yo‘riqlari.",
                30,
            ),
        ]
        for title, gr, subj, desc, order in programs_data:
            EducationProgram.objects.update_or_create(
                title=title,
                defaults={
                    "grade_range": gr,
                    "subjects_summary": subj,
                    "description": desc,
                    "sort_order": order,
                    "is_active": True,
                    "is_demo": False,
                },
            )

        # Maktab xizmatlari
        SchoolService.objects.filter(is_demo=True).delete()
        services_data = [
            (
                "club",
                "Kuchaytirilgan ingliz tili va IT to‘garaklari",
                "Birinchi sinfdan boshlab xalqaro standartlarga mos ingliz tili va barcha sinflar uchun majburiy IT darslari.",
                "O‘zbek va rus ta’lim oqimlari",
                10,
            ),
            (
                "schedule",
                "To‘liq o‘quv haftasi tartibi",
                "Dushanba–Juma to‘liq dars jadvali va Shanba kuni qo‘shimcha mashg‘ulotlar hamda test tayyorgarligi.",
                "Du–Ju: 08:00–17:00 • Sha: 08:00–13:00",
                20,
            ),
            (
                "transport",
                "10 ta yo‘nalishda maktab avtobusi",
                "O‘quvchilarning xavfsiz qatnovi uchun maktabning 10 ta yo‘nalishdagi avtobus xizmati (rasmiy YouTube videolavha asosida).",
                "Yo‘nalishlar ma’muriyat orqali aniqlanadi",
                30,
            ),
        ]
        for cat, title, summary, sched, order in services_data:
            SchoolService.objects.update_or_create(
                title=title,
                defaults={
                    "category": cat,
                    "summary": summary,
                    "schedule_info": sched,
                    "sort_order": order,
                    "is_active": True,
                    "is_demo": False,
                },
            )

        # IT Akademiya kurslari va laboratoriya loyihalari
        it_courses_data = [
            (
                "Kompyuter savodxonligi va raqamli asoslar",
                "1–4-sinflar",
                "Klaviatura madaniyati, fayl tizimi, xavfsiz internet, mantiqiy o‘yinlar",
                "Boshlang‘ich sinf o‘quvchilarida texnologiyalardan to‘g‘ri va ongli foydalanish ko‘nikmasini shakllantirish.",
                10,
            ),
            (
                "Algoritmik fikrlash va blokli dasturlash",
                "3–6-sinflar",
                "Algoritmlar, Scratch, interaktiv animatsiyalar, mantiqiy masalalar",
                "Murakkab muammolarni qadamlarga bo‘lish, vizual dasturlash orqali ijodiy loyihalar yaratish.",
                20,
            ),
            (
                "Dasturlash asoslari va zamonaviy web",
                "7–11-sinflar",
                "HTML5, CSS3, Python asoslari, amaliy laboratoriya mashg‘ulotlari",
                "Katta sinf o‘quvchilarini zamonaviy IT kasblariga tayyorlovchi majburiy va chuqurlashtirilgan amaliy darslar.",
                30,
            ),
        ]
        first_course = None
        for idx, (title, grade, stack, desc, order) in enumerate(it_courses_data):
            course_obj, _ = ITCourse.objects.update_or_create(
                title=title,
                defaults={
                    "grade_level": grade,
                    "tools_stack": stack,
                    "description": desc,
                    "sort_order": order,
                    "is_active": True,
                    "is_demo": False,
                },
            )
            if idx == 0:
                first_course = course_obj

        ITProject.objects.update_or_create(
            title="IT WORLD — Bolalar uchun o‘yin orqali IT va dasturlash ekotizimi",
            defaults={
                "course": first_course,
                "branch": furqat,
                "author_display": "Aliyev Og‘abek (IT ustozi)",
                "has_parent_consent": True,
                "summary": (
                    "Turon Odob-Ilm IT ustozi Aliyev Og‘abek tomonidan yaratilgan maxsus ta’lim-o‘yin platformasi: "
                    "3D Maktab dunyosi, PC Builder 3D, 3D Tarmoq Akademiyasi, 3D Printing Lab, Web Studio (100 bosqich), "
                    "Kiber Qalqon 3D va 20 kompyuterli sinf reytingi."
                ),
                "static_image_path": "official_media/it-lab-active.jpg",
                "alt_text": "Turon Odob-Ilm IT laboratoriyasida o‘yin orqali kompyuter va dasturlash mashg‘ulotlari",
                "source_url": "https://aliyev-turon.netlify.app/",
                "project_url": "https://aliyev-turon.netlify.app/",
                "permission_status": "verified_official",
                "is_published": True,
                "is_demo": False,
                "sort_order": 5,
            },
        )

        # IT WORLD o'yin metodikasi modullari (aliyev-turon.netlify.app asosida)
        game_modules_data = [
            (
                "TURON ODOB-ILM IT WORLD 3D",
                "360° Ochiq Dunyo Maktab O‘yini",
                "sim3d",
                "1–11-sinflar",
                "🏫",
                "Haqiqiy Turon Odob-Ilm maktabi binosi, hovlisi, avtobusi va 2 qavatli 8 ta IT laboratoriya bo‘ylab 360° sayohat, ustozlar va interaktiv topshiriqlar.",
                "https://aliyev-turon.netlify.app/#campus3d",
                "official_media/facade.jpg",
                True,
                10,
            ),
            (
                "PC Builder 3D & Ona Platani Yig‘ish",
                "Kompyuter arxitekturasi va ta’mirlash (7 va 25 bosqich)",
                "sim3d",
                "4–11-sinflar",
                "🛠️",
                "O‘quvchilar protsessor (CPU), RAM, SSD, quvvat bloki va kabellarni 3D korpusga qo‘lda joylab, kompyuterni yoqish va nosozliklarni topishni amalda o‘rganishadi.",
                "https://aliyev-turon.netlify.app/#pcbuilder",
                "official_media/it-lab-active.jpg",
                True,
                20,
            ),
            (
                "3D Tarmoq Akademiyasi (LAN/WAN/MAN/PAN)",
                "Switch, Router, Modem va Kabel ulash",
                "sim3d",
                "5–11-sinflar",
                "🌐",
                "Kompyuter xonasida 360° harakatlanib, kabel tortish, tarmoq qurilmalarini ulash (10 bosqich) hamda buzilgan tarmoqlarni tuzatish (10 bosqich).",
                "https://aliyev-turon.netlify.app/#netlab3d",
                "official_media/games/netlab-3d.svg",
                True,
                30,
            ),
            (
                "TURON 3D Printing Lab (2035)",
                "CAD Studio va qo‘lda 3D printer yig‘ish",
                "sim3d",
                "3–11-sinflar",
                "🧊",
                "Futuristik 3D bosib chiqarish laboratoriyasi: 3D CAD Studio, printer qismlarini qo‘lda yig‘ish va PLA/PETG/ABS qatlamma-qatlam chop etish.",
                "https://aliyev-turon.netlify.app/#printergame",
                "official_media/games/printing-3d.svg",
                False,
                40,
            ),
            (
                "Web Studio (100 bosqich) & Code Master",
                "Scratch, HTML, CSS va Python",
                "coding",
                "3–11-sinflar",
                "💻",
                "Blokli dasturlashdan tortib soyali kod ustidan HTML/CSS yozib shaxsiy sayt yaratish va Python topshiriqlarini yechish metodikasi.",
                "https://aliyev-turon.netlify.app/#games",
                "official_media/games/web-studio.svg",
                True,
                50,
            ),
            (
                "Kiber Qalqon 3D & Kiberqahramon",
                "20 bosqich • 300 ta kiberxavfsizlik sinovi",
                "cyber_ai",
                "4–11-sinflar",
                "🛡️",
                "Kuchli parol yaratish, firibgar (phishing) havolalarni ajratish, Firewall, SQLi va XSS himoyasini o‘yin shaklida o‘zlashtirish.",
                "https://aliyev-turon.netlify.app/#games",
                "official_media/games/cyber-shield.svg",
                True,
                60,
            ),
            (
                "AI Challenge — Sun’iy intellekt",
                "Prompt muhandisligi va AI asoslari",
                "cyber_ai",
                "5–11-sinflar",
                "✨",
                "Sun’iy intellekt qanday ishlashini amalda sinab ko‘rish, ma’lumotlarni tasniflash va AI’ga to‘g‘ri savol (prompt) berish mashqlari.",
                "https://aliyev-turon.netlify.app/#games",
                "official_media/games/ai-challenge.svg",
                True,
                70,
            ),
            (
                "HOTKEY MASTER & Mouse/Keyboard Master",
                "20 kompyuterli sinf reytingi • 10 barmoqda yozish",
                "skills",
                "1–11-sinflar",
                "⌨️",
                "Interaktiv klaviatura, Ctrl+C/Win+D/F5 kabi tezkor tugmalar, sichqoncha chaqqonligi (Mouse Master 3D) va sinf ichidagi jonli musobaqa.",
                "https://aliyev-turon.netlify.app/#hotkey",
                "official_media/games/hotkey-master.svg",
                False,
                80,
            ),
            (
                "Windows 11 Akademiyasi & Office Champion",
                "ISO, Rufus, BIOS, Word, Excel, PowerPoint",
                "skills",
                "3–11-sinflar",
                "📊",
                "Operatsion tizimni 0 dan o‘rnatish (BIOS, disk bo‘lish, drayverlar) va ofis dasturlarida hujjat, jadval hamda taqdimot yaratish.",
                "https://aliyev-turon.netlify.app/#games",
                "official_media/games/win-office.svg",
                False,
                90,
            ),
            (
                "Sarguzasht Xaritasi (5 ta orol, 15 ta modul)",
                "XP, Yulduzlar va Daraja tizimi (+300 XP)",
                "coding",
                "1–11-sinflar",
                "🏝️",
                "Bolalarni rag‘batlantiruvchi XP ballari, tangalar va 5 ta sarguzasht oroli orqali kompyuter tarixidan tortib algoritmlargacha qadam-baqadam o‘rgatish.",
                "https://aliyev-turon.netlify.app/#islands",
                "official_media/games/adventure-islands.svg",
                False,
                100,
            ),
        ]
        for title, sub, cat, grades, emoji, meth, url, img_path, featured, order in game_modules_data:
            GameModule.objects.update_or_create(
                title=title,
                defaults={
                    "subtitle": sub,
                    "category": cat,
                    "grade_range": grades,
                    "icon_emoji": emoji,
                    "methodology": meth,
                    "live_url": url,
                    "static_image_path": img_path,
                    "is_featured": featured,
                    "is_active": True,
                    "sort_order": order,
                },
            )

        # IT va Sun'iy intellekt bilan kelajak kasblariga yo'l videolari
        career_videos_data = [
            (
                "IT va Biznes boshqaruvi (CEO)",
                "Tadbirkor / CEO",
                "“Assalomu alaykum! Mana IT’dan yaxshi o‘qiganim uchun biznesmen bo‘ldim. Ota-onamga rahmat!”",
                "Zamonaviy tadbirkorlik, raqamli tahlil va IT loyihalarni boshqarish orqali kelajakda o‘z biznesini yaratish osonlashadi.",
                "official_media/videos/career-ceo.mp4",
                10,
            ),
            (
                "IT va Davlat / Kiberxavfsizlik",
                "Ichki ishlar mutaxassisi",
                "“Assalomu alaykum! Mana IT’dan yaxshi o‘qiganim uchun ichki ishlarda ishlayapman.”",
                "Axborot xavfsizligi, raqamli tizimlar va kiberhimoya bilimlari huquq-tartibot hamda davlat xizmatida katta ustunlik beradi.",
                "official_media/videos/career-officer.mp4",
                20,
            ),
            (
                "IT va Sun’iy intellekt ilm-fani",
                "Olim / Tadqiqotchi",
                "“Assalomu alaykum! Mana IT’dan yaxshi o‘qiganim uchun olim bo‘ldim.”",
                "Fizika, kimyo, biologiya va matematika fanlarini IT hamda Sun’iy intellekt bilan birlashtirib ilmiy kashfiyotlar qilish oson.",
                "official_media/videos/career-scientist.mp4",
                30,
            ),
            (
                "IT va Zamonaviy Tibbiyot",
                "Stomatolog / Shifokor",
                "“Assalomu alaykum! Mana IT’dan yaxshi o‘qiganim uchun stomatolog bo‘ldim. Ota-onamga rahmat!”",
                "Bugungi tibbiyot 3D diagnostika, raqamli tasvir va AI tahlilisiz ishlamaydi — IT bilgan shifokor zamon bilan hamnafas bo‘ladi.",
                "official_media/videos/career-dentist.mp4",
                40,
            ),
        ]
        for title, badge, quote, desc, vid_path, order in career_videos_data:
            FutureCareerVideo.objects.update_or_create(
                title=title,
                defaults={
                    "career_badge": badge,
                    "quote_text": quote,
                    "description": desc,
                    "static_video_path": vid_path,
                    "sort_order": order,
                    "is_active": True,
                },
            )

        # Rahbariyat va Ustozlar (Director Hayotbek + IT Ustozi Aliyev Og'abek)
        Teacher.objects.filter(is_demo=True).delete()
        Teacher.objects.update_or_create(
            full_name="A’zamjonov Hayotbek",
            defaults={
                "subject_or_role": "Maktab direktori",
                "experience_years": 5,
                "bio": "Turon Odob-Ilm xususiy maktabi rahbari.",
                "quote": "Bizning maqsadimiz — zamonaviy bilim, kuchli tarbiya va keng dunyoqarashga ega avlodni voyaga yetkazish.",
                "static_photo_path": "official_media/director-hayotbek.jpg",
                "is_leadership": True,
                "branch": furqat,
                "sort_order": 1,
                "is_active": True,
                "is_demo": False,
            },
        )
        Teacher.objects.update_or_create(
            full_name="Aliyev Og‘abek",
            defaults={
                "subject_or_role": "IT va dasturlash fani o‘qituvchisi • IT WORLD muallifi",
                "experience_years": 4,
                "bio": (
                    "Turon Odob-Ilm maktabining yetakchi IT ustozi va o‘quvchilar uchun maxsus yaratilgan "
                    "IT WORLD (aliyev-turon.netlify.app) interaktiv 3D o‘yin-ta’lim platformasi muallifi. "
                    "Bolalarga kompyuter savodxonligi, 3D qurilmalar yig‘ish, tarmoqlar, kiberxavfsizlik, "
                    "HTML/CSS/Python dasturlash va sun’iy intellektni zamonaviy o‘yin metodikasi orqali o‘rgatadi."
                ),
                "quote": (
                    "Bola kompyuter va dasturlashni quruq yodlash bilan emas, balki qiziqarli 3D o‘yin, "
                    "amaliy tajriba va kashfiyot orqali sevib o‘rgansagina haqiqiy natijaga erishadi."
                ),
                "static_photo_path": "official_media/teacher-aliyev.jpg",
                "is_leadership": False,
                "branch": furqat,
                "sort_order": 2,
                "is_active": True,
                "is_demo": False,
            },
        )
        Teacher.objects.update_or_create(
            full_name="Lola teacher (YouTube rasmiy lavha)",
            defaults={
                "subject_or_role": "Ingliz tili ustozi",
                "experience_years": 5,
                "bio": "Rasmiy @turonodobilm YouTube kanalida tanishtirilgan ingliz tili o‘qituvchisi.",
                "is_leadership": False,
                "branch": furqat,
                "sort_order": 10,
                "is_active": True,
                "is_demo": False,
            },
        )

        # Rasmiy hujjat (litsenziya PDF)
        OfficialDocument.objects.filter(is_demo=True).delete()
        OfficialDocument.objects.update_or_create(
            title="Davlat ta’lim litsenziyasi (Turon Odob-Ilm MChJ)",
            defaults={
                "document_number": "Litsenziya № 038782 · 14.09.2022",
                "description": "O‘zbekiston Respublikasi tomonidan berilgan rasmiy ta’lim faoliyati litsenziyasi.",
                "static_file_path": "official_media/license.pdf",
                "source_url": "https://www.turonodob-ilm.uz/documents/license.pdf",
                "sort_order": 1,
                "is_active": True,
                "is_demo": False,
            },
        )

        # Haqiqiy maktab rasmlari va rasmiy YouTube videolari (manba va ruxsat metadata bilan)
        GalleryItem.objects.filter(is_demo=True).delete()
        official_photos = [
            (
                "Turon Odob-Ilm xususiy maktabi binosi",
                "campus",
                "official_media/facade.jpg",
                "https://www.turonodob-ilm.uz/images/facade.jpg",
                "Turon Odob-Ilm xususiy maktabining Furqat tumanidagi asosiy binosi old ko‘rinishi",
                "Maktabning asosiy kirish qismi va hovlisi",
                10,
            ),
            (
                "IT va dasturlash laboratoriyasi",
                "it_lab",
                "official_media/it-lab-active.jpg",
                "https://www.turonodob-ilm.uz/images/it-lab-active.jpg",
                "O‘quvchilar IT laboratoriyasida zamonaviy kompyuterlarda dasturlash darsida",
                "Kompyuter savodxonligi va dasturlash amaliyoti",
                20,
            ),
            (
                "Brendlangan o‘quv sinfxonasi",
                "classroom",
                "official_media/classroom-branded.jpg",
                "https://www.turonodob-ilm.uz/images/classroom-branded.jpg",
                "Turon Odob-Ilm brendlangan zamonaviy yorug‘ sinfxona",
                "Qulay partalar va zamonaviy sinfxona jihozlari",
                30,
            ),
            (
                "Dars jarayoni — diqqat va intizom",
                "classroom",
                "official_media/students-attentive.jpg",
                "https://www.turonodob-ilm.uz/images/students-attentive.jpg",
                "Turon Odob-Ilm o‘quvchilari dars jarayonida",
                "Kichik sinflarda ustoz bilan faol mashg‘ulot",
                40,
            ),
            (
                "O‘quvchilar mustaqil mashg‘ulotda",
                "classroom",
                "official_media/students-studying.jpg",
                "https://www.turonodob-ilm.uz/images/students-studying.jpg",
                "Sinfxonada o‘quvchilarning dars tayyorlash jarayoni",
                "Jamoaviy va individual ta’lim muhiti",
                50,
            ),
            (
                "Operatsion tizimlar va Linux/Ubuntu amaliyoti",
                "it_lab",
                "official_media/it-class-ubuntu.jpg",
                "",
                "O‘quvchilar IT xonasida kompyuterda Linux Ubuntu va amaliy darslarni bajarishmoqda",
                "Zamonaviy kompyuter xonasida amaliy dars va daftar bilan ishlash",
                22,
            ),
            (
                "SMM, Linux, Windows, macOS va AI darsi",
                "it_lab",
                "official_media/it-class-os-ai.jpg",
                "",
                "IT sinfida SMM, Linux, Windows, macOS yo‘nalishlari va Sun’iy intellekt bilan ishlash",
                "O‘quvchilar Sun’iy intellekt va operatsion tizimlar bo‘yicha topshiriq bajarmoqda",
                24,
            ),
        ]
        for title, cat, static_path, src_url, alt, caption, order in official_photos:
            GalleryItem.objects.update_or_create(
                title=title,
                media_type="photo",
                defaults={
                    "category": cat,
                    "branch": furqat,
                    "static_asset_path": static_path,
                    "source_url": src_url,
                    "media_date": date(2026, 1, 1),
                    "alt_text": alt,
                    "permission_status": "official_pending_confirm",
                    "caption": caption,
                    "is_published": True,
                    "is_demo": False,
                    "sort_order": order,
                },
            )

        official_videos = [
            (
                "Turon odob-ilm — rasmiy maktab taqdimoti",
                "l5dlZAQIuA8",
                "Maktab muhiti, o‘quvchilar va dars jarayonlari haqida rasmiy video.",
                60,
            ),
            (
                "Turon odob-ilm maktabida qabul boshlandi!",
                "UssGBrMwMXs",
                "Yangi o‘quv yili qabul jarayoni va imkoniyatlar haqida videorolik.",
                70,
            ),
            (
                "O‘quvchilarimizning maktab haqidagi fikrlari",
                "ySq8HMHUJYM",
                "Turon Odob-Ilm o‘quvchilari maktab hayoti va ustozlar haqida.",
                80,
            ),
            (
                "10 ta yo‘nalishda avtobus xizmati",
                "ULKS9NIUODU",
                "O‘quvchilarni tashish uchun maktab avtobusi yo‘nalishlari haqida lavha.",
                90,
            ),
            (
                "Majburiy fanlarda 60 ta variantli mukammal testlar",
                "MVVFBhK3cBw",
                "Yuqori sinflar uchun test tayyorgarligi jarayonidan lavha.",
                100,
            ),
            (
                "Ingliz tili ustozimiz Lola teacher",
                "yFuCjZwmEXo",
                "Ingliz tili darslari va o‘qitish uslubi haqida video.",
                110,
            ),
        ]
        for title, yid, caption, order in official_videos:
            GalleryItem.objects.update_or_create(
                youtube_id=yid,
                defaults={
                    "title": title,
                    "media_type": "video",
                    "category": "video",
                    "branch": furqat,
                    "video_url": f"https://www.youtube.com/watch?v={yid}",
                    "source_url": f"https://www.youtube.com/watch?v={yid}",
                    "alt_text": f"{title} — Turon Odob-Ilm YouTube videosi",
                    "permission_status": "youtube_embed",
                    "caption": caption,
                    "is_published": True,
                    "is_demo": False,
                    "sort_order": order,
                },
            )

        # Haqiqiy yangiliklar va yutuqlar (rasmiy @turonodobilm Telegram kanali asosida)
        NewsPost.objects.filter(is_demo=True).delete()
        news_items = [
            (
                "Furqat tumani fan olimpiadasida 10 nafar o‘quvchimiz g‘olib bo‘ldi",
                "furqat-fan-olimpiadasi-10-golib",
                "olympiad",
                "Turon Odob-Ilm xususiy maktabining 10 nafar o‘quvchisi Furqat tumani fan olimpiadasida g‘oliblikni qo‘lga kiritdi.",
                (
                    "Quvonchli xabar! Turon Odob-Ilm xususiy maktabining 10 nafar o‘quvchisi "
                    "Furqat tumani fan olimpiadasida munosib ishtirok etib, g‘oliblikni qo‘lga kiritishdi. "
                    "Barcha g‘olib o‘quvchilarimizni, ularning ustozlari va ota-onalarini tabriklaymiz.\n\n"
                    "Aloqa: +998 55 808 55 75 (@turonodobilm_furqat)"
                ),
                "official_media/students-attentive.jpg",
                "https://t.me/turonodobilm/648",
                datetime(2026, 11, 10, 5, 48, tzinfo=dt_timezone.utc),
            ),
            (
                "IRN Xalqaro Olimpiadasida o‘quvchilarimiz faxrli g‘oliblikni qo‘lga kiritdi",
                "irn-xalqaro-olimpiada-galaba",
                "achievement",
                "Toshkent shahrida bo‘lib o‘tgan IRN Xalqaro Olimpiadasida maktabimiz o‘quvchilari muvaffaqiyatli qatnashdi.",
                (
                    "Turon Odob-Ilm xususiy maktabi o‘quvchilari Toshkent shahrida bo‘lib o‘tgan "
                    "IRN Xalqaro Olimpiadasida munosib ishtirok etib, faxrli g‘oliblikni qo‘lga kiritishdi. "
                    "Ushbu yutuq o‘quvchilarimizning tinimsiz mehnati va ustozlarimizning fidokorona "
                    "mehnatining samarasidir."
                ),
                "official_media/facade.jpg",
                "https://t.me/turonodobilm/647",
                datetime(2026, 11, 10, 5, 45, tzinfo=dt_timezone.utc),
            ),
            (
                "Furqat filialida SAT xalqaro imtihon imkoniyati yo‘lga qo‘yildi",
                "furqat-sat-xalqaro-imtihon",
                "achievement",
                "Turon Odob-Ilm xususiy maktabi Furqat filialida o‘quvchilar uchun SAT xalqaro imtihonini topshirish imkoniyati yaratildi.",
                (
                    "Turon Odob-Ilm xususiy maktabi Furqat filialida endi SAT xalqaro imtihonini topshirish "
                    "imkoniyati mavjud! SAT imtihoni orqali o‘quvchilar matematika va ingliz tili bo‘yicha "
                    "bilimlarini sinovdan o‘tkazib, xorijdagi nufuzli universitetlarga hujjat topshirishda "
                    "katta ustunlikka ega bo‘ladilar."
                ),
                "official_media/classroom-branded.jpg",
                "https://t.me/turonodobilm/497",
                datetime(2026, 11, 4, 6, 46, tzinfo=dt_timezone.utc),
            ),
            (
                "Furqat filialida 100 ga yaqin sertifikat va tashakkurnomalar topshirildi",
                "furqat-100-sertifikat-yutuqlar-etirofi",
                "achievement",
                "O‘quvchilarimiz Milliy sertifikat, maktablararo va xalqaro olimpiadalardagi yuqori natijalari uchun taqdirlandilar.",
                (
                    "Turon Odob-Ilm maktabi Furqat filiali o‘quvchilari Milliy sertifikat imtihonlarida, "
                    "maktablararo olimpiadalarda hamda xalqaro olimpiadalarda yuqori natijalarga erishib, "
                    "faxrli o‘rinlarni egalladilar. G‘olib va faol o‘quvchilarga 100 ga yaqin tashakkurnoma "
                    "hamda sertifikatlar tantanali ravishda topshirildi."
                ),
                "official_media/students-studying.jpg",
                "https://t.me/turonodobilm/596",
                datetime(2026, 11, 7, 5, 55, tzinfo=dt_timezone.utc),
            ),
            (
                "Maktabimizda fanlararo metodik hamkorlik seminari tashkil etildi",
                "fanlararo-metodik-seminar",
                "event",
                "Filiallarimizning rus tili hamda adabiyot fani o‘qituvchilari ishtirokida zamonaviy metodik seminar o‘tkazildi.",
                (
                    "Turon Odob-Ilm maktabi filiallarining rus tili hamda adabiyot fani o‘qituvchilari "
                    "ishtirokida navbatdagi metodik seminar yuqori saviyada tashkil etildi. "
                    "Seminar davomida zamonaviy metodlar, innovatsion yondashuvlar va dars jarayonida "
                    "interfaol usullardan foydalanish masalalari muhokama qilindi."
                ),
                "official_media/classroom-branded.jpg",
                "https://t.me/turonodobilm/641",
                datetime(2026, 11, 7, 14, 13, tzinfo=dt_timezone.utc),
            ),
        ]
        for title, slug, cat, excerpt, body, img_path, src_url, pub_dt in news_items:
            NewsPost.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": cat,
                    "branch": furqat,
                    "excerpt": excerpt,
                    "body": body,
                    "static_image_path": img_path,
                    "source_url": src_url,
                    "published_at": pub_dt,
                    "is_published": True,
                    "is_demo": False,
                },
            )

        # Qabul shartlari va bosqichlari (turonodob-ilm.uz/admissions asosida)
        if not AdmissionStep.objects.exists():
            AdmissionStep.objects.bulk_create([
                AdmissionStep(
                    step_type="condition",
                    title="O‘zbek va rus ta’lim oqimlari",
                    description="1–11-sinflar uchun suhbat va tayyorgarlik darajasini aniqlash asosida qabul qilinadi.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="document",
                    title="Tug‘ilganlik haqida guvohnoma va ota-ona pasporti nusxasi",
                    description="O‘quvchi va ota-ona shaxsini tasdiqlovchi hujjatlar nusxasi.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="document",
                    title="Tibbiy ma’lumotnoma (086-shakl) va 3×4 rasm",
                    description="Maktab shifokori ko‘rigi uchun ma’lumotnoma hamda 4 dona fotosurat.",
                    sort_order=20,
                ),
                AdmissionStep(
                    step_type="step",
                    title="1. Ariza topshirish",
                    description="Onlayn shaklni to‘ldirasiz.",
                    sort_order=10,
                ),
                AdmissionStep(
                    step_type="step",
                    title="2. Bog‘lanish",
                    description="Biz 1–2 ish kunida siz bilan bog‘lanamiz.",
                    sort_order=20,
                ),
                AdmissionStep(
                    step_type="step",
                    title="3. Suhbat",
                    description="Maktabga tashrif va o‘quvchi bilan suhbat.",
                    sort_order=30,
                ),
                AdmissionStep(
                    step_type="step",
                    title="4. Qabul",
                    description="Hujjatlarni rasmiylashtirish va o‘qishni boshlash.",
                    sort_order=40,
                ),
            ])

        # Namunaviy sayt fikri (aniq Demo belgisi bilan)
        if not WebsiteReview.objects.exists():
            r1 = WebsiteReview.objects.create(
                branch=furqat,
                author_name="N. Tursunova (Demo)",
                display_name="N. Tursunova (Demo namuna)",
                rating=5,
                comment=(
                    "[DEMO] Bu sayt interfeysi uchun namunaviy fikr yozuvi. Haqiqiy ota-onalar fikrlari "
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
                "Rasmiy ma'lumotlar, media katalog, IT akademiya va rollar muvaffaqiyatli yuklandi!"
            )
        )
