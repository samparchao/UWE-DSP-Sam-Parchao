# Create your views here.
import requests
from django.shortcuts import render
from textblob import TextBlob

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

    # Iterate over the articles and fetch the image URL if available
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
            
            print(article['sentiment'])

    context = {
        'articles': articles
    }

    return render(request, 'index.html', context)