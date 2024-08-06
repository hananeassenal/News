import time
import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors
import json
import re

# Groq API Key
GROQ_API_KEY = "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"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Predefined queries by country
queries_by_country = {
    "France": ["France new data centre","France new data center"],
    "UK": ["UK new data centre","UK new data center"],
    "Germany": ["Germany new data centre","Germany new data center"],
    "Ireland": ["Ireland new data centre","Ireland new data center"],
    "USA": ["USA new data centre","USA new data center"],
    "Brazil": ["Brazil new data centre","Brazil new data center"]
}

# Country codes for Google Serper API
country_codes = {
    "France": "fr",
    "Brazil": "br",
    "USA": "us",
    "UK": "gb",
    "Germany": "de",
    "Ireland": "ie"
}

def check_login():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("You need to be logged in to view this page.")
        st.write("[Login](login.py)")
        st.stop()

def fetch_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        # Use Groq model for summarization
        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt)
        
        return f"{summary}\n\nFor more please visit {url}"
    except Exception as e:
        return f"For more please visit {url}"

def fetch_articles(query, country_code):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": country_code,
        "tbs": "qdr:m"
    })
    headers = {
        'X-API-KEY': '72961141ec55e220e7bfac56098cc1627f49bd9b',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 429:
        # Handle rate limit error
        st.warning("Too many requests. Waiting for 1 minute before retrying...")
        time.sleep(60)
        response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        json_data = response.json()
        if 'organic' in json_data and json_data['organic']:
            articles = []
            for article in json_data['organic']:
                title = article.get('title', '')
                snippet = article.get('snippet', '')
                date = article.get('date', '')
                article_url = article.get('link', '')
                
                articles.append({
                    'title': title,
                    'snippet': snippet,
                    'date': date,
                    'url': article_url
                })
            
            for article in articles:
                with st.spinner(f"Processing article: {article['title']}"):
                    summary = fetch_summary(article['url'])
                    article['summary'] = summary
                    display_article(article)
                    st.write("---")
        else:
            st.error("No articles found.")
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")

def parse_relative_date(relative_date_str):
    # Function to parse relative dates like '1 day ago'
    now = datetime.now()
    if "hour" in relative_date_str:
        hours = int(re.findall(r'\d+', relative_date_str)[0])
        return now - timedelta(hours=hours)
    elif "day" in relative_date_str:
        days = int(re.findall(r'\d+', relative_date_str)[0])
        return now - timedelta(days=days)
    elif "month" in relative_date_str:
        months = int(re.findall(r'\d+', relative_date_str)[0])
        return now - timedelta(days=months * 30)
    elif "year" in relative_date_str:
        years = int(re.findall(r'\d+', relative_date_str)[0])
        return now - timedelta(days=years * 365)
    return now

def display_article(article):
    button_key = f"save_{article['url']}"  # Unique key for each button

    # Format date for better readability
    if isinstance(article['date'], str):
        if "hour" in article['date'] or "day" in article['date']:
            try:
                date = parse_relative_date(article['date'])
            except Exception as e:
                st.error(f"Date parsing error for: {article['date']}")
                date = datetime.now()
        else:
            try:
                date = datetime.strptime(article['date'], '%d %b %Y')
            except ValueError:
                st.error(f"Date parsing error for: {article['date']}")
                date = datetime.now()
    else:
        date = datetime.now()

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <p>{article['snippet']}</p>
        <p>Date: {date.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Save Article: {article['title']}", key=button_key):
        save_article(article)
        st.success(f"Article saved: {article['title']}")

def save_article(article):
    try:
        client = MongoClient("mongodb+srv://hananeassendal:RebelDehanane@cluster0.6bgmgnf.mongodb.net/Newsapp?retryWrites=true&w=majority")
        db = client.Newsapp
        saved_articles_collection = db.SavedArticles
    except errors.OperationFailure as e:
        st.error(f"Authentication failed: {e.details['errmsg']}")
        return
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return

    saved_articles_collection.update_one(
        {"url": article['url']},
        {"$set": article},
        upsert=True
    )

def main():
    check_login()  # Ensure the user is logged in

    st.title("New Data Centre")

    # Ensure country is set from session state
    if 'country' not in st.session_state:
        st.session_state.country = "France"  # Default country if not set

    country_options = ["France", "UK", "Germany", "Ireland", "USA", "Brazil"]
    try:
        country_index = country_options.index(st.session_state.country)
    except ValueError:
        country_index = 0  # Fallback to default if the country is not in the list

    country = st.selectbox("Select Country", country_options, index=country_index)
    
    # Check if the selected country is different from the session state
    if country != st.session_state.country:
        st.session_state.country = country
        st.rerun()  # Trigger rerun if country is changed

    st.subheader("Search News")
    query = st.text_input("Enter search query")

    country_code = country_codes.get(st.session_state.country, "us")  # Default to "us" if country code not found

    if query:
        fetch_articles(query, country_code)
    else:
        queries = queries_by_country.get(st.session_state.country, [])
        for query in queries:
            fetch_articles(query, country_code)

if __name__ == "__main__":
    main()
