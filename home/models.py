from django.db import models

# Create your models here.


class Announcement(models.Model):
    STATUS_CHOICES = (
        ('draft', 'draft'),
        ('published', 'published')
    )

    title = models.CharField(max_length=1023, unique=True)
    body = models.TextField()
    manager = models.ForeignKey(
        'auth.User',
        models.SET_NULL,
        null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=15,
        default='draft',
        choices=STATUS_CHOICES
    )

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcement'

    def __str__(self):
        max_length = 5
        short_name = self.title.split()[:max_length]
        if len(short_name) < max_length:
            return '[{}] {}'.format(self.status, self.title)
        else:
            return '[{}] {} ...'.format(self.status, ' '.join(short_name))
