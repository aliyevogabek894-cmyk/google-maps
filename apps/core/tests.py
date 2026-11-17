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

        home_html = self.client.get(reverse("core:home")).content.decode("utf-8")
        self.assertIn("Qabulga ariza", home_html)
        self.assertIn("Xaritada ko‘rish", home_html)
        self.assertIn("Biz bilan bog‘lanish", home_html)
        self.assertIn("Demo", home_html)

        robots = self.client.get(reverse("core:robots_txt")).content.decode("utf-8")
        self.assertIn("Disallow: /boshqaruv/", robots)
        self.assertIn("Sitemap:", robots)

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
