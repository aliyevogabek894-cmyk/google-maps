"""Maxfiylikka mos analitika, bot filtri va rasmiy API adapter testlari."""
import json

from django.test import TestCase
from django.urls import reverse

from apps.analytics.adapters import GoogleBusinessAdapter, YandexBusinessAdapter
from apps.analytics.models import AnalyticsEvent, PlatformStatSnapshot
from apps.branches.models import Branch


class AnalyticsAndAdaptersTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name="Furqat filiali",
            slug="furqat",
            address="Furqat",
            phone="+998901234567",
            is_primary=True,
        )

    def test_page_view_middleware_tracks_human_and_ignores_bots_and_admin(self):
        self.client.get(reverse("core:home"), HTTP_USER_AGENT="Mozilla/5.0 (Linux; Android 13; Mobile)")
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="page_view").count(), 1)
        ev = AnalyticsEvent.objects.first()
        self.assertEqual(ev.device_type, "mobile")
        self.assertEqual(len(ev.anonymous_session_id), 32)

        # Bot so'rovi hisobga olinmaydi
        self.client.get(reverse("core:about"), HTTP_USER_AGENT="Googlebot/2.1 (+http://www.google.com/bot.html)")
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="page_view").count(), 1)

        # Login sahifasi (/boshqaruv/) hisobga olinmaydi
        self.client.get(reverse("accounts:login"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="page_view").count(), 1)

    def test_cta_tracking_endpoint(self):
        res = self.client.post(
            reverse("analytics:track_cta"),
            data=json.dumps({"cta_label": "Hero: Qabulga ariza", "branch_id": self.branch.pk, "page_path": "/"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="cta_click", cta_label="Hero: Qabulga ariza").count(), 1)

    def test_adapters_report_not_configured_without_fabricating_numbers(self):
        g_res = GoogleBusinessAdapter().get_status()
        y_res = YandexBusinessAdapter().get_status()
        self.assertFalse(g_res.is_configured)
        self.assertEqual(g_res.status_code, "not_configured")
        self.assertFalse(y_res.is_configured)
        self.assertEqual(y_res.status_code, "not_configured")
        self.assertEqual(PlatformStatSnapshot.objects.count(), 0)
