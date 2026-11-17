"""Qabul arizasi formasi."""
from django import forms

from apps.branches.models import Branch
from apps.core.security import generate_form_timestamp_token, verify_form_anti_spam
from .models import AdmissionApplication


class AdmissionApplicationForm(forms.ModelForm):
    """Qabulga ariza yuborish formasi (spam himoyasi va maxfiylik roziligi bilan)."""

    website_url = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}))
    form_ts = forms.CharField(required=False, widget=forms.HiddenInput())

    GRADE_CHOICES = [
        ("Tayyorlov guruhi", "Tayyorlov guruhi (6 yosh)"),
        ("1-sinf", "1-sinf"),
        ("2-sinf", "2-sinf"),
        ("3-sinf", "3-sinf"),
        ("4-sinf", "4-sinf"),
        ("5-sinf", "5-sinf"),
        ("6-sinf", "6-sinf"),
        ("7-sinf", "7-sinf"),
        ("8-sinf", "8-sinf"),
        ("9-sinf", "9-sinf"),
        ("10-sinf", "10-sinf"),
        ("11-sinf", "11-sinf"),
    ]

    grade_level = forms.ChoiceField(
        label="Qaysi sinfga",
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = AdmissionApplication
        fields = [
            "parent_name",
            "phone",
            "student_name",
            "grade_level",
            "branch",
            "notes",
            "accepted_privacy_policy",
        ]
        widgets = {
            "parent_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ota-ona ismi va familiyasi"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+998 90 123 45 67"}),
            "student_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Farzandingizning F.I.Sh."}),
            "branch": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 3, "placeholder": "Ixtiyoriy: savol yoki qo‘shimcha ma’lumot"}
            ),
            "accepted_privacy_policy": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
        labels = {
            "parent_name": "Ota-ona F.I.Sh.",
            "phone": "Aloqa telefoni",
            "student_name": "O‘quvchi F.I.Sh.",
            "branch": "Filial",
            "notes": "Qo‘shimcha izoh (ixtiyoriy)",
            "accepted_privacy_policy": "Shaxsiy ma’lumotlarni qayta ishlash va maxfiylik siyosatiga roziman",
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

    def clean_accepted_privacy_policy(self):
        accepted = self.cleaned_data.get("accepted_privacy_policy")
        if not accepted:
            raise forms.ValidationError("Ariza yuborish uchun maxfiylik siyosatiga rozilik bildirishingiz shart.")
        return accepted

    def clean(self):
        cleaned = super().clean()
        spam_error = verify_form_anti_spam(
            cleaned.get("website_url", ""),
            cleaned.get("form_ts", ""),
        )
        if spam_error:
            raise forms.ValidationError(spam_error)
        return cleaned
