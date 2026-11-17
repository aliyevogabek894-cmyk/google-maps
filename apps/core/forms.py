"""Asosiy sayt formalari (spam himoyasi va rozilik bilan)."""
from django import forms

from apps.branches.models import Branch
from .models import ContactMessage
from .security import generate_form_timestamp_token, verify_form_anti_spam


class ContactMessageForm(forms.ModelForm):
    """Aloqa sahifasi murojaat formasi."""

    website_url = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}))
    form_ts = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ["full_name", "phone", "email", "branch", "subject", "message", "accepted_privacy_policy"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ism va familiyangiz"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+998 90 123 45 67"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "Ixtiyoriy: email@namuna.uz"}),
            "branch": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(attrs={"class": "form-input", "placeholder": "Murojaat mavzusi"}),
            "message": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 4, "placeholder": "Savol yoki murojaatingizni yozing..."}
            ),
            "accepted_privacy_policy": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
        labels = {
            "full_name": "Ismingiz",
            "phone": "Telefon raqamingiz",
            "email": "Elektron pochta (ixtiyoriy)",
            "branch": "Filial",
            "subject": "Mavzu",
            "message": "Murojaat matni",
            "accepted_privacy_policy": "Maxfiylik siyosati shartlariga roziman",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["branch"].queryset = Branch.objects.filter(is_active=True)
        self.fields["branch"].required = False
        self.fields["branch"].empty_label = "Umumiy / Barcha filiallar"
        if not self.is_bound:
            self.fields["form_ts"].initial = generate_form_timestamp_token()

    def clean_accepted_privacy_policy(self):
        accepted = self.cleaned_data.get("accepted_privacy_policy")
        if not accepted:
            raise forms.ValidationError("Murojaat yuborish uchun maxfiylik siyosatiga rozilik bildirishingiz kerak.")
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
