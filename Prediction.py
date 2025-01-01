import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF


def preprocess_text(text):
    """
    Preprocesses the input text for topic prediction.

    Args:
        text (str): The text to preprocess.

    Returns:
        list: A list of preprocessed tokens.
    """
    return text.lower().split()  # Simple example: lowercase and split by spaces


def load_model(model_path):
    """
    Loads a model from a given file path.

    Args:
        model_path (str): The path to the .pkl file.

    Returns:
        object: The loaded model.
    """
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model


def predict_topic_words(new_abstract, tfidf_vectorizer, nmf_model, no_top_words=3):
    """
    Predicts the most representative word and subtopics for the topic of a new abstract.

    Args:
        new_abstract (str): The new abstract to classify.
        tfidf_vectorizer (TfidfVectorizer): The TF-IDF vectorizer.
        nmf_model (NMF): The NMF model.
        no_top_words (int): The number of top words to return (including subtopics).

    Returns:
        tuple: A tuple containing the primary word and subtopics.
    """
    # Preprocess the new abstract
    new_processed = preprocess_text(new_abstract)

    # Join tokens into a single string
    new_processed_str = ' '.join(new_processed)

    # Transform using the TF-IDF vectorizer
    new_tfidf = tfidf_vectorizer.transform([new_processed_str])

    # Transform using the NMF model to get topic distribution
    new_topic_distribution = nmf_model.transform(new_tfidf)

    # Get the topic index with the highest probability
    predicted_topic_idx = new_topic_distribution.argmax(axis=1)[0]

    # Get the words from the topic that contribute most to this topic
    topic_words = nmf_model.components_[predicted_topic_idx]

    # Sort the words based on their weight in this topic (descending)
    sorted_indices = topic_words.argsort()[::-1]

    # Get the top words for this topic
    top_words = [tfidf_vectorizer.get_feature_names_out()[i] for i in sorted_indices[:no_top_words]]

    primary_topic = top_words[0]  # Most representative word
    subtopics = top_words[1:3]  # Top two subtopics

    return primary_topic, subtopics


# If this script is run directly, load models and test prediction (optional)
if __name__ == "__main__":
    tfidf_vectorizer = load_model('News Proto/tfidf_vectorizer.pkl')
    nmf_model = load_model('News Proto/nmf_model.pkl')

    # Example of predicting the most representative word for a new article
    new_article = "Rohit Sharma, Virat Kohli announce retirement from T20 after world cup."

    primary_topic, subtopics = predict_topic_words(new_article, tfidf_vectorizer, nmf_model)

    print(f"The most representative word for the topic of the new article is: {primary_topic}")
    print(f"Subtopics: {', '.join(subtopics)}")