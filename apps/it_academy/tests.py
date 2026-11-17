"""IT Akademiya bo'limi, IT domlasi, IT WORLD o'yin metodikasi va kurslar testlari."""
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.it_academy.models import GameModule, ITCourse, ITProject


class ItAcademyTests(TestCase):
    def test_it_academy_page_renders_with_teacher_games_and_lab(self):
        call_command("seed_demo")
        self.assertGreaterEqual(ITCourse.objects.count(), 3)
        self.assertGreaterEqual(ITProject.objects.count(), 1)
        self.assertGreaterEqual(GameModule.objects.count(), 8)

        res = self.client.get(reverse("it_academy:index"))
        self.assertEqual(res.status_code, 200)
        html = res.content.decode("utf-8")
        self.assertIn("IT Akademiyasi", html)
        self.assertIn("Aliyev Og‘abek", html)
        self.assertIn("teacher-aliyev.jpg", html)
        self.assertIn("aliyev-turon.netlify.app", html)
        self.assertIn("it-lab-active.jpg", html)
