from django.urls import path
from Index import views

app_name = 'index'

urlpatterns = [
    path('', views.fetch_news_articles, name='index'),
    path('home/', views.home, name='home'),
    path('article/<int:article_id>/', views.article_details, name='article_details'),
    path('staff/', views.staff_page, name='staff-page'),
    path('delete-articles/', views.delete_articles, name='delete-articles'),
    path('save-article/<int:article_id>/', views.save_article, name='save-article'),
    path('unsave-article/<int:article_id>/', views.unsave_article, name='unsave-article'),
    path('comment/<int:article_id>/', views.comment, name='comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete-comment'),
    path('saved-articles/', views.view_saved_articles, name='saved-articles'),
    path('delete-daily-task-flags/', views.delete_daily_task_flags, name='delete-daily-task-flags'),
]
