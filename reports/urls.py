from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("report/", views.report_tree, name="report_tree"),
]