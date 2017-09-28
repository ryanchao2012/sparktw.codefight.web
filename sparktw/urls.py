"""web URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from combat import views as combat_views
from auth import views as auth_views


urlpatterns = [
    url(r'^yeee/', admin.site.urls),
    url(r'^$', auth_views.home, name='home'),
    url(r'^challenges/$', combat_views.challenges, name='challenges'),
    url(r'^leaderboard/$', combat_views.leaderboard, name='leaderboard'),
    url(r'^q/(?P<slug>[-\w]+)/$', combat_views.QuizView.as_view(), name='quiz'),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/signup/$', auth_views.signup, name='signup'),
    url(r'^accounts/profile/(?P<slug>[-\w]+)/$', auth_views.ProfileView.as_view(), name='profile_view'),
    url(r'^accounts/update/(?P<slug>[-\w]+)/$', auth_views.ProfileUpdate.as_view(), name='profile_update'),

]
