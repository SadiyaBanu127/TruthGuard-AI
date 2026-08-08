import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Load dataset
df = pd.read_csv("dataset/news.csv")

# Combine title and text
df["content"] = df["title"].fillna("") + " " + df["text"].fillna("")

# Input and output
X = df["content"]
y = df["label"]

# Create machine learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train the model
model.fit(X, y)

# Save the trained model
joblib.dump(model, "model/fake_news_model.pkl")

print("Model trained successfully!")
print("Model saved as model/fake_news_model.pkl")