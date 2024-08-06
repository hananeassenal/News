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

            for article in articles:
                with st.spinner(f"Processing article: {article['title']}"):
                    summary = fetch_summary(article['url'])
                    article['summary'] = summary
                    display_article(article)
                    st.write("---")
        else:
            st.warning("No articles found.")
    else:
        st.error(f"API request error: {response.status_code} - {response.reason}")
