from django.urls import path
from Recommendations import views

app_name = 'recommendations'

urlpatterns = [
    path('select-topics/', views.select_topics, name='select_topics'),
    path('create-topic/', views.create_topic, name='create-topic'),
    path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('delete-topic-preferences/', views.delete_topic_preferences, name='delete-topic-preferences'),
    path('fetch-articles/', views.fetch_articles_from_categories, name='fetch-articles'),
    path('record-action/', views.record_action, name='record-action'),
]
