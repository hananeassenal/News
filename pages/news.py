import streamlit as st
import requests
from newspaper import Article
from llama_index.llms.groq import Groq
from datetime import datetime
from pymongo import MongoClient, errors
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging

# Setup logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Groq API Key
GROQ_API_KEY = "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"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[403, 404, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# Predefined queries by country
queries_by_country = {
    "Brazil": ["Brazil hydro Drought", "Brazil low hydro", "Sao Paolo Blackouts", "Brazil blackouts"],
    "Dubai": ["Jebel Ali Dubai Port constraints", "Jebel Ali Dubai Port storm", "Jebel Ali Dubai Port flood"],
    "Saudi": ["Saudi new data centre", "Saudi new data center"],
    "China": ["Shanghai port congestion", "Shanghai port constraint", "Shanghai port delays"]
}

# Function to check if user is logged in
def check_login():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("You need to be logged in to view this page.")
        st.write("[Login](login.py)")
        st.stop()

def fetch_summary(url):
    try:
        article = Article(url, browser_user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        article.download()
        article.parse()
        text = article.text.strip()

        if not text:
            return f"There is no summary for this article.\n\nFor more please visit {url}"

        # Use Groq model for summarization
        prompt = f"Summarize the following text:\n\n{text}"
        response = llm.complete(prompt)

        # Accessing summary from the response
        summary = response.strip() if isinstance(response, str) else str(response).strip()

        if not summary:
            return f"There is no summary for this article.\n\nFor more please visit {url}"

        return f"{summary}\n\nFor more please visit {url}"
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error while fetching summary for URL {url}: {e}")
        return f"There is no summary for this article.\n\nFor more please visit {url}"
    except Exception as e:
        logging.error(f"Error occurred while fetching summary for URL {url}: {e}")
        return f"There is no summary for this article.\n\nFor more please visit {url}"

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

    response = http.post(url, json=payload, headers=headers)

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
            
            for idx, article in enumerate(articles):
                with st.spinner(f"Processing article: {article['title']}"):
                    summary = fetch_summary(article['url'])
                    article['summary'] = summary
                    display_article(article, idx)
                    st.write("---")
        else:
            st.error("No articles found.")
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")

def display_article(article, index):
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
    
    # Use unique key by including the index
    if st.button(f"Save Article: {article['title']}", key=f"save_button_{index}"):
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

    st.header(f"News Articles")
    
    # Ensure country is set from session state
    if 'country' not in st.session_state:
        st.session_state.country = "Brazil"  # Default country if not set

    country = st.selectbox("Select Country", ["Brazil", "Dubai", "Saudi", "China"], index=["Brazil", "Dubai", "Saudi", "China"].index(st.session_state.country))
    st.session_state.country = country

    st.subheader("Search News")
    query = st.text_input("Enter search query")

    if query:
        fetch_articles(query)
    else:
        queries = queries_by_country.get(st.session_state.country, [])
        for query in queries:
            fetch_articles(query)

if __name__ == "__main__":
    main()
