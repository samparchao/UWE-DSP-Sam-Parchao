from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TopicPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics = models.ManyToManyField('Topic')

class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

