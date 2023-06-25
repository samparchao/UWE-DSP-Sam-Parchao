from django.urls import path
from Recommendations import views

urlpatterns = [
    # other URL patterns
    path('select-topics/', views.select_topics, name='select_topics'),
]
