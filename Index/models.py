from django.db import models
from Recommendations.models import Topic
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(default=None, blank=True, null=True)
    content = models.TextField(default=None, blank=True, null=True)
    url = models.TextField(default=None, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    sentiment = models.CharField(max_length=10)
    published_date = models.DateTimeField(default=None, blank=True, null=True)
    source_name = models.CharField(max_length=255, default=None, blank=True, null=True)
    source_url = models.TextField(default=None, blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, default=None, blank=True, null=True)
    saved_by = models.ManyToManyField(User, related_name='saved_articles')

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    sentiment = models.CharField(max_length=10, default=None, blank=True, null=True)
    content = models.TextField()