import httpx
from Prediction import load_model, predict_topic_words
from similarity import calculate_similarity
from flask import Flask, request, render_template

# Initialize Flask app
app = Flask(__name__)

# Load models once when starting the app
tfidf_vectorizer = load_model('News Proto/tfidf_vectorizer.pkl')  # Ensure correct path
nmf_model = load_model('News Proto/nmf_model.pkl')  # Ensure correct path


def google_search(api_key, search_engine_id, query, **params):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': 'AIzaSyC6oIUD2f1iuXGadfVPksbAQpHJSvcFtvk',
        'cx': '5047be7447f514341',
        'q': query,
        **params
    }
    response = httpx.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


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
        print("sent")  # Indicate that a submission has been received

        # Predict topics
        primary_topic, subtopics = predict_topic_words(news_headline, tfidf_vectorizer, nmf_model)
        print(f"Predicted Topic: {primary_topic}")
        print(f"Subtopics: {', '.join(subtopics)}")

        # Collect search results using Google Custom Search API
        api_key = 'YOUR_API_KEY'  # Replace with your actual API key
        search_engine_id = 'YOUR_SEARCH_ENGINE_ID'  # Replace with your actual search engine ID

        try:
            response = google_search(api_key, search_engine_id, news_headline)
            search_results = response.get('items', [])
            if len(search_results) >= 5:  # Limit to top 5 results
                search_results = search_results[:5]

            # Extract top titles and URLs
            similar_headlines = [(result['title'], result['link']) for result in search_results]
            print("Top 5 Similar Headlines:")
            for title, url in similar_headlines:
                print(f"Title: {title}, URL: {url}")  # Print each headline with its URL

            # Calculate similarities between input and scraped headlines
            similarities = []
            harmonic_means = []  # To store harmonic means for aggregation

            for title, url in similar_headlines:
                if title:  # Check if title is not empty or None
                    score_dict = calculate_similarity(news_headline, title)  # Use title for similarity calculation
                    similarities.append((title, score_dict))
                    harmonic_means.append(score_dict['harmonic_mean'])  # Collect harmonic means
                else:
                    print("Empty title found; skipping similarity calculation.")

            print("Similarities:")
            for title, score in similarities:
                print(f"Title: {title}, Score: {score}")

            # Calculate combined score as average of harmonic means
            if harmonic_means:
                combined_score = sum(harmonic_means) / 5
            else:
                combined_score = 0

            return render_template("main.html",
                                   prediction_text="Most representative word: {}<br>Subtopics: {}".format(primary_topic,
                                                                                                          ', '.join(
                                                                                                              subtopics)),
                                   similarities=similarities,
                                   combined_score=combined_score)  # Pass combined score to template

        except Exception as e:
            print(f"Error occurred during Google Search: {e}")
            return render_template("main.html", error="An error occurred while fetching news articles.")

    else:
        return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)