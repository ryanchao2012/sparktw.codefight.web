from django import template
from auth.forms import UserLoginForm

register = template.Library()


@register.simple_tag
def get_loginform():
    return UserLoginForm()
