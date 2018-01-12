from django.shortcuts import render


# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')


def index(request):
    return render(request, "index.html")


def login(request):
    return render(request, 'dashboard.html')