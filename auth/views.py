import json
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    authenticate
)
from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from rest_framework.renderers import JSONRenderer
from auth.forms import (
    UserSignupForm, UserLoginForm
)
# from django.contrib.auth.models import User


# Create your views here.
class JSONResponse(HttpResponse):
    """An HttpResponse that renders its content into JSON."""

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def home(request):
    return render(request, 'home.html')


def logout(request):
    redirect_to = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(redirect_to)


def login(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))

    redirect_to = request.GET.get('next', '/')
    if request.method == 'POST':
        loginform = UserLoginForm(request.POST)
        if loginform.is_valid():
            auth_user = authenticate(username=loginform.cleaned_data['username'], password=loginform.cleaned_data['password'])
            if auth_user:
                auth_login(request, auth_user)
                return redirect(redirect_to)
        else:
            form = UserSignupForm()
            return render(request, 'signup.html', {'loginform': loginform, 'form': form})
    else:
        return redirect(redirect_to)


def signup(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))

    if request.method == "POST":
        redirect_to = request.GET.get('next', '/')
        data = request.POST.copy()
        form = UserSignupForm(data)

        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            auth_user = authenticate(username=user.username, password=raw_password)
            if auth_user:
                auth_login(request, auth_user)
            return redirect(redirect_to)

    else:
        form = UserSignupForm()

    return render(request, 'signup.html', {'form': form})
