"""Ota-onalar fikrlari, maxfiylik roziligi, telefonni yashirish va moderatsiya testlari."""
import time

from django.contrib.auth.models import User
from django.core.signing import TimestampSigner
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import ROLE_EDITOR, ROLE_MODERATOR, AdminAuditLog
from apps.accounts.services import ensure_default_roles
from apps.branches.models import Branch, MapLink
from apps.reviews.models import ReviewConsent, WebsiteReview


def _valid_ts_token():
    signer = TimestampSigner(salt="turon-form-guard")
    return signer.sign(str(int(time.time()) - 5))


class ReviewsFlowAndPrivacyTests(TestCase):
    def setUp(self):
        ensure_default_roles()
        self.branch = Branch.objects.create(
            name="Furqat filiali",
            slug="furqat",
            address="Furqat tumani",
            phone="+998900001122",
            is_primary=True,
        )
        self.google_review_link = MapLink.objects.create(
            branch=self.branch,
            platform="google",
            link_type="review",
            label="Google’da fikr qoldirish",
            target_url="https://www.google.com/maps/search/?api=1&query=Turon+Odob+Ilm",
        )
        self.yandex_review_link = MapLink.objects.create(
            branch=self.branch,
            platform="yandex",
            link_type="review",
            label="Yandex’da fikr qoldirish",
            target_url="https://yandex.uz/maps/?text=Turon+Odob+Ilm",
        )

    def test_review_submission_saves_pending_and_consent_and_hides_phone(self):
        secret_phone = "+998998887766"
        response = self.client.post(
            reverse("reviews:list"),
            data={
                "branch": self.branch.pk,
                "author_name": "Dilshodbek",
                "display_name": "D. Rahimov",
                "phone": secret_phone,
                "rating": 4,
                "comment": "O'qituvchilar e'tibori va dars sifati yaxshi, transport jadvalini kengaytirishni taklif qilaman.",
                "accepted_privacy_policy": "on",
                "website_url": "",
                "form_ts": _valid_ts_token(),
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        review = WebsiteReview.objects.get(author_name="Dilshodbek")
        self.assertEqual(review.status, "pending")
        self.assertTrue(ReviewConsent.objects.filter(review=review, accepted_privacy_policy=True).exists())

        # Moderatsiyadan oldin ommaviy sahifada chiqmaydi
        public_html = self.client.get(reverse("reviews:list")).content.decode("utf-8")
        self.assertNotIn("D. Rahimov", public_html)
        self.assertNotIn(secret_phone, public_html)

        # Tasdiqlangandan keyin ko'rinadi, lekin telefon RAQAMI HECH QACHON chiqmaydi!
        review.status = "approved"
        review.save()
        public_html_after = self.client.get(reverse("reviews:list")).content.decode("utf-8")
        self.assertIn("D. Rahimov", public_html_after)
        self.assertNotIn(secret_phone, public_html_after)

        # Har ikkala rasmiy xarita sharh tugmasi doim teng ko'rsatiladi (review gating yo'q)
        self.assertIn("Google’da fikr qoldirish", public_html_after)
        self.assertIn("Yandex’da fikr qoldirish", public_html_after)

    def test_honeypot_blocks_spam_review(self):
        self.client.post(
            reverse("reviews:list"),
            data={
                "branch": self.branch.pk,
                "author_name": "Bot",
                "rating": 5,
                "comment": "Bu avtomatik spam izoh matni hisoblanadi.",
                "accepted_privacy_policy": "on",
                "website_url": "https://spam.example.com",
                "form_ts": _valid_ts_token(),
            },
        )
        self.assertEqual(WebsiteReview.objects.count(), 0)

    def test_moderator_can_approve_and_editor_cannot(self):
        from django.contrib.auth.models import Group

        review = WebsiteReview.objects.create(
            branch=self.branch,
            author_name="Ota-ona",
            rating=2,
            comment="Tanqidiy, lekin asosli va xolis taklif matni.",
            status="pending",
        )
        editor = User.objects.create_user(username="muharrir1", password="StrongPassword123!")
        editor.groups.add(Group.objects.get(name=ROLE_EDITOR))
        self.client.force_login(editor)
        res_editor = self.client.get(reverse("reports:moderation"))
        self.assertEqual(res_editor.status_code, 403)

        moderator = User.objects.create_user(username="mod1", password="StrongPassword123!")
        moderator.groups.add(Group.objects.get(name=ROLE_MODERATOR))
        self.client.force_login(moderator)
        res_mod = self.client.post(
            reverse("reports:moderation"),
            data={
                "review_id": review.pk,
                "decision": "approved",
                "admin_reply": "Taklifingiz uchun rahmat, ko'rib chiqamiz.",
                "moderation_note": "Siyosatga mos.",
            },
        )
        self.assertEqual(res_mod.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.status, "approved")
        self.assertEqual(review.moderated_by, moderator)
        self.assertTrue(AdminAuditLog.objects.filter(action="review_approved", target_id=str(review.pk)).exists())
