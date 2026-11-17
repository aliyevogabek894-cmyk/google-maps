# Production Deployment, Xavfsizlik va Zaxira Nusxa (Backup) Yo‘riqnomasi

## 1. PostgreSQL sozlash

Production muhitida SQLite o‘rniga PostgreSQL ishlatiladi:

```sql
CREATE DATABASE turon_odob_ilm;
CREATE USER turon_user WITH PASSWORD 'KUCHLI_TASODIFIY_PAROL';
ALTER ROLE turon_user SET client_encoding TO 'utf8';
ALTER ROLE turon_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE turon_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE turon_odob_ilm TO turon_user;
```

`.env` faylida:
```env
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<kamida-50-belgili-tasodifiy-kalit>
DJANGO_ALLOWED_HOSTS=turon-odob-ilm.uz,www.turon-odob-ilm.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://turon-odob-ilm.uz,https://www.turon-odob-ilm.uz
DATABASE_URL=postgresql://turon_user:KUCHLI_TASODIFIY_PAROL@127.0.0.1:5432/turon_odob_ilm
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## 2. Statik fayllar va Gunicorn

```bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

## 3. HTTPS (Nginx + Certbot)

Nginx `X-Forwarded-Proto https` sarlavhasini uzatishi, `media/` va `staticfiles/` ni to‘g‘ridan-to‘g‘ri xizmat qilishi hamda TLS 1.2/1.3 sertifikatlari bilan ishlashi tavsiya etiladi.

## 4. Kunlik zaxira nusxa (Backup) va tiklash

### PostgreSQL zaxira nusxasi (`pg_dump`)
```bash
pg_dump -Fc -U turon_user -h 127.0.0.1 turon_odob_ilm > /backups/turon_$(date +%F).dump
```

### Tiklash (`pg_restore`)
```bash
pg_restore -U turon_user -h 127.0.0.1 -d turon_odob_ilm --clean --if-exists /backups/turon_2026-11-17.dump
```

### Media fayllar zaxirasi
`media/` papkasini ham kunlik arxivlang (`tar -czf media_$(date +%F).tar.gz media/`).

## 5. Loglar va Monitoring

- Ilova va xavfsizlik loglari `logs/turon.log` faylida rotatsiya bilan (`5 MB × 5 fayl`) yuritiladi.
- Barcha muhim xodim amallari (`review_approved`, `map_link_updated`, `report_exported` va h.k.) `AdminAuditLog` jadvalida saqlanadi.
- Superadmin va moderatorlar uchun kuchli parol (kamida 10 ta belgi) va TOTP 2FA qo‘llash tavsiya etiladi.
