# Create your views here.
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from textblob import TextBlob
from django.contrib import messages
from Index.models import Article
from django.db.models import Count
from random import sample
from Recommendations.models import TopicPreference
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

    context = {
        'articles': articles
    }

    return render(request, 'index.html', context)




def article_details(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # auth = tweepy.OAuthHandler(api_key_tweepy, api_secret_key_tweepy)
    # auth.set_access_token(access_token_tweepy, access_token_tweepy_secret)

    # api = tweepy.API(auth)

    # tweet_list = []
    # for tweet in tweepy.Cursor(api.user_timeline, screen_name='BBCWorld', tweet_mode='extended', lang='en').items(10):
    #     tweet_list.append(tweet)



    # Place holder for tweets (DUE TO TWITTER API CHANGES, THIS IS NO LONGER POSSIBLE ON THE FREE TIER)
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
        'tweets': tweet_list
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
    return redirect('index:index')

@staff_member_required
def staff_page(request):
    return render(request, 'staff_page.html')

@staff_member_required
def delete_articles(request):
    Article.objects.all().delete()
    return redirect('index:staff-page')


def home(request):
    print("HOME PAGE----------------------------------------------------------------")
    return render(request, 'home.html')