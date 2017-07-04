import os
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


class Contestant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # TODO: Define fields here
    nick_name = models.CharField(max_length=31, null=True, blank=True)
    sparko = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Contestant"
        verbose_name_plural = "Contestant"

    def __str__(self):
        return '{}'.format(self.user.username)

    # def save(self):
    #     pass

    # @models.permalink
    # def get_absolute_url(self):
    #     return ('')

    # TODO: Define custom methods here


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
    title = models.CharField(max_length=1023, unique=True)
    slug = models.SlugField(max_length=1023, unique=True)
    description = models.FileField(upload_to=quiz_directory_path, null=True, blank=True)

    answer = models.FileField(upload_to=quiz_directory_path, null=True, blank=True)

    difficulty = models.CharField(
        max_length=15,
        choices=DIFFICULT_CHOICES,
        default='easy',
        null=True, blank=True
    )

    reward = models.IntegerField(default=0)
    status = models.CharField(
        max_length=15,
        default='draft',
        choices=STATUS_CHOICES
    )

    success_rate = models.FloatField(default=0.0, null=True, blank=True)

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

    @models.permalink
    def get_absolute_url(self):
        return reverse('quiz', [self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Quiz, self).save(*args, **kwargs)


def snippet_directory_path(instance, filename):
    subname = 'snippet/{0}/{1}/{2}'.format(
        instance.contestant.user.username, instance.quiz.slug, filename
    )
    fullname = os.path.join(conf_settings.MEDIA_ROOT, subname)
    if os.path.exists(fullname):
        os.remove(fullname)
    return subname


class Snippet(models.Model):
    LANGUAGE_CHOICES = (
        ('python3.5', 'python3.5'),
        ('scala', 'scala')
    )

    STATUS_CHOICES = (
        ('unknown', 'unknown'),
        ('pass', 'pass'),
        ('wrong', 'wrong'),
        ('compile', 'compilation error'),
    )

    language = models.CharField(
        max_length=15,
        choices=LANGUAGE_CHOICES,
        default='python3.5'
    )
    body = models.TextField()

    script = models.FileField(upload_to=snippet_directory_path)

    run_count = models.IntegerField(default=0)
    last_run = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True
    )
    run_result = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        null=True, blank=True
    )

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

    # def __str__(self):
    #     pass
