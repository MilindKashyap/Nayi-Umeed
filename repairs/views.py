from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse

from accounts.models import Roles
from accounts.utils import role_required

from .models import RepairAssignment, RepairStatus


class RepairUpdateForm(forms.ModelForm):
    class Meta:
        model = RepairAssignment
        fields = ["status", "estimated_completion", "report_file", "report_notes", "is_certified"]
        widgets = {
            "estimated_completion": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


@login_required
@role_required([Roles.REPAIR_PARTNER, Roles.ADMIN])
def assigned_list(request: HttpRequest) -> HttpResponse:
    assignments = RepairAssignment.objects.select_related("device").filter(repair_partner=request.user)
    return render(request, "repairs/assigned_list.html", {"assignments": assignments})


@login_required
@role_required([Roles.REPAIR_PARTNER, Roles.ADMIN])
def assignment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    assignment = get_object_or_404(
        RepairAssignment.objects.select_related("device"), pk=pk, repair_partner=request.user
    )
    if request.method == "POST":
        form = RepairUpdateForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            if assignment.is_certified:
                assignment.mark_certified()
                messages.success(request, "Repair certified and device lifecycle updated where applicable.")
            else:
                messages.success(request, "Repair assignment updated.")
            return redirect("repairs:assignment_detail", pk=assignment.pk)
    else:
        form = RepairUpdateForm(instance=assignment)
    return render(request, "repairs/assignment_detail.html", {"assignment": assignment, "form": form})


