from django.contrib.auth.models import User
from django.db import models


class TreeReport(models.Model):
    """
    Stores a reported tree affected by invasive ivy.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tree_reports",
        null=True,
        blank=True,
    )

    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("action_needed", "Action Needed"),
        ("protected", "Protected"),
        ("monitoring", "Monitoring"),
    ]

    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to="tree_reports/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="reported",
    )
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.location


class ProgressUpdate(models.Model):
    """
    Stores progress updates linked to an individual tree report.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progress_updates",
        null=True,
        blank=True,
    )
      
    tree_report = models.ForeignKey(
        TreeReport,
        on_delete=models.CASCADE,
        related_name="progress_updates",
    )
    notes = models.TextField()
    image = models.ImageField(
        upload_to="progress_updates/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=TreeReport.STATUS_CHOICES,
        default="monitoring",
    )
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for {self.tree_report.location}"