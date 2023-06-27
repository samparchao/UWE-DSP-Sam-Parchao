from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from Recommendations.forms import TopicForm
from Recommendations.models import Topic

# Create your views here.
def select_topics(request):
    topics = Topic.objects.all()
    context = {'topics': topics}
    return render(request, 'select_topics.html', context)

@staff_member_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = TopicForm()
    return render(request, 'create_topic.html', {'form': form})