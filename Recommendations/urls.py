from django.urls import path
from Recommendations import views

app_name = 'recommendations'

urlpatterns = [
    # other URL patterns
    path('select-topics/', views.select_topics, name='select_topics'),
    path('create-topic/', views.create_topic, name='create-topic'),
]
