from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User, Roles


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(choices=Roles.choices, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone_number", "role")


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, label="Verification Code")

