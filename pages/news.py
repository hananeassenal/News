import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors

# Groq API Key
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

def fetch_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt)
        
        return f"{summary}\n\nFor more please visit {url}"
    except Exception as e:
        return f"For more please visit {url}"

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
        "x-rapidapi-key": "import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors

# Groq API Key
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

def fetch_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt)
        
        return f"{summary}\n\nFor more please visit {url}"
    except Exception as e:
        return f"For more please visit {url}"

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
        "x-rapidapi-key": "import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors

# Groq API Key
GROQ_API_KEY = "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"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

def fetch_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt)
        
        return f"{summary}\n\nFor more please visit {url}"
    except Exception as e:
        return f"For more please visit {url}"

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
        return response.json().get('news', [])
    else:
        return []

def display_article(article):
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <img src="{article['image_url']}" alt="{article['title']}" style="width:100%; height:auto;">
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("News Summarizer")

    query = st.text_input("Enter search query")

    if query:
        articles = fetch_articles(query)
        for article in articles:
            article_url = article['url']
            title, text, image_url = fetch_summary(article_url)
            article['summary'] = text
            article['title'] = title
            article['image_url'] = image_url
            display_article(article)

if __name__ == "__main__":
    main()
",
        "x-rapidapi-host": "newsnow.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('news', [])
    else:
        return []

def display_article(article):
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <img src="{article['image_url']}" alt="{article['title']}" style="width:100%; height:auto;">
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("News Summarizer")

    query = st.text_input("Enter search query")

    if query:
        articles = fetch_articles(query)
        for article in articles:
            article_url = article['url']
            title, text, image_url = fetch_summary(article_url)
            article['summary'] = text
            article['title'] = title
            article['image_url'] = image_url
            display_article(article)

if __name__ == "__main__":
    main()
",
        "x-rapidapi-host": "newsnow.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('news', [])
    else:
        return []

def display_article(article):
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <img src="{article['image_url']}" alt="{article['title']}" style="width:100%; height:auto;">
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("News Summarizer")

    query = st.text_input("Enter search query")

    if query:
        articles = fetch_articles(query)
        for article in articles:
            article_url = article['url']
            title, text, image_url = fetch_summary(article_url)
            article['summary'] = text
            article['title'] = title
            article['image_url'] = image_url
            display_article(article)

if __name__ == "__main__":
    main()
