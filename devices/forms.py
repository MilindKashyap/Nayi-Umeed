from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["title", "description", "category", "condition", "price"]


class DeviceStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["status"]

