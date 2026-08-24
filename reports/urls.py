from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("report/", views.report_tree, name="report_tree"),
    path("reports/", views.report_list, name="report_list"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/edit/", views.report_edit, name="report_edit"),
    path("reports/<int:pk>/delete/", views.report_delete, name="report_delete"),
]