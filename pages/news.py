def fetch_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text

        if not text.strip():
            return "There is no summary for this article.\n\nFor more please visit {url}"

        # Use Groq model for summarization
        prompt = f"Summarize the following text:\n\n{text}"
        summary = llm.complete(prompt)

        if not summary.strip():
            return "There is no summary for this article.\n\nFor more please visit {url}"

        return f"{summary}\n\nFor more please visit {url}"
    except Exception as e:
        return f"There is no summary for this article.\n\nFor more please visit {url}"
