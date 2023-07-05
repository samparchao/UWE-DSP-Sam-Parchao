from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from Recommendations.forms import TopicForm
from Recommendations.models import Topic, TopicPreference


def select_topics(request):
    print(request.method)
    if request.method == 'POST':
        # Get the selected topics and ratings from the form
        selected_topics = request.POST.getlist('topic')
        ratings = request.POST.getlist('rating')

        # Delete existing topic preferences for the user
        TopicPreference.objects.filter(user=request.user).delete()

        # Create new topic preferences for the selected topics
        for topic_id, rating in zip(selected_topics, ratings):
            topic = get_object_or_404(Topic, id=topic_id)
            TopicPreference.objects.create(user=request.user, topic=topic, rating=rating)

        return redirect('index:home')  # Replace 'index' with the appropriate URL name for the index page
    else:
        topics = Topic.objects.all()
        context = {'topics': topics}
        return render(request, 'select_topics.html', context)
    


@staff_member_required
def create_topic(request):
    topics = Topic.objects.all()  # Get all existing topics
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic created successfully.')
    else:
        form = TopicForm()
    return render(request, 'create_topic.html', {'form': form, 'topics': topics})


@staff_member_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        topic.delete()
        messages.success(request, 'Topic deleted successfully.')
    
    return redirect('recommendations:create-topic')