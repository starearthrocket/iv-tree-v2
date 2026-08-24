from django import forms

from .models import TreeReport


class TreeReportForm(forms.ModelForm):
    """Form for users to submit a new tree report."""

    class Meta:
        model = TreeReport
        fields = ["location", "description", "image"]