# Turon Odob-Ilm — Raqamli Maktab Platformasi

**Turon Odob-Ilm xususiy maktabi** (boshlang‘ich filial: **Furqat filiali**) uchun yaratilgan, mobil qurilmalarga mos rasmiy veb-platforma, Google Maps / Yandex Maps integratsiyasi, ota-onalar fikrlari tizimi va administrator monitoring paneli.

## Asosiy imkoniyatlar

- **Ommaviy veb-sayt (o‘zbek lotin yozuvida):**
  - Bosh sahifa (`/`) — asosiy CTA tugmalar (*Qabulga ariza*, *Xaritada ko‘rish*, *Biz bilan bog‘lanish*), Furqat filiali tezkor xarita kartasi.
  - Maktab haqida (`/maktab-haqida/`) — tarix, qadriyatlar, infratuzilma, o‘qituvchilar va rasmiy hujjatlar.
  - Ta’lim va xizmatlar (`/talim/`) — sinflar, fanlar, to‘garaklar, kun tartibi, ovqatlanish va transport.
  - Yangiliklar va tadbirlar (`/yangiliklar/`) hamda Galereya (`/galereya/`).
  - Qabul (`/qabul/`) — shartlar, kerakli hujjatlar va himoyalangan onlayn ariza formasi.
  - Filiallar (`/filiallar/`) — `Branch` va `MapLink` modellari orqali ko‘p filialli kengayish imkoniyati.
- **Google Maps va Yandex Maps xavfsiz integratsiyasi:**
  - Barcha xarita havolalari admin paneldan boshqariladi (kodga qattiq yozilmaydi).
  - Xarita tugmasi bosilganda `AnalyticsEvent` yoziladi va foydalanuvchi faqat admin tasdiqlagan ruxsat etilgan HTTPS Google/Yandex domenlariga yo‘naltiriladi (open-redirect himoyasi).
- **Halol va shaffof ota-onalar fikrlari (`/fikrlar/`):**
  - Sayt ichidagi fikrlar moderatsiyadan so‘ng chiqariladi; rozilik (`ReviewConsent`) saqlanadi; telefon raqamlari hech qachon ommaga ko‘rsatilmaydi.
  - Google/Yandex sharhlari uchun barcha foydalanuvchilarga neytral va bir xil rasmiy havola beriladi (soxta sharh yoki bahoga qarab filtrlash yo‘q).
- **Monitoring Dashboard va Eksport (`/boshqaruv/`):**
  - Tashriflar, sahifa ko‘rishlari, saytdagi Google/Yandex tugma bosishlari, sayt fikrlari va sana/filial filtrlari.
  - **Muhim ajratish:** Saytdagi tugma bosishlari rasmiy Google/Yandex qidiruv ko‘rsatkichlaridan alohida ko‘rsatiladi. Rasmiy platforma ko‘rsatkichlari uchun `GoogleBusinessAdapter`, `YandexBusinessAdapter` va qo‘lda CSV/forma importi (`/boshqaruv/platforma-statistikasi/`) tayyorlangan.
  - **Eksport:** XLSX (`openpyxl`), CSV (formula injection himoyasi bilan) va chop etish (PDF) hisobotlari.
  - **Xavfsizlik:** CSRF/XSS himoyasi, rate limiting, honeypot va vaqt tekshiruvi, rolga asoslangan kirish (`Superadmin`, `Muharrir`, `Fikr moderatori`), `AdminAuditLog`.

## Tezkor ishga tushirish (Lokal muhit)

1. Muhit o‘zgaruvchilarini sozlang:
   ```bash
   copy .env.example .env
   ```
   *(Lokal ishlab chiqishda `DATABASE_URL` bo‘sh qolsa SQLite `db.sqlite3` ishlatiladi; production uchun PostgreSQL `DATABASE_URL` kiriting.)*

2. Kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

3. Migratsiyalarni yarating va qo‘llang:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Boshlang‘ich rollar va aniq `[DEMO]` belgili ma’lumotlarni yuklang:
   ```bash
   python manage.py seed_demo
   ```

5. Superadmin yarating:
   ```bash
   python manage.py createsuperuser
   ```

6. Testlarni ishga tushiring va serverni ko‘taring:
   ```bash
   python manage.py test
   python manage.py runserver
   ```

## Tekin serverga (Render) deploy qilish

Repozitoriy ildizida `render.yaml`, `build.sh` va `.python-version` fayllari tayyorlangan:
1. [Render Dashboard](https://dashboard.render.com/) ga GitHub akkauntingiz bilan kiring.
2. **New + -> Blueprint** bo‘limini tanlab `aliyevogabek894-cmyk/google-maps` repozitoriysini ulang (yoki to‘g‘ridan-to‘g‘ri havola: `https://render.com/deploy?repo=https://github.com/aliyevogabek894-cmyk/google-maps`).
3. So‘ralganda admin uchun `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` va `DJANGO_SUPERUSER_PASSWORD` qiymatlarini kiriting va **Apply / Deploy** tugmasini bosing.
4. Eslatma: Render’ning bepul PostgreSQL bazasi 30 kundan so‘ng tugaydi (doimiy bepul baza uchun Neon/Supabase PostgreSQL ulash mumkin), bepul Web Service esa faolsizlikdan keyin ~30–50 soniyada uyg‘onadi.

## Ishga tushirishdan oldingi tekshiruv ro‘yxati

1. Google Business Profile’da (`https://business.google.com/`) `FPGX+82H, A-376, Chirkay` manzili aynan Furqat filiali ekanligini tasdiqlang, dublikat yaratmang.
2. Yandex Business’da (`https://business.yandex.com/`) Furqat filialini tekshiring yoki rasmiy egalikni tasdiqlang.
3. Tasdiqlangan to‘g‘ridan-to‘g‘ri xarita va sharh yozish URL’larini `/boshqaruv/filiallar/` orqali kiriting.
4. Haqiqiy maktab logotipi, telefon raqamlari, fotosuratlari va matnlarini kiritgach, `SiteSettings` ichida **Demo kontent belgisi (`is_demo_mode`)** ni o‘chiring.

Batafsil arxitektura: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
Zaxira nusxa va production yo‘riqnomasi: [docs/BACKUP_AND_DEPLOY.md](docs/BACKUP_AND_DEPLOY.md)
