# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from textblob import TextBlob
from django.contrib import messages
from Index.models import Article, Comment
from django.db.models import Count
from random import sample
from Recommendations.models import DailyTaskFlag, TopicPreference
from Recommendations.views import calculate_category_distribution, fetch_articles_from_categories


# Define Twitter API credentials
# api_key_tweepy = 'YJRATVZGuDLWhWEOgqjbtJHi7'
# api_secret_key_tweepy = '1uT2Yf3FhFaBzFdwkhw6blPSFje5stuuPWASJfG95axuPQsYPT'
# access_token_tweepy = '1495776074118086660-MzKY1lKFO0mAn2VHsrrRrvg2vOyX7M'
# access_token_tweepy_secret = '1jyPVXQrNPTnDU4jBLl8xpxE4gAGmAI0Bw64UZaKusg6G'

def fetch_news_articles(request):
    user = request.user
    category_distribution = calculate_category_distribution(user)
    articles = []

    if 'q' in request.GET:
        search_query = request.GET['q']
        if search_query:
            # Search for articles in the database
            articles = list(Article.objects.filter(title__icontains=search_query).order_by('-published_date')[:5])

            if len(articles) < 5:
                # Fetch additional articles from GNews API
                api_key = 'cbd719bbe559acf8e3bc3f6d08a6417a'
                api_endpoint = 'https://gnews.io/api/v4/search'
                params = {
                    'token': api_key,
                    'q': search_query,
                    'lang': 'en',
                    'max': 10 - len(articles)  # Number of articles to fetch
                }
                response = requests.get(api_endpoint, params=params)
                data = response.json()
                additional_articles = data.get('articles', [])

                for article in additional_articles:
                    if 'image' in article:
                        image_url = article['image']
                        title = article['title']
                        content = article['content']

                        # Add the 'image_url' key to the article dictionary
                        article['image_url'] = image_url

                        sentiment = TextBlob(content).sentiment.polarity
                        if sentiment == 0:
                            article['sentiment'] = "Neutral"
                        elif sentiment < 0:
                            article['sentiment'] = "Negative"
                        else:
                            article['sentiment'] = "Positive"

                        # Save the article to the database
                        saved_article = Article.objects.create(
                            title=title,
                            content=content,
                            image_url=image_url,
                            description=article['description'],
                            url=article['url'],
                            sentiment=article['sentiment'],
                            published_date=article['publishedAt'],
                            source_name=article['source']['name'],
                            source_url=article['source']['url']
                        )
                        articles.append(saved_article)

    if not articles:
        # Fetch articles based on the category distribution
        for category, distribution in category_distribution.items():
            articles_count = distribution['articles_count']
            category_articles = Article.objects.filter(topic__name=category).order_by('-published_date')[:articles_count]

            # Check if each article is saved by the current user
            for article in category_articles:
                article.saved_by_current_user = article.saved_by.filter(id=user.id).exists()

            articles.extend(category_articles)

    # Filter articles by sentiment if 'sentiment' parameter is present in the request GET
    sentiment_filter = request.GET.get('sentiment')
    if sentiment_filter in ['positive', 'neutral', 'negative']:
        articles = [article for article in articles if article.sentiment == sentiment_filter.capitalize()]

    context = {
        'articles': articles
    }

    return render(request, 'index.html', context)




def article_details(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Retrieve all comments for the article
    comments = Comment.objects.filter(article=article)
    
    # Convert comments to a list of dictionaries
    comment_list = []
    for comment in comments:
        comment_dict = {
            'id': comment.id,
            'username': comment.user.username,
            'time': comment.time.strftime('%b %d, %Y %I:%M %p'), 
            'content': comment.content,
            'sentiment': comment.sentiment,
        }
        comment_list.append(comment_dict)

    # auth = tweepy.OAuthHandler(api_key_tweepy, api_secret_key_tweepy)
    # auth.set_access_token(access_token_tweepy, access_token_tweepy_secret)

    # api = tweepy.API(auth)

    # tweet_list = []
    # for tweet in tweepy.Cursor(api.user_timeline, screen_name='BBCWorld', tweet_mode='extended', lang='en').items(10):
    #     tweet_list.append(tweet)

    
    # Placeholder for tweets
    tweet_list = [
        {
            'username': '@JohnDoe',
            'content': 'Wow amazing article!',
        },
        {   
            'username': '@JaneDoe',
            'content': 'So happy this is happening right now',
        },
        {
            'username': '@Jacob_Smith',
            'content': 'This is so sad, I hope this gets resolved soon',
        },
        {
            'username': '@JamesJohnson',
            'content': 'Not happy about this, but I hope it works out',
        },
    ]
    
    # Perform sentiment analysis on tweets
    for tweet in tweet_list:
        content = tweet['content']
        sentiment = TextBlob(content).sentiment.polarity
        if sentiment == 0:
            tweet['sentiment'] = "Neutral"
        elif sentiment < 0:
            tweet['sentiment'] = "Negative"
        else:
            tweet['sentiment'] = "Positive"
    
    context = {
        'article': article,
        'tweets': tweet_list,
        'comments': comment_list,
    }
    
    return render(request, 'article_details.html', context)

def save_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    article.saved_by.add(user)
    article.save()
    print(article.saved_by.all())
    messages.success(request, 'Article saved successfully!')
    return redirect('index:index')

def unsave_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    article.saved_by.remove(user)
    article.save()
    messages.success(request, 'Article unsaved successfully!')

    # Get the referer URL from the request headers
    referer = request.META.get('HTTP_REFERER')

    # Check if the referer URL is from the index:index or index:saved-articles page
    if referer and (referer.endswith(reverse('index:index')) or referer.endswith(reverse('index:saved-articles'))):
        return HttpResponseRedirect(referer)
    else:
        return redirect('index:index')

def comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    content = request.POST['content']
    sentiment = TextBlob(content).sentiment.polarity
    if sentiment == 0:
        sentiment = "Neutral"
    elif sentiment < 0:
        sentiment = "Negative"
    else:
        sentiment = "Positive"
    Comment.objects.create(article=article, user=user, content=content, sentiment=sentiment)
    messages.success(request, 'Comment posted successfully!')
    return redirect('index:article_details', article_id=article_id)

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if the user is the owner of the comment
    if comment.user == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this comment.')
    
    # Redirect back to the article details page
    return redirect('index:article_details', article_id=comment.article.id)

def view_saved_articles(request):
    user = request.user
    articles = Article.objects.filter(saved_by=user)
    context = {
        'articles': articles
    }
    return render(request, 'saved_articles.html', context)

@staff_member_required
def staff_page(request):
    return render(request, 'staff_page.html')

@staff_member_required
def delete_articles(request):
    Article.objects.all().delete()
    return redirect('index:staff-page')

@staff_member_required
def delete_daily_task_flags(request):
    DailyTaskFlag.objects.all().delete()
    return redirect('index:staff-page')


def home(request):
    print("HOME PAGE----------------------------------------------------------------")
    return render(request, 'home.html')