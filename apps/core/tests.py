"""Asosiy ommaviy sahifalar, SEO, formalar va seed_demo buyrug'i testlari."""
import time

from django.core.management import call_command
from django.core.signing import TimestampSigner
from django.test import TestCase
from django.urls import reverse

from apps.branches.models import Branch
from apps.content.models import AdmissionApplication
from apps.core.models import ContactMessage


def _valid_ts():
    return TimestampSigner(salt="turon-form-guard").sign(str(int(time.time()) - 5))


class CorePublicAndSeoTests(TestCase):
    def test_seed_demo_and_public_pages_render_in_uzbek(self):
        call_command("seed_demo")
        call_command("seed_demo")  # Idempotentligini tekshirish
        self.assertEqual(Branch.objects.filter(slug="furqat").count(), 1)

        urls = [
            reverse("core:home"),
            reverse("core:about"),
            reverse("it_academy:index"),
            reverse("content:education"),
            reverse("content:news_list"),
            reverse("content:gallery"),
            reverse("content:admission"),
            reverse("branches:list"),
            reverse("branches:detail", kwargs={"slug": "furqat"}),
            reverse("reviews:list"),
            reverse("core:contact"),
            reverse("core:privacy"),
            reverse("sitemap"),
            reverse("core:robots_txt"),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, msg=f"Sahifa xato qaytardi: {url}")

        # Eski turonodob-ilm.uz SEO yo'llari 301 bilan yo'naltirilishi
        self.assertEqual(self.client.get("/about").status_code, 301)
        self.assertEqual(self.client.get("/admissions").status_code, 301)
        self.assertEqual(self.client.get("/contact").status_code, 301)

        home_html = self.client.get(reverse("core:home")).content.decode("utf-8")
        self.assertIn("Bilim, odob va kelajak", home_html)
        self.assertIn("Qabul haqida ma’lumot", home_html)
        self.assertIn("Xaritada ko‘rish", home_html)
        self.assertIn("facade.jpg", home_html)
        self.assertIn("it-lab-active.jpg", home_html)
        self.assertIn("youtube-nocookie.com/embed/", home_html)
        self.assertIn("038782", home_html)
        self.assertIn("Demo", home_html)
        # Mobil moslashuv elementlari
        self.assertIn("viewport-fit=cover", home_html)
        self.assertIn("mobile-action-dock", home_html)
        self.assertIn("subjects-grid", home_html)
        self.assertIn("leader-inline-card", home_html)
        self.assertIn("mobile-swipe-hint", home_html)

        robots = self.client.get(reverse("core:robots_txt")).content.decode("utf-8")
        self.assertIn("Disallow: /boshqaruv/", robots)
        self.assertIn("Sitemap:", robots)

        health = self.client.get(reverse("core:healthz"))
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.content, b"ok")

    def test_admission_and_contact_forms(self):
        call_command("seed_demo")
        furqat = Branch.objects.get(slug="furqat")

        res_adm = self.client.post(
            reverse("content:admission"),
            data={
                "parent_name": "Aziza Karimova",
                "phone": "+998901112233",
                "student_name": "Bilol Karimov",
                "grade_level": "1-sinf",
                "branch": furqat.pk,
                "notes": "Ingliz tili sinfiga qiziqamiz.",
                "accepted_privacy_policy": "on",
                "website_url": "",
                "form_ts": _valid_ts(),
            },
        )
        self.assertEqual(res_adm.status_code, 302)
        self.assertEqual(AdmissionApplication.objects.count(), 1)

        res_contact = self.client.post(
            reverse("core:contact"),
            data={
                "full_name": "Sardor Alimov",
                "phone": "+998914445566",
                "email": "",
                "branch": furqat.pk,
                "subject": "Transport haqida savol",
                "message": "Furqat tumani markazidan maktab avtobusi qatnaydimi?",
                "accepted_privacy_policy": "on",
                "website_url": "",
                "form_ts": _valid_ts(),
            },
        )
        self.assertEqual(res_contact.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
