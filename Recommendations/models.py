from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TopicPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(default=0) 
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, null=True, blank=True, default=None)

class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class DailyTaskFlag(models.Model):
    date = models.DateField(unique=True)