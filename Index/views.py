# Create your views here.
import requests
from django.shortcuts import get_object_or_404, render
from textblob import TextBlob
from Index.models import Article
import tweepy

# Define Twitter API credentials
api_key_tweepy = 'YJRATVZGuDLWhWEOgqjbtJHi7'
api_secret_key_tweepy = '1uT2Yf3FhFaBzFdwkhw6blPSFje5stuuPWASJfG95axuPQsYPT'
access_token_tweepy = '1495776074118086660-MzKY1lKFO0mAn2VHsrrRrvg2vOyX7M'
access_token_tweepy_secret = '1jyPVXQrNPTnDU4jBLl8xpxE4gAGmAI0Bw64UZaKusg6G'

def fetch_news_articles(request):
    api_key = 'cbd719bbe559acf8e3bc3f6d08a6417a'
    api_endpoint = 'https://gnews.io/api/v4/search'
    default_params = {
        'token': api_key,
        'q': 'Trump',
        'lang': 'en',
        'max': 10  # Number of articles to fetch
    }
    
    if 'q' in request.GET:
        search_query = request.GET['q']
        if search_query:
            default_params['q'] = search_query

    response = requests.get(api_endpoint, params=default_params)
    data = response.json()
    articles = data.get('articles', [])

    # Iterate over the articles and save them to the database
    saved_articles = []
    for article in articles:
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
            saved_articles.append(saved_article)

            print(article['sentiment'])

    context = {
        'articles': saved_articles
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



def home(request):
    print("HOME PAGE----------------------------------------------------------------")
    return render(request, 'home.html')