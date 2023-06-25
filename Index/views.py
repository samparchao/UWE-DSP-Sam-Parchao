# Create your views here.
import requests
from django.shortcuts import get_object_or_404, render
from textblob import TextBlob
from Index.models import Article

def fetch_news_articles(request):
    api_key = 'cbd719bbe559acf8e3bc3f6d08a6417a'
    api_endpoint = 'https://gnews.io/api/v4/search'
    params = {
        'token': api_key,
        'q': 'Trump',
        'lang': 'en',
        'max': 10  # Number of articles to fetch
    }

    response = requests.get(api_endpoint, params=params)
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

    context = {
        'article': article
    }

    return render(request, 'article_details.html', context)


def home(request):
    print("HOME PAGE----------------------------------------------------------------")
    return render(request, 'home.html')