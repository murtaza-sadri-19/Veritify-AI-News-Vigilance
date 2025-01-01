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
        print("sent")  # This line will print "sent" to the terminal

        # Use predict_topic_words function from Prediction.py
        primary_topic, subtopics = predict_topic_words(news_headline, tfidf_vectorizer, nmf_model)

        # Sample headline for comparison (this should ideally come from a search result)
        searched_headline = "Rohit Sharma announces retirement from T20"  # Example headline

        # Calculate similarities between input and searched headline
        similarities = calculate_similarity(news_headline, searched_headline)

        # Return prediction result and similarities to main.html template
        return render_template("main.html",
                               prediction_text="Most representative word: {}<br>Subtopics: {}".format(primary_topic,
                                                                                                      ', '.join(
                                                                                                          subtopics)),
                               similarities=similarities)

    else:
        return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)