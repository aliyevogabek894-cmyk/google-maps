"""Xodimlar autentifikatsiya formalari."""
from django import forms


class StaffLoginForm(forms.Form):
    """Boshqaruv paneliga kirish formasi."""

    username = forms.CharField(
        label="Foydalanuvchi nomi",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Loginni kiriting",
                "autocomplete": "username",
                "required": True,
            }
        ),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Parolni kiriting",
                "autocomplete": "current-password",
                "required": True,
            }
        ),
    )
