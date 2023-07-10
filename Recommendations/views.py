import time
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from Recommendations.forms import TopicForm
from Recommendations.models import Topic, TopicPreference
import requests
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from Index.models import Article
from Recommendations.models import Topic
from textblob import TextBlob
from django.db.models import Sum

# Define GNews API key
api_key = 'cbd719bbe559acf8e3bc3f6d08a6417a'

def fetch_articles_from_categories(limit=10):
    topics = Topic.objects.all()
    existing_articles = set()  # Set to store existing article titles

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
    topic_preference = TopicPreference.objects.filter(user=user, topic=topic).first()
    
    # Adjust weight based on the given action
    if action == 'like':
        weight_change = 0.25
    elif action == 'dislike':
        weight_change = -0.25
    elif action == 'read':
        weight_change = 0.15
    elif action == 'open':
        weight_change = 0.05
    else:
        print(f"Unknown action: {action}")
        return  # Unknown action
    
    if topic_preference:
        topic_preference.rating += weight_change
        print(f"Topic preference for {topic.name} updated to {topic_preference.rating}")
        
        # Limit the rating to a maximum of 8
        if topic_preference.rating > 8:
            topic_preference.rating = 8
        
        topic_preference.save()

def perform_action(request, article_id, action):
    # Process the action and update topic weights
    update_topic_weights(request, article_id, action)
    
    # Track the action in your analytics or logging system
    # For example, you can log the action in your database or external service
    
    # Redirect the user to the appropriate page
    #return redirect('index:index')  # Or any other desired redirect



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