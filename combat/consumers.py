import time
import json
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from channels.generic.websockets import WebsocketConsumer
from channels import Group
from .utils import PseudoEvaluator, SparkApiEvaluator
from .forms import SnippetForm
from .models import Snippet, Answer
from configparser import RawConfigParser
config_parser = RawConfigParser()
config_parser.read('sparktw.config.ini')

scenario = config_parser.get('global', 'scenario')


class EvaluateConsumer(WebsocketConsumer):
    logger = logging.getLogger('combat')
    http_user_and_session = True

    def connection_groups(self, **kwargs):
        """
        Group(s) to make people join when they connect and leave when they disconnect.

        Make sure to return a list/tuple, not a string!
        """
        if self.message.user.is_authenticated():
            return [self.message.channel_session['sessionid']]
        else:
            return [self.message.channel_session._SessionBase__session_key]

    def receive(self, text=None, bytes=None, **kwargs):

        self.logger.info('data received')

        if self.message.user.is_authenticated():
            data = json.loads(text)
            try:
                snpt = Snippet.objects.get(
                    contestant=data['contestant'],
                    quiz=data['quiz'],
                    language=data['language']
                )
                form = SnippetForm(data=data, instance=snpt)
            except Exception as err:
                self.logger.warning(err)
                form = SnippetForm(data=data)

            if form.is_valid():
                snippet = form.save()

                has_passed = len(
                    Answer.objects.filter(
                        contestant=snippet.contestant,
                        quiz=snippet.quiz
                    )
                ) > 0

                to_dump = []
                this_pass = True
                testdata = dict(
                    language=snippet.language,
                    solution=snippet.body,
                    subject=snippet.quiz.dirname,
                    user=snippet.contestant.valid_name(),
                    user_email=snippet.contestant.user.email,
                    has_passed=has_passed
                )

                if scenario == 'deploy':
                    result = SparkApiEvaluator().eval(testdata)
                else:
                    result = PseudoEvaluator().eval(testdata)

                for r in result:
                    if r['response_code'] >= 0:
                        this_pass = this_pass and r['response_code'] == 0
                    to_dump.append(r)
                    self.send(text=json.dumps(r))

                snippet.status = 'pass' if this_pass else 'fail'
                snippet.run_result = '\n'.join([json.dumps(r) for r in to_dump])
                snippet.is_running = False
                if this_pass:
                    ans, _ = Answer.objects.get_or_create(
                        quiz=snippet.quiz,
                        contestant=snippet.contestant,
                        language=snippet.language,
                    )
                    path = 'answer/{0}/{1}/{2}.{3}'.format(
                        ans.contestant.valid_name(),
                        ans.quiz.valid_name(),
                        ans.valid_name(),
                        'scala' if 'scala' in ans.language else 'py'
                    )
                    default_storage.delete(path)
                    ans.body = snippet.body
                    ans.script = default_storage.save(path, ContentFile(snippet.body))
                    if not has_passed:
                        snippet.contestant.sparko += snippet.quiz.reward
                        snippet.contestant.save()
                    ans.save()
                snippet.save()

    def send(self, text=None, bytes=None, close=False):
        """Send a reply back down the WebSocket."""
        message = {}
        if close:
            message["close"] = close
        if text is not None:
            message["text"] = text
        elif bytes is not None:
            message["bytes"] = bytes
        else:
            raise ValueError("You must pass text or bytes")
        # self.message.reply_channel.send(message, immediately=True)
        for session in self.connection_groups():
            Group(session).send(message, immediately=True)
