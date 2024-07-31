# pages/data_centre.py

import streamlit as st
import requests
from newspaper import Article
from datetime import datetime

# Function to fetch articles
def fetch_articles(query):
    url = "https://newsnow.p.rapidapi.com/newsv2"
    payload = {
        "query": query,
        "time_bounded": True,
        "from_date": "01/01/2023",
        "to_date": "30/12/2024",
        "location": "us",
        "language": "en",
        "page": 1
    }
    headers = {
        "x-rapidapi-key": "3f0b7a04abmshe28889e523915e1p12b5dcjsn4014e40913e8",
        "x-rapidapi-host": "newsnow.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        if 'news' in json_data and json_data['news']:
            articles = []
            for article in json_data['news']:
                title = article.get('title', '')
                image_url = article.get('top_image', '')
                date = article.get('date', '')
                article_url = article.get('url', '')
                
                articles.append({
                    'title': title,
                    'image_url': image_url,
                    'date': datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT'),
                    'url': article_url
                })
            
            articles.sort(key=lambda x: x['date'], reverse=True)
            return articles
        else:
            st.error("No articles found.")
            return []
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")
        return []

# Function to extract article content using newspaper3k
def extract_article_content(article_url):
    try:
        article = Article(article_url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        st.error(f"Error extracting article content: {e}")
        return ""

# Function to display an article
def display_article(article):
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <img src="{article['image_url']}" alt="{article['title']}" style="width:100%; height:auto;">
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Automatically extract and display the article content
    content = extract_article_content(article['url'])
    if content:
        st.write("Content:")
        st.write(content)  # Display the full article content

# Function to handle the data centre page
def data_centre():
    st.title("European Data Centre")
    
    country = st.selectbox("Select Country", ["France", "UK", "Germany", "Ireland"], index=0)
    
    st.subheader(f"Articles for {country}")
    
    # Automatically fetch articles for the selected country
    query = f"{country} data centre"
    articles = fetch_articles(query)
    
    for article in articles:
        display_article(article)
        st.write("---")

if __name__ == "__main__":
    data_centre()
