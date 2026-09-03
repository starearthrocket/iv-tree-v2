from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ProgressUpdate, TreeReport


class TreeReportForm(forms.ModelForm):
    """Form for users to submit a new tree report."""

    class Meta:
        model = TreeReport
        fields = ["location", "description", "image"]


class ProgressUpdateForm(forms.ModelForm):
    """Form for users to add progress updates to a tree report."""

    class Meta:
        model = ProgressUpdate
        fields = ["notes", "image", "status"]


class RegisterForm(UserCreationForm):
    """Form for new users to create an account."""

    class Meta:
        model = UserCreationForm.Meta.model
        fields = ("username", "password1", "password2")