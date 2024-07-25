import streamlit as st
from requests_html import HTMLSession
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors
import os

# Groq API Key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# MongoDB credentials from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://hananeassendal:RebelDehanane@cluster0.6bgmgnf.mongodb.net/Newsapp?retryWrites=true&w=majority")

# NewsNow API Key (if needed)
NEWSNOW_API_KEY = os.getenv("NEWSNOW_API_KEY", "3f0b7a04abmshe28889e523915e1p12b5dcjsn4014e40913e8")

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
        st.error(f"Error fetching summary: {e}")
        return f"For more please visit {url}"

def fetch_articles_from_google_news():
    session = HTMLSession()
    url = 'https://news.google.com/topstories?hl=en-GB&gl=GB&ceid=GB:en'
    r = session.get(url)
    r.html.render(sleep=1, scrolldown=5)

    articles = r.html.find('article')
    newslist = []

    for item in articles:
        try:
            newsitem = item.find('h3', first=True)
            title = newsitem.text
            link = list(newsitem.absolute_links)[0]  # Convert set to list and get the first link
            newsarticle = {
                'title': title,
                'url': link,
                'date': datetime.now()  # Use current date, or extract date if available
            }
            newslist.append(newsarticle)
        except Exception as e:
            st.error(f"Error processing article: {e}")
            continue

    return newslist

def display_article(article):
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article.get('summary', 'Summary not available')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Save Article: {article['title']}", key=article['url']):
        save_article(article)
        st.success(f"Article saved: {article['title']}")

def save_article(article):
    try:
        client = MongoClient(MONGO_URI)
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

    st.header("News Articles")

    st.subheader("Fetching News from Google")
    articles = fetch_articles_from_google_news()
    
    if articles:
        for article in articles:
            with st.spinner(f"Processing article: {article['title']}"):
                summary = fetch_summary(article['url'])
                article['summary'] = summary
                display_article(article)
                st.write("---")
    else:
        st.error("No articles found.")

if __name__ == "__main__":
    main()
