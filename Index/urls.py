from django.urls import path
from Index import views

app_name = 'index'

urlpatterns = [
    path('', views.fetch_news_articles, name='home'),
]
