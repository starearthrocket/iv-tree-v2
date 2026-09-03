from django.urls import path

from . import views


urlpatterns = [
    path(
        "register/",
        views.register,
        name="register",
    ),
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "about/",
        views.about,
        name="about",
    ),
    path(
        "report/",
        views.report_tree,
        name="report_tree",
    ),
    path(
        "reports/",
        views.report_list,
        name="report_list",
    ),
    path(
        "reports/<int:pk>/",
        views.report_detail,
        name="report_detail",
    ),
    path(
        "reports/<int:pk>/edit/",
        views.report_edit,
        name="report_edit",
    ),
    path(
        "reports/<int:pk>/delete/",
        views.report_delete,
        name="report_delete",
    ),
    path(
        "reports/<int:pk>/update/",
        views.progress_update_create,
        name="progress_update_create",
    ),
    path(
        "updates/<int:pk>/edit/",
        views.progress_update_edit,
        name="progress_update_edit",
    ),
    path(
        "updates/<int:pk>/delete/",
        views.progress_update_delete,
        name="progress_update_delete",
    ),
]
