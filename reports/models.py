from django.db import models


class TreeReport(models.Model):
    """
    Stores a reported tree affected by invasive ivy.
    """

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