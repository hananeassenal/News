import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from requests.exceptions import RequestException

# Groq API Key
GROQ_API_KEY = "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"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

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

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
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
    except RequestException as e:
        st.error(f"API request error: {e}")
        return []

# Function to summarize articles
def fetch_summary(url):
    try:
        article = Article(url, browser_user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        article.download()
        article.parse()
        text = article.text

        # Use Groq model for summarization
        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt).strip()
        
        return f"{summary}\n\nFor more please visit {url}"
    except RequestException as e:
        st.error(f"Network error while summarizing article: {e}")
        return f"For more please visit {url}"
    except Exception as e:
        st.error(f"Error summarizing article: {e}")
        return f"For more please visit {url}"

# Function to display an article
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
    
    if st.button(f"Save Article: {article['title']}", key=article['url']):
        save_article(article)
        st.success(f"Article saved: {article['title']}")

# Function to save the article
def save_article(article):
    try:
        client = MongoClient("mongodb+srv://hananeassendal:RebelDehanane@cluster0.6bgmgnf.mongodb.net/Newsapp?retryWrites=true&w=majority")
        db = client.Newsapp
        saved_articles_collection = db.SavedArticles
        saved_articles_collection.update_one(
            {"url": article['url']},
            {"$set": article},
            upsert=True
        )
    except errors.OperationFailure as e:
        st.error(f"Authentication failed: {e.details['errmsg']}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to handle the data centre page
def data_centre():
    st.title("European Data Centre")
    
    country = st.selectbox("Select Country", ["France", "UK", "Germany", "Ireland"], index=0)
    
    st.subheader("Fetching Articles Automatically")
    
    # Generate query based on selected country
    query = f"{country} data centre"
    
    articles = fetch_articles(query)
    for article in articles:
        st.write(f"Processing article: {article['title']}")
        summary = fetch_summary(article['url'])
        article['summary'] = summary
        display_article(article)
        st.write("---")

if __name__ == "__main__":
    data_centre()
