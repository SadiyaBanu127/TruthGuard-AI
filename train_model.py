"""Train and save the local TruthGuard text classifier."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "news.csv"
MODEL_PATH = BASE_DIR / "model" / "fake_news_model.pkl"
REQUIRED_COLUMNS = {"title", "text", "label"}


def main():
    dataset = pd.read_csv(DATASET_PATH)
    missing = REQUIRED_COLUMNS - set(dataset.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    if dataset["label"].nunique() < 2:
        raise ValueError("Dataset must contain at least two labels.")
    content = dataset["title"].fillna("") + " " + dataset["text"].fillna("")
    model = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    model.fit(content, dataset["label"])
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Trained on {len(dataset)} records and saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
