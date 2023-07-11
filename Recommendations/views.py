import time
import json
import requests
import sys
from io import StringIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Recommendations.forms import TopicForm
from Recommendations.models import Topic, TopicPreference, UserAction
from Index.models import Article
from Recommendations.models import Topic
from textblob import TextBlob
from django.db.models import Sum

# Define GNews API key
api_key = 'cbd719bbe559acf8e3bc3f6d08a6417a'

def fetch_articles_from_categories(limit=10, capture_output=False):
    topics = Topic.objects.all()
    existing_articles = set()  # Set to store existing article titles

    if capture_output:
        output = StringIO()  # Create a StringIO object to capture the printed output
        sys.stdout = output  # Redirect the stdout to the StringIO object

    for topic in topics:
        print(f"Fetching articles for {topic.name}...")
        category = str.lower(topic.name)  # Use the topic name as the GNews category - lowercase for compatibility with API
        url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=any&category={category}&token={api_key}&max={limit}"
        response = requests.get(url)
        articles = response.json().get("articles", [])

        for article_data in articles:
            article_id = article_data.get("id")
            title = article_data.get("title")
            print(article_id, "Article title:", title)

            # Skip if the article title already exists in the set
            if title in existing_articles:
                continue

            description = article_data.get("description")
            content = article_data.get("content")
            url = article_data.get("url")
            image_url = article_data.get("image")
            published_date = article_data.get("publishedAt")
            source_name = article_data.get("source", {}).get("name")
            source_url = article_data.get("source", {}).get("url")

            sentiment = TextBlob(content).sentiment.polarity
            if sentiment == 0:
                sentiment_label = "Neutral"
            elif sentiment < 0:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Positive"

            existing_articles_with_title = Article.objects.filter(title=title)
            if existing_articles_with_title.exists():
                # Skip if an article with the same title already exists
                continue

            # Create a new article if it doesn't exist
            Article.objects.create(
                id=article_id,
                title=title,
                description=description,
                content=content,
                url=url,
                image_url=image_url,
                sentiment=sentiment_label,
                published_date=published_date,
                source_name=source_name,
                source_url=source_url,
                topic=topic
            )

            # Add the article title to the existing_articles set
            existing_articles.add(title)

        # Delay for 1 second between API requests
        time.sleep(1)

    if capture_output:
        sys.stdout = sys.__stdout__  # Restore the original stdout
        output.seek(0)  # Move the StringIO object's pointer to the beginning
        print_output = output.getvalue()  # Get the captured printed output as a string
        output.close()  # Close the StringIO object

        return print_output

    return HttpResponse("Articles fetched successfully.")



def calculate_category_distribution(user):
    # Define the maximum number of articles to recommend
    max_article_count = 20
    # Get the user's TopicPreference ratings
    topic_preferences = TopicPreference.objects.filter(user=user).select_related('topic')

    # Calculate the total sum of ratings
    total_ratings_sum = topic_preferences.aggregate(Sum('rating'))['rating__sum']

    category_distribution = {}

    # Calculate the percentage and number of articles for each category
    for topic_preference in topic_preferences:
        topic = topic_preference.topic
        rating = topic_preference.rating

        if total_ratings_sum == 0:
            percentage = 0.0
        else:
            percentage = rating / total_ratings_sum * 100

        articles_count = round(percentage / 100 * max_article_count)  

        category_distribution[topic.name] = {
            'percentage': percentage,
            'articles_count': articles_count
        }

    # Distribute the remaining articles to categories with the highest ratings
    remaining_articles = max_article_count - sum(category['articles_count'] for category in category_distribution.values())
    if remaining_articles > 0:
        sorted_categories = sorted(category_distribution.keys(), key=lambda x: category_distribution[x]['percentage'], reverse=True)
        for category in sorted_categories:
            if remaining_articles > 0:
                category_distribution[category]['articles_count'] += 1
                remaining_articles -= 1
            else:
                break
    
    print("Category distribution:")
    print(json.dumps(category_distribution, indent=4))

    return category_distribution


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

        return redirect('index:home') # Redirect to the home page
    else:
        topics = Topic.objects.all()
        context = {'topics': topics}
        return render(request, 'select_topics.html', context)


def update_topic_weights(user, article_id, action):
    article = get_object_or_404(Article, id=article_id)
    topic = article.topic
    
    # Check if the user has already performed the same action on the article
    existing_action = UserAction.objects.filter(user=user, article_id=article_id, action=action).exists()
    if existing_action:
        print("User has already performed the same action on the article. Skipping weight update.")
        return
    
    # Adjust weight based on the given action
    if action == 'like':
        weight_change = 10
    elif action == 'dislike':
        weight_change = -0.25
    elif action == 'read':
        weight_change = 0.15
    elif action == 'open':
        weight_change = 0.05
    else:
        print(f"Unknown action: {action}")
        return  # Unknown action
    
    print(f"Updating topic preference for {topic.name} by {weight_change}...")
    
    topic_preference = TopicPreference.objects.filter(user=user, topic=topic).first()
    
    if topic_preference:
        topic_preference.rating += weight_change
        print(f"Topic preference for {topic.name} updated to {topic_preference.rating}")
        
        # Limit the rating to a maximum of 8
        if topic_preference.rating > 8:
            topic_preference.rating = 8
        
        topic_preference.save()
    
    # Create a UserAction record to track the action
    UserAction.objects.create(user=user, article_id=article.id, action=action)


@login_required
def record_action(request):
    print("RECORD ACTION FUNCTION TRIGGERED")
    print("METHOD:", request.method)
    if request.method == 'POST':
        data = json.loads(request.body)
        article_id = data.get('article_id')
        print("ARTICLE ID:", article_id)
        action = data.get('action')
        print("ACTION:", action)
        
        # Pass the user object to the update_topic_weights function
        update_topic_weights(request.user, article_id, action)
        
        # Return a JSON response to indicate success
        return JsonResponse({'message': 'Action recorded successfully'})
    else:
        # Return a JSON response with an error message
        return JsonResponse({'error': 'Invalid request method'})




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

@staff_member_required
def delete_topic_preferences(request):
    TopicPreference.objects.all().delete()
    return redirect('index:staff-page')