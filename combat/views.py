import logging
import json
import time
from django.core.files.storage import default_storage
from django.conf import settings as django_settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.decorators.http import (
    require_POST
)
from django.shortcuts import redirect, reverse
from django.core.serializers.json import DjangoJSONEncoder

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage, SELF
from django.utils import timezone

from rest_framework.renderers import JSONRenderer

from combat.models import Quiz, Snippet, Contestant
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
    return render(request, 'challenges.html', {'quizs': quizs})


def leaderboard(request):
    contestants = Contestant.objects.filter(user__is_staff=False).filter(sparko__gt=0).order_by('-sparko')[:100]
    return render(request, 'ranking.html', {'contestants': contestants})


@require_POST
def evaluate(request):
    logger.info("evaluate request received.")
    ret = {'error': 0}
    if request.user.is_authenticated():
        data = request.POST.copy()

        try:
            snippet = Snippet.objects.get(contestant=data['contestant'], quiz=data['quiz'], language=data['language'])
            form = SnippetForm(data, instance=snippet)
        except Exception as err:
            logger.warning(err)
            form = SnippetForm(data)

        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.last_run = timezone.now()
            snippet.save()

            # TODO: backend callback

            # # dummy code:

            # # load user's answer
            # import importlib
            # path = snippet.script.name
            # # body = default_storage.open(snippet.script.path).read().decode('utf-8')
            # # logger.info(body)
            # module = path[:path.find('.')].replace('/', '.')
            # module = '{}.{}'.format(django_settings.MEDIA_ROOT, module)
            # h = importlib.import_module(module)

            # # dummy testcase
            # test_case = ['ryan1', 'ryan2', 'leo3', 'admin4', 'bla5'] * 5

            # # socket, blocking operation, should apply asyn mechanism
            # redis_publisher = RedisPublisher(facility=snippet.quiz.slug, users=[SELF], request=request)
            # for i, tc in enumerate(test_case):
            #     r = h.answer(tc)
            #     time.sleep(0.001)
            #     if r == 'Hello ' + tc:
            #         redis_publisher.publish_message(RedisMessage('{}:pass'.format(i)))
            #     else:
            #         redis_publisher.publish_message(RedisMessage('{}:failed'.format(i)))

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

        if self.object.description:
            content = default_storage.open(self.object.description.path).read().decode('utf-8')
        else:
            content = '### No description, good luck :p'

        default_answer = '# Write your answer below.\n\n'
        answer = {}
        languages = [
            ('python3', self.object.answer_py),
            ('scala', self.object.answer_scala)
        ]
        if self.request.user.is_authenticated():
            snippet = Snippet.objects.filter(contestant=self.request.user.contestant, quiz=self.object).order_by('-last_run')
            for lang, file in languages:
                try:
                    sn = snippet.get(language=lang)
                    answer[lang] = sn.body

                except:
                    if bool(file):
                        answer[lang] = default_storage.open(file.path).read().decode('utf-8')
                    else:
                        answer[lang] = default_answer

            try:
                form = ClientSnippetForm({'language': snippet[0].language}, instance=snippet[0])
            except Exception as err:
                logger.warning(err)
                form = ClientSnippetForm({'language': 'python3'})

        else:
            for lang, file in languages:
                if bool(file):
                    answer[lang] = default_storage.open(file.path).read().decode('utf-8')
                else:
                    answer[lang] = default_answer
            form = ClientSnippetForm({'language': 'python3'})

        context['description'] = content
        context['snippet'] = form
        context['answer'] = json.dumps(answer, cls=DjangoJSONEncoder)

        return context
