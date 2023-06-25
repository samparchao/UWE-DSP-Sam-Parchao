from django.shortcuts import render
from Recommendations.models import Topic

# Create your views here.
def select_topics(request):
    topics = Topic.objects.all()
    context = {'topics': topics}
    return render(request, 'recommendations/select_topics.html', context)