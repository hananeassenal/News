import streamlit as st
import requests
from bs4 import BeautifulSoup
from llama_index.llms.groq import Groq
from datetime import datetime

# Groq API Key
GROQ_API_KEY = "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"
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Google News API Key
GOOGLE_NEWS_API_KEY = "3f0b7a04abmshe28889e523915e1p12b5dcjsn4014e40913e8"

def fetch_article_content(url):
    """
    Fetches and extracts article content from the provided URL.
    
    Args:
        url (str): URL of the article to fetch.
    
    Returns:
        str: Extracted article text.
    """
    try:
        r = requests.get(url)
        r.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Extract text from h1 and p tags
        results = soup.find_all(['h1', 'p'])
        text = [result.get_text() for result in results]
        article_text = ' '.join(text)
        
        return article_text
    except requests.RequestException as e:
        return f"Error fetching content: {str(e)}"

def summarize_content(content):
    """
    Summarizes the provided content using the Groq model.
    
    Args:
        content (str): The text content to summarize.
    
    Returns:
        str: Summarized content.
    """
    try:
        # Use Groq model for summarization
        prompt = f"Summarize the following text:\n\n{content}"
        summary = llm.complete(prompt)
        
        return summary
    except Exception as e:
        return f"Error summarizing content: {str(e)}"

def fetch_articles(query):
    """
    Fetches articles from Google News API based on the query.
    
    Args:
        query (str): Search query for fetching articles.
    
    Returns:
        list: List of articles with title, URL, and publication date.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": GOOGLE_NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5  # Limit the number of articles
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        json_data = response.json()
        if 'articles' in json_data and json_data['articles']:
            articles = []
            for article in json_data['articles']:
                title = article.get('title', '')
                url = article.get('url', '')
                date = article.get('publishedAt', '')

                articles.append({
                    'title': title,
                    'url': url,
                    'date': datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                })
            
            return articles
        else:
            st.error("No articles found.")
            return []
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")
        return []

def display_article(article):
    """
    Displays an article with its title, publication date, and summary.
    
    Args:
        article (dict): Article details including title, URL, and date.
    """
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
        <a href="{article['url']}" target="_blank" style="text-decoration: none; color: inherit;">
            <h3>{article['title']}</h3>
        </a>
        <p>Date: {article['date'].strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>{article['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("News Articles with Summaries")

    query = st.text_input("Enter search query")

    if query:
        articles = fetch_articles(query)
        if articles:
            for article in articles:
                with st.spinner(f"Processing article: {article['title']}"):
                    article_content = fetch_article_content(article['url'])
                    if article_content:
                        summary = summarize_content(article_content)
                        article['summary'] = summary
                        display_article(article)
                        st.write("---")

if __name__ == "__main__":
    main()
