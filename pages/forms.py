from django import forms


class ContactForm(forms.Form):
    """Contact form for users to send messages"""
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your full name",
            "required": True,
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "your.email@example.com",
            "required": True,
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+91 123 456 7890",
        })
    )
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "What is this regarding?",
            "required": True,
        })
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Tell us more about your inquiry...",
            "rows": 6,
            "required": True,
        })
    )
