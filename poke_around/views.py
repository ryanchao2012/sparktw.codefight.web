from django.shortcuts import render
from combat.forms import SnippetForm
# Create your views here.


def index(request, *args, **kargs):
    form = SnippetForm()
    data = {
        'form': form,
    }
    return render(request, 'index.html', data)
