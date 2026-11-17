"""IT Akademiya bo'limi, kurslar va ruxsat metama'lumotlari testlari."""
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.it_academy.models import ITCourse, ITProject


class ItAcademyTests(TestCase):
    def test_it_academy_page_renders_with_courses_and_lab(self):
        call_command("seed_demo")
        self.assertGreaterEqual(ITCourse.objects.count(), 3)
        self.assertGreaterEqual(ITProject.objects.count(), 1)

        res = self.client.get(reverse("it_academy:index"))
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        self.assertIn("IT Akademiyasi", html)
        self.assertIn("it-lab-active.jpg", html)
