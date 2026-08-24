from django.contrib import messages
from django.shortcuts import redirect, render

from .models import TreeReport
from .forms import TreeReportForm


def home(request):
    """
    Display the homepage and the three most recent tree reports.
    """
    recent_reports = TreeReport.objects.order_by("-date_reported")[:3]

    context = {
        "recent_reports": recent_reports,
    }

    return render(request, "reports/home.html", context)

def report_tree(request):
    """Display and process the tree report form."""

    if request.method == "POST":
        form = TreeReportForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Tree report submitted successfully.")
            return redirect("home")

    else:
        form = TreeReportForm()

    return render(
        request,
        "reports/report_tree.html",
        {"form": form},
    )