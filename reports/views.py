from django.shortcuts import render

from .models import TreeReport


def home(request):
    """
    Display the homepage and the three most recent tree reports.
    """
    recent_reports = TreeReport.objects.order_by("-date_reported")[:3]

    context = {
        "recent_reports": recent_reports,
    }

    return render(request, "reports/home.html", context)