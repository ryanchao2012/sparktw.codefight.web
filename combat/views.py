import logging
import json
from django.core.files.storage import default_storage
from django.conf import settings as django_settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.decorators.http import (
    require_POST
)
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage, SELF
# from django.utils import timezone

from rest_framework.renderers import JSONRenderer

from combat.models import Quiz, Snippet
from combat.forms import SnippetForm, ClientSnippetForm
# Create your views here.

logger = logging.getLogger('django')


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
    logger.info("submit received.")
    ret = {'error': 0}
    if request.user.is_authenticated():
        data = request.POST.copy()

        try:
            snippet = Snippet.objects.get(contestant=data['contestant'], quiz=data['quiz'], language=data['language'])
            form = SnippetForm(data, instance=snippet)
        except Exception as err:
            logger.error(err)
            form = SnippetForm(data)

        if form.is_valid():
            snippet = form.save()

            # TODO: backend callback
            # dummy code:

            # load user's answer
            import importlib
            path = snippet.script.name
            module = path[:path.find('.')].replace('/', '.')
            module = '{}.{}'.format(django_settings.MEDIA_ROOT, module)
            h = importlib.import_module(module)

            # dummy testcase
            test_case = ['ryan1', 'ryan2', 'leo3', 'admin4', 'bla5'] * 5

            # socket, blocking operation, should apply asyn mechanism
            redis_publisher = RedisPublisher(facility='hello-spark', users=[SELF], request=request)
            for tc in test_case:
                r = h.answer(tc)
                if r == 'Hello ' + tc:
                    redis_publisher.publish_message(RedisMessage('pass'))
                else: redis_publisher.publish_message(RedisMessage('failed'))

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
        default_body = '# Write your answer below.\n\n'
        if self.object.answer:
            try:
                default_body = default_storage.open(self.object.answer.path).read()
            except:
                pass

        try:
            snippet = Snippet.objects.get(contestant=self.request.user.contestant, quiz=self.object)
            body = snippet.body or default_body

            form = ClientSnippetForm({'body': body}, instance=snippet)
        except Exception as err:
            logger.warning(err)
            form = ClientSnippetForm({'body': default_body})
        context['description'] = content
        context['snippet'] = form

        return context
