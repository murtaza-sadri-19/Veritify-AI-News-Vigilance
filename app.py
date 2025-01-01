import asyncio
from crawl4ai import AsyncWebCrawler  # Import Crawl4AI for web scraping
from Prediction import load_model, predict_topic_words  # Import your Prediction module here
from similarity import calculate_similarity  # Import similarity calculation function

from flask import Flask, request, render_template

# Initialize Flask app
app = Flask(__name__)

# Load models once when starting the app
tfidf_vectorizer = load_model('News Proto/tfidf_vectorizer.pkl')  # Ensure correct path
nmf_model = load_model('News Proto/nmf_model.pkl')  # Ensure correct path


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/main")
def about():
    return render_template("main.html")


@app.route("/prediction", methods=['GET', 'POST'])
def prediction():
    if request.method == "POST":
        news_headline = request.form['chatInput']

        # Print "sent" to the terminal when the form is submitted
        print("sent")

        # Use predict_topic_words function from Prediction.py
        primary_topic, subtopics = predict_topic_words(news_headline, tfidf_vectorizer, nmf_model)

        # Scrape top 5 similar news headlines using Crawl4AI
        similar_headlines = asyncio.run(scrape_similar_news(news_headline))

        # Print all scraped headlines
        print("Top 5 Similar Headlines:")
        for headline in similar_headlines:
            print(headline)  # Print each headline

        # Calculate similarities between input and scraped headlines
        similarities = []
        for headline in similar_headlines:
            score = calculate_similarity(news_headline, headline)
            similarities.append((headline, score))

        # Return prediction result and similarities to main.html template
        return render_template("main.html",
                               prediction_text="Most representative word: {}<br>Subtopics: {}".format(primary_topic,
                                                                                                      ', '.join(
                                                                                                          subtopics)),
                               similarities=similarities)

    else:
        return render_template("main.html")


async def scrape_similar_news(query):
    """
    Scrapes the top 5 news headlines related to the query using Crawl4AI.

    Args:
        query (str): The search query for news headlines.

    Returns:
        list: A list of scraped news headlines.
    """
    async with AsyncWebCrawler() as crawler:
        search_url = f"https://news.google.com/search?q={query.replace(' ', '%20')}&hl=en-US&gl=US&ceid=US%3Aen"

        result = await crawler.arun(url=search_url)

        # Extract headlines from the result (adjust based on actual HTML structure)
        headlines = []

        if hasattr(result, 'articles'):  # Check if 'articles' is a valid attribute
            for article in result.articles[:5]:  # Assuming articles is a list
                if 'title' in article:
                    headlines.append(article['title'])

        return headlines[:5]  # Return the top 5 headlines


if __name__ == "__main__":
    app.run(debug=True)