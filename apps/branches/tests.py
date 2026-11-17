"""Filiallar va xarita redirect xavfsizligi testlari."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.analytics.models import AnalyticsEvent
from apps.branches.models import Branch, MapLink
from apps.branches.validators import validate_allowed_map_url


class MapUrlValidationAndRedirectTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name="Turon Odob-Ilm — Furqat filiali",
            slug="furqat",
            address="Furqat tumani",
            phone="+998901234567",
            is_primary=True,
        )
        self.google_link = MapLink.objects.create(
            branch=self.branch,
            platform="google",
            link_type="profile",
            target_url="https://www.google.com/maps/search/?api=1&query=Turon+Odob+Ilm",
        )
        self.yandex_link = MapLink.objects.create(
            branch=self.branch,
            platform="yandex",
            link_type="directions",
            target_url="https://yandex.uz/maps/?text=Turon+Odob+Ilm",
        )

    def test_valid_google_and_yandex_urls_pass(self):
        self.assertEqual(
            validate_allowed_map_url("https://maps.app.goo.gl/abc123", platform="google"),
            "https://maps.app.goo.gl/abc123",
        )
        self.assertEqual(
            validate_allowed_map_url("https://g.page/r/example", platform="google"),
            "https://g.page/r/example",
        )
        self.assertEqual(
            validate_allowed_map_url("https://yandex.uz/maps/org/12345", platform="yandex"),
            "https://yandex.uz/maps/org/12345",
        )

    def test_open_redirect_and_malicious_urls_rejected(self):
        bad_urls = [
            "http://www.google.com/maps",  # HTTPS emas
            "javascript:alert(1)",
            "https://evil.com/maps.google.com",
            "https://google.com.evil.org/maps",
            "https://google.com@evil.com/phish",
            "https://yandex.uz.attacker.net/maps",
            "//evil.com/redirect",
        ]
        for url in bad_urls:
            with self.assertRaises(ValidationError, msg=f"Bloklanishi kerak edi: {url}"):
                validate_allowed_map_url(url)

    def test_platform_mismatch_rejected(self):
        with self.assertRaises(ValidationError):
            validate_allowed_map_url("https://yandex.uz/maps/", platform="google")
        with self.assertRaises(ValidationError):
            validate_allowed_map_url("https://maps.google.com/", platform="yandex")

    def test_safe_redirect_logs_event_and_ignores_query_next(self):
        url = reverse("branches:map_redirect", kwargs={"slug": self.branch.slug, "link_id": self.google_link.pk})
        response = self.client.get(f"{url}?next=https://evil.com&url=https://evil.com")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.google_link.target_url)
        self.assertIn("no-store", response["Cache-Control"])

        ev = AnalyticsEvent.objects.filter(event_type="map_click", map_link=self.google_link).first()
        self.assertIsNotNone(ev)
        self.assertEqual(ev.platform, "google")
        self.assertEqual(ev.branch, self.branch)
