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

            messages.success(
                request,
                "Tree report submitted successfully.",
            )
            return redirect("home")

    else:
        form = TreeReportForm()

    return render(
        request,
        "reports/report_tree.html",
        {"form": form},
    )


def report_list(request):
    """
    Display, search and filter submitted tree reports.

    Search includes the original report location and description,
    together with notes from related progress updates.
    """
    reports = TreeReport.objects.order_by("-date_reported")

    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status")

    if search_query:
        reports = reports.filter(
            Q(location__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(progress_updates__notes__icontains=search_query)
        ).distinct()

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
        messages.error(
            request,
            "You can only edit your own tree reports.",
        )
        return redirect("report_detail", pk=report.pk)

    if request.method == "POST":
        form = TreeReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Tree report updated successfully.",
            )
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

        messages.success(
            request,
            "Tree report deleted successfully.",
        )
        return redirect("report_list")

    return render(
        request,
        "reports/report_delete.html",
        {"report": report},
    )


@login_required
def progress_update_create(request, pk):
    """
    Add a progress update and synchronise the report's current status.
    """
    report = get_object_or_404(TreeReport, pk=pk)

    if request.method == "POST":
        form = ProgressUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            update = form.save(commit=False)
            update.tree_report = report
            update.owner = request.user
            update.save()

            report.status = update.status
            report.save(update_fields=["status"])

            messages.success(
                request,
                "Progress update added successfully.",
            )
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
    """
    Edit a progress update.

    The report's current status is changed only when the edited
    progress update is the most recent update for that report.
    """
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
            updated_progress = form.save()
            report = updated_progress.tree_report

            latest_update = report.progress_updates.order_by(
                "-date_added",
                "-pk",
            ).first()

            if latest_update and latest_update.pk == updated_progress.pk:
                report.status = updated_progress.status
                report.save(update_fields=["status"])

            messages.success(
                request,
                "Progress update edited successfully.",
            )
            return redirect(
                "report_detail",
                pk=report.pk,
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
    """
    Delete a progress update and restore the previous current status
    when the latest update is removed.
    """
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

    report = update.tree_report
    report_pk = report.pk

    if request.method == "POST":
        latest_update = report.progress_updates.order_by(
            "-date_added",
            "-pk",
        ).first()

        deleting_latest = (
            latest_update is not None
            and latest_update.pk == update.pk
        )

        update.delete()

        if deleting_latest:
            previous_update = report.progress_updates.order_by(
                "-date_added",
                "-pk",
            ).first()

            if previous_update:
                report.status = previous_update.status
            else:
                report.status = "reported"

            report.save(update_fields=["status"])

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

            messages.success(
                request,
                "Account created successfully. You can now log in.",
            )
            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "reports/register.html",
        {"form": form},
    )
