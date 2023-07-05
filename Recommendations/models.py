from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TopicPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, null=True, blank=True, default=None)

