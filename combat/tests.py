import logging
from django.test import TestCase, Client
from combat.models import Quiz, Snippet
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

logger = logging.getLogger('django')

# Create your tests here.


class QuizTest(TestCase):
    title = 'Demo Challenge'

    def test_model_quiz(self):
        quiz = Quiz(title=self.title)
        quiz.save()
        self.assertEqual(quiz.slug, slugify(self.title))

        quiz.delete()
        self.assertFalse(Quiz.objects.filter(title=self.title).exists())


class SnippetTest(TestCase):
    signup_email = 'fake@gmail.com'
    signup_username = 'fake'
    signup_password = 'fake12345678'

    language = 'python3'
    script_ext = 'py'
    token = 'ZXCVASDFQWER1234'
    body = '''
    def answer(string):
        # test token: {}
        return 'Hello ' + string
    '''.format(token)

    quiz_title = 'Demo Challenge'

    def setUp(self):
        user = User.objects.create(username=self.signup_username, email=self.signup_email)
        user.set_password(self.signup_password)
        user.save()
        quiz = Quiz(title=self.quiz_title)
        quiz.save()

        client = Client()
        client.post(reverse('login'), {'email': self.signup_email, 'password': self.signup_password})
        response = client.post(
            reverse('evaluate'),
            {
                'contestant': user.contestant.id,
                'quiz': quiz.id,
                'language': self.language,
                'body': self.body
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_evaluate_without_login(self):
        client = Client()
        response = client.post(
            reverse('evaluate'),
            {
                'language': self.language,
                'body': self.body
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AnonymousUser')

    def test_login_data(self):
        """Check whether the sript body is sent to template when user is authenticated."""
        client = Client()
        quiz = Quiz.objects.get(title=self.quiz_title)
        response = client.get(quiz.get_absolute_url())
        self.assertNotContains(response, self.token)

        client.post(reverse('login'), {'email': self.signup_email, 'password': self.signup_password})
        response = client.get(quiz.get_absolute_url())
        self.assertContains(response, self.token)

    def test_evaluate(self):
        """Check whether the script is written in the correct path."""
        contestant = User.objects.get(email=self.signup_email).contestant
        quiz = Quiz.objects.get(title=self.quiz_title)
        snippet_set = Snippet.objects.filter(
            contestant=contestant.id,
            quiz=quiz.id,
            language=self.language
        )
        self.assertTrue(snippet_set.exists())

        snippet = snippet_set[0]
        self.assertEqual(
            snippet.script.name,
            'snippet/{}/{}/{}.{}'.format(
                contestant.valid_name(),
                quiz.valid_name(),
                snippet.valid_name(),
                self.script_ext
            )
        )
