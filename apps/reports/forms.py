"""Boshqaruv paneli formalari: sana filtri, platforma importi, filial va moderatsiya."""
from django import forms

from apps.analytics.models import PlatformStatSnapshot
from apps.branches.models import Branch, MapLink
from apps.core.models import SiteSettings


class PlatformStatManualForm(forms.ModelForm):
    """Google Business yoki Yandex Business rasmiy ko'rsatkichlarini qo'lda kiritish formasi."""

    class Meta:
        model = PlatformStatSnapshot
        fields = [
            "branch",
            "platform",
            "source_label",
            "period_start",
            "period_end",
            "impressions",
            "profile_views",
            "direction_clicks",
            "call_clicks",
            "website_clicks",
            "average_rating",
            "review_count",
            "notes",
        ]
        widgets = {
            "branch": forms.Select(attrs={"class": "form-select"}),
            "platform": forms.Select(attrs={"class": "form-select"}),
            "source_label": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Masalan: Google Business Profile kabineti (qo‘lda)"}
            ),
            "period_start": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "period_end": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "impressions": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "profile_views": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "direction_clicks": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "call_clicks": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "website_clicks": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "average_rating": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "1", "max": "5"}),
            "review_count": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "notes": forms.Textarea(attrs={"class": "form-textarea", "rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("period_start")
        end = cleaned.get("period_end")
        if start and end and start > end:
            raise forms.ValidationError("Davr boshlanish sanasi tugash sanasidan katta bo'lishi mumkin emas.")
        return cleaned


class PlatformStatCSVUploadForm(forms.Form):
    """Rasmiy kabinet eksport qilingan CSV faylini yuklash formasi."""

    branch = forms.ModelChoiceField(
        label="Filial",
        queryset=Branch.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    platform = forms.ChoiceField(
        label="Platforma",
        choices=PlatformStatSnapshot.PLATFORM_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    source_label = forms.CharField(
        label="Manba tavsifi",
        max_length=180,
        initial="Kabinet CSV eksporti",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    csv_file = forms.FileField(
        label="CSV fayl",
        widget=forms.FileInput(attrs={"class": "form-input", "accept": ".csv,text/csv"}),
    )


class BranchManageForm(forms.ModelForm):
    """Filial ma'lumotlari va tasdiqlash holatini boshqarish formasi."""

    class Meta:
        model = Branch
        fields = [
            "name",
            "slug",
            "city_or_district",
            "address",
            "landmark",
            "phone",
            "secondary_phone",
            "email",
            "working_hours",
            "latitude",
            "longitude",
            "google_verification_status",
            "yandex_verification_status",
            "verification_note",
            "description",
            "is_primary",
            "is_active",
            "is_demo",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "slug": forms.TextInput(attrs={"class": "form-input"}),
            "city_or_district": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.TextInput(attrs={"class": "form-input"}),
            "landmark": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "secondary_phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "working_hours": forms.TextInput(attrs={"class": "form-input"}),
            "latitude": forms.NumberInput(attrs={"class": "form-input", "step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-input", "step": "0.000001"}),
            "google_verification_status": forms.Select(attrs={"class": "form-select"}),
            "yandex_verification_status": forms.Select(attrs={"class": "form-select"}),
            "verification_note": forms.Textarea(attrs={"class": "form-textarea", "rows": 2}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 2}),
        }


class MapLinkManageForm(forms.ModelForm):
    """Xarita havolalarini boshqarish formasi (qat'iy HTTPS domen tekshiruvi bilan)."""

    class Meta:
        model = MapLink
        fields = [
            "branch",
            "platform",
            "link_type",
            "label",
            "target_url",
            "is_verified_profile",
            "is_active",
            "sort_order",
        ]
        widgets = {
            "branch": forms.Select(attrs={"class": "form-select"}),
            "platform": forms.Select(attrs={"class": "form-select"}),
            "link_type": forms.Select(attrs={"class": "form-select"}),
            "label": forms.TextInput(attrs={"class": "form-input", "placeholder": "Masalan: Google Maps’da ko‘rish"}),
            "target_url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://..."}),
            "sort_order": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
        }


class SiteQuickSettingsForm(forms.ModelForm):
    """Saytning asosiy kontakt va demo holati sozlamalari."""

    class Meta:
        model = SiteSettings
        fields = [
            "school_name",
            "tagline",
            "primary_phone",
            "email",
            "telegram_url",
            "instagram_url",
            "is_demo_mode",
        ]
        widgets = {
            "school_name": forms.TextInput(attrs={"class": "form-input"}),
            "tagline": forms.TextInput(attrs={"class": "form-input"}),
            "primary_phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "telegram_url": forms.URLInput(attrs={"class": "form-input"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-input"}),
        }
