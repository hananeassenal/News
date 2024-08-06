import requests
import json
import streamlit as st
from datetime import datetime
import time

def parse_relative_date(date_str):
    # Assuming `date_str` is in a relative format like '4 days ago'
    number, unit = date_str.split()[0], date_str.split()[1]
    number = int(number)
    if unit.startswith('day'):
        delta = timedelta(days=number)
    elif unit.startswith('hour'):
        delta = timedelta(hours=number)
    else:
        delta = timedelta()  # Default to no delta
    return datetime.now() - delta

def fetch_summary(url):
    # Placeholder function for summarizing article
    # You should replace this with actual summarization logic
    return "Summary of the article."

def fetch_articles(query):
    country_code = {
        "France": "fr",
        "Brazil": "br",
        "USA": "us",
        "UK": "gb",
        "Germany": "de",
        "Ireland": "ie"
    }.get(st.session_state.country, "us")

    url = "https://google.serper.dev/news"
    payload = json.dumps({
        "q": query,
        "gl": country_code,
        "tbs": "qdr:w"
    })
    headers = {
        'X-API-KEY': '72961141ec55e220e7bfac56098cc1627f49bd9b',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 429:
        st.warning("Too many requests. Waiting for 1 minute before retrying...")
        time.sleep(60)
        response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        json_data = response.json()

        if 'news' in json_data and json_data['news']:
            articles = []
            for article in json_data['news']:
                title = article.get('title', '')
                snippet = article.get('snippet', '')
                date_str = article.get('date', '')
                article_url = article.get('link', '')
                image_url = article.get('imageUrl', '')

                if "ago" in date_str:
                    date = parse_relative_date(date_str)
                else:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    except ValueError:
                        date = datetime.now()

                articles.append({
                    'title': title,
                    'snippet': snippet,
                    'date': date,
                    'url': article_url,
                    'image_url': image_url
                })

            # Sorting all articles by date
            articles.sort(key=lambda x: x['date'], reverse=True)

            # Display the 6 most recent articles first, then display the rest
            if len(articles) > 5:
                recent_articles = articles[:6]
                other_articles = articles[6:]
            else:
                recent_articles = articles
                other_articles = []

            # Display the 6 most recent articles
            for article in recent_articles:
                with st.spinner(f"Processing article: {article['title']}"):
                    summary = fetch_summary(article['url'])
                    article['summary'] = summary
                    display_article(article)
                    st.write("---")

            # Display the rest of the articles
            for article in other_articles:
                with st.spinner(f"Processing article: {article['title']}"):
                    summary = fetch_summary(article['url'])
                    article['summary'] = summary
                    display_article(article)
                    st.write("---")
        else:
            st.warning("No articles found.")
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")

def display_article(article):
    st.write(f"**Title:** {article['title']}")
    st.write(f"**Date:** {article['date'].strftime('%Y-%m-%d %H:%M:%S')}")
    if article['image_url']:
        st.image(article['image_url'], use_column_width=True)
    st.write(f"**Snippet:** {article['snippet']}")
    st.write(f"**Summary:** {article['summary']}")
    st.write(f"[Read more]({article['url']})")
