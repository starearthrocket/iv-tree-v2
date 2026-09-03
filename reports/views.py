from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProgressUpdateForm, RegisterForm, TreeReportForm
from .models import ProgressUpdate, TreeReport


def home(request):
    """
    Display the homepage and the three most recent tree reports.
    """
    recent_reports = TreeReport.objects.order_by("-date_reported")[:3]

    context = {
        "recent_reports": recent_reports,
    }

    return render(request, "reports/home.html", context)


def about(request):
    """Display information about the I-V Tree project."""
    return render(
        request,
        "reports/about.html",
    )


@login_required
def report_tree(request):
    """Display and process the tree report form."""

    if request.method == "POST":
        form = TreeReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user
            report.save()
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
    """Display, search and filter submitted tree reports."""
    reports = TreeReport.objects.order_by("-date_reported")

    search_query = request.GET.get("search")
    status_filter = request.GET.get("status")

    if search_query:
        reports = reports.filter(
            Q(location__icontains=search_query)
            | Q(description__icontains=search_query)
        )
    if status_filter:
        reports = reports.filter(status=status_filter)

    return render(
        request,
        "reports/report_list.html",
        {
            "reports": reports,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": TreeReport.STATUS_CHOICES,
        },
    )


def report_detail(request, pk):
    """Display one individual tree report."""
    report = get_object_or_404(TreeReport, pk=pk)

    return render(
        request,
        "reports/report_detail.html",
        {"report": report},
    )


@login_required
def report_edit(request, pk):
    """Edit an existing tree report."""
    report = get_object_or_404(TreeReport, pk=pk)

    if report.owner != request.user:
       messages.error(request, "You can only edit your own tree reports.")
       return redirect("report_detail", pk=report.pk)

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


@login_required
def report_delete(request, pk):
    """Delete an existing tree report."""
    report = get_object_or_404(TreeReport, pk=pk)

    if report.owner != request.user:
        messages.error(
            request,
            "You can only delete your own tree reports.",
        )
        return redirect("report_detail", pk=report.pk)

    if request.method == "POST":
        report.delete()
        messages.success(request, "Tree report deleted successfully.")
        return redirect("report_list")

    return render(
        request,
        "reports/report_delete.html",
        {"report": report},
    )


@login_required
def progress_update_create(request, pk):
    """Add a progress update to an existing tree report."""
    report = get_object_or_404(TreeReport, pk=pk)

    if request.method == "POST":
        form = ProgressUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            update = form.save(commit=False)
            update.tree_report = report
            update.owner = request.user
            update.save()

            messages.success(request, "Progress update added successfully.")
            return redirect("report_detail", pk=report.pk)

    else:
        form = ProgressUpdateForm()

    return render(
        request,
        "reports/progress_update_form.html",
        {
            "form": form,
            "report": report,
        },
    )


@login_required
def progress_update_edit(request, pk):
    """Edit an existing progress update."""
    update = get_object_or_404(ProgressUpdate, pk=pk)

    if update.owner != request.user:
        messages.error(
            request,
            "You can only edit your own progress updates.",
        )
        return redirect(
            "report_detail",
            pk=update.tree_report.pk,
        )
    if request.method == "POST":
        form = ProgressUpdateForm(
            request.POST,
            request.FILES,
            instance=update,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Progress update edited successfully.",
            )
            return redirect(
                "report_detail",
                pk=update.tree_report.pk,
            )
    else:
        form = ProgressUpdateForm(instance=update)
    return render(
        request,
        "reports/progress_update_form.html",
        {
            "form": form,
            "report": update.tree_report,
        },
    )


@login_required
def progress_update_delete(request, pk):
    """Delete an existing progress update."""
    update = get_object_or_404(ProgressUpdate, pk=pk)

    if update.owner != request.user:
        messages.error(
            request,
            "You can only delete your own progress updates.",
        )
        return redirect(
            "report_detail",
            pk=update.tree_report.pk,
        )

    report_pk = update.tree_report.pk

    if request.method == "POST":
        update.delete()
        messages.success(
            request,
            "Progress update deleted successfully.",
        )
        return redirect(
            "report_detail",
            pk=report_pk,
        )

    return render(
        request,
        "reports/progress_update_delete.html",
        {"update": update},
    )


def register(request):
    """Allow a new user to create an account."""
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "reports/register.html",
        {"form": form},
    )