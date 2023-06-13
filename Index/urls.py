from django.urls import path
from Index import views

app_name = 'index'

urlpatterns = [
    path('', views.fetch_news_articles, name='index'),
    path('home/', views.home, name='home'),
    path('article/<int:article_id>/', views.article_details, name='article_details'),
]
