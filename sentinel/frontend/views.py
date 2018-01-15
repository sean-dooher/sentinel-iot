from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse


# Create your views here.
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return HttpResponseRedirect(reverse('index'))


def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
        except KeyError:
            return JsonResponse({'accepted': False, 'reason': 'Missing either username or password.'})

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active and '-' not in username:
                login(request, user)
                return JsonResponse({'accepted': True})
            elif not user.is_active:
                return JsonResponse({'accepted': False, 'reason': 'Your account is disabled.'})
            else:
                return JsonResponse({'accepted': False, 'reason': "Invalid characters in username."})
        else:
            return JsonResponse({'accepted': False, 'reason': 'Invalid username or password.'})
    elif request.user.is_authenticated():
        return JsonResponse({'accepted': True})
    else:
        return HttpResponseRedirect(reverse('index'))


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.method == 'POST' and not request.user.is_authenticated():
        try:
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
        except KeyError:
            return JsonResponse({'accepted': False, 'reason': 'Missing either username, email, or password.'})

        user = User.objects.filter(username=username) | User.objects.filter(email=email)

        if user.exists():
            return JsonResponse({'accepted': False, 'reason': 'User with specified username or email already exists'})
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return JsonResponse({'accepted': True})

    elif request.method == "POST" and request.user.is_authenticated():
        return JsonResponse({'accepted': False, 'reason': 'You are already logged in'})
    else:
        return HttpResponseRedirect(reverse('index'))
