import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn import naive_bayes
from sklearn.metrics import accuracy_score
import pickle


class SentimentAnalysis:
    """Class for sentiment analysis of user reviews."""

    def __init__(self, dataset_path='../reviews.csv'):
        """Initialize the SentimentAnalysis class."""
        self.dataset_path = dataset_path
        self.dataset = pd.read_csv(dataset_path)
        self.stopset = stopwords.words('english')
        self.vectorizer = TfidfVectorizer(
            use_idf=True, lowercase=True, strip_accents='ascii', stop_words=self.stopset)

    def preprocess_data(self):
        """Preprocess the data by vectorizing the text and splitting into training and test sets."""
        X = self.vectorizer.fit_transform(self.dataset.review)
        y = self.dataset.sentiment
        self.save_transformer()
        return X, y

    def save_transformer(self, filename='../artifact/transform.pkl'):
        """Save the vectorizer transformer to a pickle file."""
        pickle.dump(self.vectorizer, open(filename, 'wb'))
        print(f"Vectorizer transformer saved as {filename}")

    def train_model(self, X_train, y_train):
        """Train the sentiment analysis model."""
        clf = naive_bayes.MultinomialNB()
        clf.fit(X_train, y_train)
        self.save_model(clf)
        return clf

    def save_model(self, model, filename='artifact/sentiment_model.pkl'):
        """Save the trained model to a pickle file."""
        pickle.dump(model, open(filename, 'wb'))
        print(f"Trained model saved as {filename}")

    def evaluate_model(self, model, X_test, y_test):
        """Evaluate the performance of the trained model."""
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred) * 100
        print(f"Model accuracy: {accuracy:.2f}%")
        return accuracy

    def run_sentiment_analysis(self, test_size=0.20, random_state=42):
        """Run the complete sentiment analysis process."""
        X, y = self.preprocess_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state)
        model = self.train_model(X_train, y_train)
        accuracy = self.evaluate_model(model, X_test, y_test)
        return accuracy


if __name__ == "__main__":
    sentiment_analysis = SentimentAnalysis()
    sentiment_analysis.run_sentiment_analysis()
