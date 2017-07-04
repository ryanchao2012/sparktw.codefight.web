from django.core.files.storage import default_storage

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.decorators.http import (
    require_POST
)
# from django.utils import timezone

from rest_framework.renderers import JSONRenderer

from combat.models import Quiz, Snippet
from combat.forms import SnippetForm, ClientSnippetForm
# Create your views here.


class JSONResponse(HttpResponse):
    """An HttpResponse that renders its content into JSON."""

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def challenges(request):
    quizs = Quiz.objects.all()[:10]
    return render(request, 'quiz_list.html', {'quizs': quizs})


@require_POST
def evaluate(request):
    print(repr(request.META))
    ret = {'error': 0}
    if request.user.is_authenticated():
        data = request.POST.copy()

        try:
            snippet = Snippet.objects.get(contestant=data['contestant'], quiz=data['quiz'], language=data['language'])
            form = SnippetForm(data, instance=snippet)
        except Exception as err:
            print(err)
            form = SnippetForm(data)

        if form.is_valid():
            form.save()

            # TODO: backend callback

            #

    else:
        ret['error'] = 1
        ret['error_message'] = 'AnonymousUser'

    return JSONResponse(ret)


class QuizView(DetailView):
    template_name = 'quiz.html'
    model = Quiz
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super(QuizView, self).get_context_data(**kwargs)
        content = default_storage.open(self.object.description.path).read()
        form = ClientSnippetForm()
        context['description'] = content
        context['snippet'] = form

        return context
