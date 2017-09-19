import logging
import json
from django.core.files.storage import default_storage
from django.conf import settings as django_settings
from django.shortcuts import render
from django.forms.models import model_to_dict
import requests
from django.http import HttpResponse
from django.views.generic import DetailView
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework.renderers import JSONRenderer

from combat.models import Quiz, Snippet, Contestant
from combat.forms import LanguageForm
from combat.utils import QuizData, SnippetData, MyDict

# Create your views here.

logger = logging.getLogger('django')

SPARK_SUBMIT = 'http://35.187.234.136:3000/submit'  # curl -XPOST -d '{"user":"larry", "language":"python", "subject":"word_count", "solution":"ccc"}'  spark1.3du.me:3000/submit
SPARK_CREATE = 'http://spark1.3du.me:3000/create/user'  # curl -XPOST -d '{"user":"dd"}' spark1.3du.me:3000/create/user


class JSONResponse(HttpResponse):
    """An HttpResponse that renders its content into JSON."""

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def challenges(request):
    quizs = Quiz.objects.all()[:50]
    return render(request, 'challenges.html', {'quizs': quizs})


def leaderboard(request):
    contestants = Contestant.objects.filter(user__is_staff=False).filter(sparko__gte=0).order_by('-sparko')[:100]
    return render(request, 'ranking.html', {'contestants': contestants})


class QuizView(DetailView):
    template_name = 'quiz.html'
    model = Quiz
    context_object_name = 'quiz'
    create_user_url = 'http://35.198.254.175:3000/create/user'

    def get_context_data(self, **kwargs):
        context = super(QuizView, self).get_context_data(**kwargs)

        description = (
            default_storage.open(self.object.description.path).read().decode('utf-8')
            if self.object.description else '### No description.'
        )

        qdata = QuizData(
            description=description,
            title=self.object.title,
            uid=self.object.uid.hex,
            status=self.object.status,
            difficulty=self.object.difficulty or 'tutorial',
            reward=self.object.reward
        )

        snippets = MyDict()
        current = None

        templates = [
            ('python3', self.object.answer_py),
            ('scala', self.object.answer_scala)
        ]

        if self.request.user.is_authenticated():
            if not self.request.user.contestant.created:
                r = requests.post(
                    self.create_user_url,
                    json.dumps(
                        dict(user=self.request.user.contestant.valid_name())
                    ),
                    timeout=1
                )
                rdata = json.loads(r.content.decode('utf-8'))
                if rdata['response_code'] == 0:
                    self.request.user.contestant.created = True
                    self.request.user.contestant.save()
            snips = Snippet.objects.filter(
                contestant=self.request.user.contestant,
                quiz=self.object
            ).order_by('-last_run')

            if bool(snips):
                for s in snips:
                    snippets[s.language] = SnippetData(
                        language=s.language,
                        body=s.body,
                        uid=s.uid.hex,
                        run_count=s.run_count,
                        contestant_id=s.contestant.id,
                        quiz_id=self.object.id,
                        status=s.status,
                        is_running=s.is_running
                    )
                    if not bool(current):
                        current = snippets[s.language]

        for lang, file in templates:
            if lang not in snippets:
                body = (
                    default_storage.open(file.path).read().decode('utf-8')
                    if bool(file) else '# Write your answer below.\n\n'
                )
                snippets[lang] = SnippetData(
                    language=lang,
                    body=body,
                    quiz_id=self.object.id,
                    contestant_id=self.request.user.contestant.id if self.request.user.is_authenticated() else -1,
                )

        if not bool(current):
            current = snippets['python3']

        context['form'] = LanguageForm(initial={'language': current.get('language', 'python3')})
        context['quizdata'] = qdata
        context['current'] = current
        context['snippetdata'] = snippets

        return context
