"""Ota-onalar fikr yuborish formasi."""
from django import forms

from apps.branches.models import Branch
from apps.core.security import generate_form_timestamp_token, verify_form_anti_spam
from .models import WebsiteReview


class WebsiteReviewForm(forms.ModelForm):
    """Neytral va xavfsiz sayt ichidagi fikr qoldirish formasi."""

    RATING_CHOICES = [
        (5, "5 — A’lo"),
        (4, "4 — Yaxshi"),
        (3, "3 — Qoniqarli"),
        (2, "2 — Kamchiliklar bor"),
        (1, "1 — Qoniqarsiz"),
    ]

    rating = forms.TypedChoiceField(
        label="Baho (1 dan 5 gacha)",
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect(attrs={"class": "rating-radio"}),
    )
    accepted_privacy_policy = forms.BooleanField(
        label="Fikrimni saytda moderatsiyadan so‘ng e’lon qilishga va maxfiylik siyosati shartlariga roziman",
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    website_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    form_ts = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = WebsiteReview
        fields = ["branch", "author_name", "display_name", "phone", "rating", "comment"]
        widgets = {
            "branch": forms.Select(attrs={"class": "form-select"}),
            "author_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ismingiz"}),
            "display_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ixtiyoriy: saytda ko‘rinadigan taxallus (masalan, A. Karimov)"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Ixtiyoriy: +998 90 ... (saytda ko‘rinmaydi)"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Maktab haqidagi xolis fikr va takliflaringizni yozing...",
                }
            ),
        }
        labels = {
            "branch": "Filial",
            "author_name": "Ismingiz",
            "display_name": "Saytda ko‘rinadigan ism / taxallus (ixtiyoriy)",
            "phone": "Aloqa telefoni (ixtiyoriy, ommaga chiqmaydi)",
            "comment": "Fikr matni",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_branches = Branch.objects.filter(is_active=True).order_by("-is_primary", "name")
        self.fields["branch"].queryset = active_branches
        self.fields["branch"].empty_label = None
        if active_branches.exists() and not self.is_bound:
            self.fields["branch"].initial = active_branches.first()
        if not self.is_bound:
            self.fields["form_ts"].initial = generate_form_timestamp_token()

    def clean_comment(self):
        comment = (self.cleaned_data.get("comment") or "").strip()
        if len(comment) < 10:
            raise forms.ValidationError("Iltimos, kamida 10 ta belgidan iborat mazmunli fikr yozing.")
        return comment

    def clean(self):
        cleaned = super().clean()
        spam_error = verify_form_anti_spam(
            cleaned.get("website_url", ""),
            cleaned.get("form_ts", ""),
        )
        if spam_error:
            raise forms.ValidationError(spam_error)
        return cleaned
