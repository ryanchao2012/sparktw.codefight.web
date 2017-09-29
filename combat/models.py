import os
import uuid
import datetime
from django.conf import settings as conf_settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
@receiver(post_save, sender=User)
def update_user_contestant(sender, instance, created, **kwargs):
    if created:
        Contestant.objects.create(user=instance)
    instance.contestant.save()


def uuid4hex():
    return uuid.uuid4().hex


class Contestant(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=63, unique=True)
    nickname = models.CharField(max_length=31, null=True, blank=True)
    sparko = models.IntegerField(default=0)
    github = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    last_update = models.DateTimeField(default=timezone.now)
    created = models.BooleanField(default=False)
    submits = models.IntegerField(default=0)
    elapsed = models.DurationField(default=datetime.timedelta, blank=True, null=True)

    class Meta:
        verbose_name = "Contestant"
        verbose_name_plural = "Contestant"

    def __str__(self):
        if self.nickname:
            return '{}'.format(self.nickname)
        else:
            return '{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username.replace('.', '-'))
        if not self.nickname:
            self.nickname = self.user.username
        super(Contestant, self).save(*args, **kwargs)

    def valid_name(self):
        return 'user_{}'.format(self.uid.hex)

    def get_absolute_url(self):
        return reverse('profile_view', kwargs={'slug': self.slug})


def quiz_directory_path(instance, filename):
        subname = 'quiz/{0}/{1}'.format(instance.slug, filename)
        fullname = os.path.join(conf_settings.MEDIA_ROOT, subname)
        if os.path.exists(fullname):
            os.remove(fullname)
        return subname


class Quiz(models.Model):
    DIFFICULT_CHOICES = (
        ('tutorial', 'tutorial'),
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard')
    )

    STATUS_CHOICES = (
        ('draft', 'draft'),
        ('published', 'published')
    )
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=1023, unique=True)
    slug = models.SlugField(max_length=1023, unique=True)
    dirname = models.CharField(max_length=1023)
    description = models.FileField(upload_to=quiz_directory_path, null=True, blank=True)
    prerequisite_py = models.TextField(blank=True, null=True)
    template_py = models.FileField(upload_to=quiz_directory_path, null=True, blank=True)
    prerequisite_scala = models.TextField(blank=True, null=True)
    template_scala = models.FileField(upload_to=quiz_directory_path, null=True, blank=True)
    reward = models.IntegerField(default=0)
    submits = models.IntegerField(default=0)
    passes = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    difficulty = models.CharField(
        max_length=15,
        choices=DIFFICULT_CHOICES,
        default='tutorial',
        null=True, blank=True
    )
    status = models.CharField(
        max_length=15,
        default='draft',
        choices=STATUS_CHOICES
    )

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

    def __str__(self):
        max_length = 3
        short_name = self.title.split()[:max_length]
        if len(short_name) < max_length:
            return '[{}] {}'.format(self.difficulty, self.title)
        else:
            return '[{}] {} ...'.format(self.difficulty, ' '.join(short_name))

    def get_absolute_url(self):
        return reverse('quiz', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Quiz, self).save(*args, **kwargs)

    def valid_name(self):
        return 'quiz_{}'.format(self.uid.hex)


def snippet_directory_path(instance, filename):
    subname = 'snippet/{0}/{1}/{2}'.format(
        instance.contestant.valid_name(), instance.quiz.valid_name(), instance.valid_name()
    )
    fullname = os.path.join(conf_settings.MEDIA_ROOT, subname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return subname


class Snippet(models.Model):

    LANGUAGE_CHOICES = (
        ('python3', 'python3'),
        ('scala', 'scala')
    )

    STATUS_CHOICES = (
        ('unknown', 'unknown'),
        ('fail', 'fail'),
        ('pass', 'pass'),
        ('compile', 'compilation error'),
        ('runtime', 'runtime error'),
        ('memory', 'memory exceeded'),
        ('running', 'running')
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language = models.CharField(
        max_length=15,
        choices=LANGUAGE_CHOICES,
        default='python3'
    )
    body = models.TextField()

    script = models.FileField(upload_to=snippet_directory_path)

    created = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(auto_now=True)
    run_count = models.IntegerField(default=0)
    run_result = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        null=True, blank=True
    )

    is_running = models.BooleanField(default=False)
    # is_pass = models.BooleanField(default=False)

    submit = models.BooleanField(default=False)
    submit_time = models.DateTimeField(null=True, blank=True)

    contestant = models.ForeignKey(
        'Contestant',
        models.SET_NULL,
        null=True, blank=True
    )

    quiz = models.ForeignKey(
        'Quiz',
        models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Snippet"
        verbose_name_plural = "Snippet"
        unique_together = ('contestant', 'quiz', 'language')

    def valid_name(self):
        return 'script_{}'.format(self.uid.hex)

    def __str__(self):
        return '{} @ {}'.format(self.quiz, self.contestant)


def answer_directory_path(instance, filename):
    subname = 'answer/{0}/{1}/{2}'.format(
        instance.contestant.valid_name(), instance.quiz.valid_name(), instance.valid_name()
    )
    fullname = os.path.join(conf_settings.MEDIA_ROOT, subname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return subname


class Answer(models.Model):
    LANGUAGE_CHOICES = (
        ('python3', 'python3'),
        ('scala', 'scala')
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language = models.CharField(
        max_length=15,
        choices=LANGUAGE_CHOICES,
        default='python3'
    )

    contestant = models.ForeignKey(
        'Contestant', models.SET_NULL,
        null=True, blank=True
    )

    quiz = models.ForeignKey(
        'Quiz', models.SET_NULL,
        null=True, blank=True
    )

    body = models.TextField()
    script = models.FileField(upload_to=answer_directory_path)

    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    submits = models.IntegerField(default=0)
    elapsed = models.DurationField(blank=True, null=True)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answer"
        unique_together = ('contestant', 'quiz', 'language')

    def valid_name(self):
        return 'answer_{}'.format(self.uid.hex)
