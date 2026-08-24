from django.shortcuts import render


def home(request):
    """
    Display the I-V Tree homepage.
    """
    return render(request, "reports/home.html")