from django.db import models


class RepeatUser(models.Model):
    name = models.CharField(max_length=63)
    count = models.IntegerField(default=0)

# Create your models here.
