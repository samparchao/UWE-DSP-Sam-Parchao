# Create your views here.
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from textblob import TextBlob
from Index.models import Article
from django.db.models import Count
from random import sample
import tweepy
from Recommendations.models import TopicPreference
from Recommendations.views import calculate_category_distribution, fetch_articles_from_categories

# Define Twitter API credentials
api_key_tweepy = 'YJRATVZGuDLWhWEOgqjbtJHi7'
api_secret_key_tweepy = '1uT2Yf3FhFaBzFdwkhw6blPSFje5stuuPWASJfG95axuPQsYPT'
access_token_tweepy = '1495776074118086660-MzKY1lKFO0mAn2VHsrrRrvg2vOyX7M'
access_token_tweepy_secret = '1jyPVXQrNPTnDU4jBLl8xpxE4gAGmAI0Bw64UZaKusg6G'

def fetch_news_articles(request):
    user = request.user
    category_distribution = calculate_category_distribution(user)
    print(category_distribution)

    # Fetch articles based on the category distribution
    articles = []
    for category, distribution in category_distribution.items():
        articles_count = distribution['articles_count']
        category_articles = Article.objects.filter(topic__name=category).order_by('-published_date')[:articles_count]
        articles.extend(category_articles)

    context = {
        'articles': articles
    }

    return render(request, 'index.html', context)


def article_details(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    auth = tweepy.OAuthHandler(api_key_tweepy, api_secret_key_tweepy)
    auth.set_access_token(access_token_tweepy, access_token_tweepy_secret)

    api = tweepy.API(auth)

    tweet_list = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name='BBCWorld', tweet_mode='extended', lang='en').items(10):
        tweet_list.append(tweet)

    context = {
        'article': article,
        'tweets': tweet_list
    }

    return render(request, 'article_details.html', context)

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