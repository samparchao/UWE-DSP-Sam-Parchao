from django.db import models
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
    category = models.CharField(max_length=255, default=None, blank=True, null=True)   

    def __str__(self):
        return self.title