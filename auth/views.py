# import json
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    authenticate
)
from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.http import HttpResponse
from django.http import HttpResponseForbidden

from django.shortcuts import render, reverse, redirect
from rest_framework.renderers import JSONRenderer
from auth.forms import (
    UserSignupForm, UserLoginForm
)
from combat.models import Contestant
from .forms import ProfileForm, PasswordForm
from django.views.generic.edit import UpdateView
from django.contrib import messages
from combat.utils import QuizData
# from django.contrib.auth.forms import PasswordChangeForm


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
    redirect_to = request.GET.get('next', '/')
    if request.method == "POST":
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

    return render(request, 'signup.html', {'form': form, 'next': redirect_to})


class PasswordChangeView(UpdateView):
    form_class = PasswordForm
    template_name = 'change_password.html'
    model = User

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if not self.success_url:
            # Forcing possible reverse_lazy evaluation
            return reverse(
                'profile_update',
                kwargs={
                    'slug': self.object.contestant.slug
                }
            )
        return super().get_success_url()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        if self.request.method == 'POST':
            return form_class(self.request.user, self.request.POST)
        else:
            return form_class(self.request.user)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            messages.success(request, 'Password updated. Please re-login with your new password.')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user != self.object:
            # return redirect(reverse('home'))
            return redirect(
                reverse(
                    'profile_view',
                    kwargs={'slug': self.object.contestant.slug}
                )
            )
        else:
            return response


def get_ranking(this):
    aheads = Contestant.objects.filter(
        user__is_staff=False,
        sparko__gte=this.sparko
    )

    same_scores = aheads.filter(sparko=this.sparko).order_by('last_update', 'submits', 'elapsed')
    _ranking = 0
    for c in same_scores:
        if c.id == this.id:
            break
        _ranking += 1

    return 1 + len(aheads) - len(same_scores) + _ranking


class ProfileView(DetailView):
    template_name = 'profile_view.html'
    model = Contestant
    context_object_name = 'contestant'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        # passed_quiz = list({ans.quiz for ans in self.object.answer_set.all()})
        context['ranking'] = get_ranking(self.object)
        # context['quiz'] =
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user == self.object.user:
            return redirect(
                reverse(
                    'profile_update',
                    kwargs={'slug': self.object.slug}
                )
            )
        else:
            return response


class ProfileUpdate(UpdateView):
    template_name = 'profile_update.html'
    model = Contestant
    form_class = ProfileForm
    context_object_name = 'contestant'

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdate, self).get_context_data(**kwargs)

        context['ranking'] = get_ranking(self.object)
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not (request.user.is_authenticated()) or request.user != self.object.user:
            # return HttpResponseForbidden()
            return redirect(
                reverse(
                    'profile_view',
                    kwargs={'slug': self.object.slug}
                )
            )
        else:
            return response

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            response = super().post(request, *args, **kwargs)
            if self.get_form().is_valid():
                messages.success(request, 'Profile Updated.')
            return response
        else:
            return HttpResponseForbidden()
