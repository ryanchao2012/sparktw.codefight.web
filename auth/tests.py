import logging
from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.auth.models import User
from auth.models import RepeatUserName
# Create your tests here.

logger = logging.getLogger('django')


def create_user_(func):
    def _wrapper(self, *args, **kwargs):
        user = User.objects.create(username=self.login_username, email=self.login_email)
        user.set_password(self.login_password)
        user.save()
        return func(self, user, *args, **kwargs)
    return _wrapper


class AuthTestCase(TestCase):
    login_username = 'admin12345'
    login_email = 'info@admin12345.com'
    login_password = 'admin12345'

    signup_email = 'fake@gmail.com'
    signup_username = 'fake'
    signup_password = 'fake12345678'
    signup_nickname = 'FakeMe'

    def setUp(self):
        user = User.objects.create(username=self.login_username, email=self.login_email)
        user.set_password(self.login_password)
        user.save()

    def test_template(self):
        name_ls = ['home', 'challenges', 'signup']
        for name in name_ls:
            response = self.client.get(reverse(name))
            self.assertTemplateUsed(response, '{}.html'.format(name))
            self.assertEqual(response.status_code, 200)

    def test_login_fail(self):
        client = Client()
        response = client.post(reverse('login'), {'email': self.signup_email, 'password': self.signup_password}, follow=True)
        self.assertNotIn('_auth_user_id', client.session)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct email and password.')

    def test_login_success(self):
        client = Client()
        response = client.post(reverse('login'), {'email': self.login_email, 'password': self.login_password}, follow=True)
        self.assertIn('_auth_user_id', client.session)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

    def test_logout(self):
        client = Client()
        client.post(reverse('login'), {'email': self.login_email, 'password': self.login_password})
        self.assertIn('_auth_user_id', client.session)
        response = client.get(reverse('logout'), follow=True)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Profile')

    def test_signup(self):
        client = Client()
        client.post(reverse('login'), {'email': self.login_email, 'password': self.login_password})
        self.assertIn('_auth_user_id', client.session)
        response = client.get(reverse('signup'))

        self.assertEqual(response.status_code, 302)
        # self.assertIn('location', response)
        # self.assertEqual(response['location'], reverse('home'))

        client.get(reverse('logout'))
        response = client.post(
            reverse('signup'),
            {'email': self.login_email},
            follow=True,
        )

        self.assertContains(response, 'This email has been taken.')

        response = client.post(
            reverse('signup'),
            {
                'email': self.signup_email,
                'nickname': self.signup_nickname,
                'password1': self.signup_password,
                'password2': self.signup_password,
            },
        )
        self.assertTrue(User.objects.filter(username=self.signup_username).exists())
        self.assertIn('_auth_user_id', client.session)
        self.assertEqual(response.status_code, 302)

    def test_model_repeatusername(self):
        RepeatUserName(name=self.signup_username).save()
        client = Client()
        client.post(
            reverse('signup'),
            {
                'email': self.signup_email,
                'nickname': self.signup_nickname,
                'password1': self.signup_password,
                'password2': self.signup_password,
            },
        )
        self.assertTrue(User.objects.filter(username='{}.{}'.format(self.signup_username, 1)).exists())
        repeat_user = RepeatUserName.objects.get(name=self.signup_username)
        self.assertEqual(repeat_user.name, self.signup_username)
        self.assertEqual(repeat_user.count, 1)

        repeat_user.delete()
        self.assertFalse(RepeatUserName.objects.filter(name=self.signup_username).exists())
