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

def report_list(request):
    """Display all submitted tree reports."""
    reports = TreeReport.objects.order_by("-date_reported")

    return render(
        request,
        "reports/report_list.html",
        {"reports": reports},
    )

def report_detail(request, pk):
    """Display one individual tree report."""
    report = TreeReport.objects.get(pk=pk)

    return render(
        request,
        "reports/report_detail.html",
        {"report": report},
    )
def report_edit(request, pk):
    """Edit an existing tree report."""
    report = TreeReport.objects.get(pk=pk)

    if request.method == "POST":
        form = TreeReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Tree report updated successfully.")
            return redirect("report_detail", pk=report.pk)

    else:
        form = TreeReportForm(instance=report)

    return render(
        request,
        "reports/report_edit.html",
        {
            "form": form,
            "report": report,
        },
    )

def report_delete(request, pk):
    """Delete an existing tree report."""
    report = TreeReport.objects.get(pk=pk)

    if request.method == "POST":
        report.delete()
        messages.success(request, "Tree report deleted successfully.")
        return redirect("report_list")

    return render(
        request,
        "reports/report_delete.html",
        {"report": report},
    )