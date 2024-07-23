import streamlit as st
import hashlib
import requests
from newspaper import Article
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

# Function to generate a unique key using SHA256
def generate_unique_key(article, index):
    unique_string = f"{article['title']}_{index}_{article['url']}"
    return hashlib.sha256(unique_string.encode()).hexdigest()

# Function to fetch articles from an API
def fetch_articles(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey=YOUR_API_KEY"
    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    
    for idx, article in enumerate(articles):
        display_article(article, idx)

# Function to save an article
def save_article(article):
    # Implement saving functionality here
    pass

# Function to summarize an article
def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return article.summary
    except Exception as e:
        return f"Error occurred while fetching summary: {str(e)}"

# Function to display an article
def display_article(article, index):
    # Generate a unique key for the button
    unique_key = generate_unique_key(article, index)

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <img src="{article.get('urlToImage', '')}" alt="{article['title']}" style="width:100%; height:auto;">
        <p>Date: {datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{summarize_article(article['url'])}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"Save Article: {article['title']}", key=unique_key):
        save_article(article)
        st.success(f"Article saved: {article['title']}")

# Main function
def main():
    st.set_page_config(page_title="News App", page_icon="📰")

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
        queries_by_country = {
            "Brazil": ["Brazil + hydro + Drought", "Brazil + low + hydro", "Sao Paolo + Blackouts", "Brazil + blackouts"],
            "Dubai": ["Jebel Ali + Dubai + Port + constraints", "Jebel Ali + Dubai + Port + storm", "Jebel Ali + Dubai + Port + flood"],
            "Saudi": ["Saudi + new data centre", "Saudi + new data center"],
            "China": ["Shanghai + port + congestion", "Shanghai port + constraint", "Shanghai + port + delays"]
        }
        queries = queries_by_country.get(st.session_state.country, [])
        for query in queries:
            fetch_articles(query)

if __name__ == "__main__":
    main()
