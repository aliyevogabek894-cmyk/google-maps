"""Dashboard, rollar, qo'lda import, eksport (XLSX/CSV) va login rate-limit testlari."""
import io

import openpyxl
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import ROLE_MODERATOR, ROLE_SUPERADMIN
from apps.accounts.services import ensure_default_roles
from apps.analytics.models import AnalyticsEvent, PlatformStatSnapshot
from apps.branches.models import Branch


class ReportsDashboardAndSecurityTests(TestCase):
    def setUp(self):
        ensure_default_roles()
        self.branch = Branch.objects.create(
            name="Furqat filiali",
            slug="furqat",
            address="Furqat",
            phone="+998901234567",
            is_primary=True,
        )
        self.superadmin = User.objects.create_user(username="super1", password="VeryStrongPassword123!")
        self.superadmin.groups.add(Group.objects.get(name=ROLE_SUPERADMIN))

        self.moderator = User.objects.create_user(username="mod_only", password="VeryStrongPassword123!")
        self.moderator.groups.add(Group.objects.get(name=ROLE_MODERATOR))

    def test_dashboard_requires_login_and_enforces_roles(self):
        res_anon = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(res_anon.status_code, 302)

        self.client.force_login(self.moderator)
        self.assertEqual(self.client.get(reverse("reports:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("reports:branches")).status_code, 403)
        self.assertEqual(self.client.get(reverse("reports:audit")).status_code, 403)

    def test_xlsx_and_csv_export_with_formula_injection_protection(self):
        AnalyticsEvent.objects.create(
            event_type="cta_click",
            branch=self.branch,
            platform="website",
            cta_label="=CMD|' /C calc'!A0",
            page_path="/",
            referrer_domain="direct",
            device_type="desktop",
            anonymous_session_id="sess12345",
        )
        self.client.force_login(self.superadmin)

        xlsx_res = self.client.get(reverse("reports:export_xlsx"))
        self.assertEqual(xlsx_res.status_code, 200)
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_res.content))
        self.assertIn("Umumiy ko'rsatkichlar", wb.sheetnames)
        self.assertIn("Rasmiy platforma statistikasi", wb.sheetnames)
        ws5 = wb["Sayt hodisalari"]
        self.assertEqual(ws5.cell(row=2, column=5).value, "'=CMD|' /C calc'!A0")

        csv_res = self.client.get(reverse("reports:export_csv"))
        self.assertEqual(csv_res.status_code, 200)
        csv_text = csv_res.content.decode("utf-8-sig")
        self.assertIn("'=CMD|' /C calc'!A0", csv_text)

    def test_manual_and_csv_platform_stats_import(self):
        self.client.force_login(self.superadmin)
        csv_bytes = (
            "period_start,period_end,impressions,profile_views,direction_clicks,call_clicks,website_clicks,average_rating,review_count,notes\n"
            "2026-10-01,2026-10-31,1240,510,82,34,120,4.8,19,Oktyabr oyi kabinet eksporti\n"
        ).encode("utf-8")
        upload = SimpleUploadedFile("google_stats.csv", csv_bytes, content_type="text/csv")

        res = self.client.post(
            reverse("reports:platform_metrics"),
            data={
                "import_mode": "csv",
                "branch": self.branch.pk,
                "platform": "google",
                "source_label": "Google Business Profile CSV",
                "csv_file": upload,
            },
        )
        self.assertEqual(res.status_code, 302)
        snap = PlatformStatSnapshot.objects.get(branch=self.branch, platform="google")
        self.assertEqual(snap.impressions, 1240)
        self.assertEqual(snap.source_type, "manual_csv")

    def test_staff_login_rate_limit(self):
        login_url = reverse("accounts:login")
        for _ in range(5):
            r = self.client.post(login_url, {"username": "super1", "password": "wrong"})
            self.assertEqual(r.status_code, 200)
        r_blocked = self.client.post(login_url, {"username": "super1", "password": "wrong"})
        self.assertEqual(r_blocked.status_code, 429)
