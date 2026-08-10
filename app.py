"""TruthGuard AI web application."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import joblib
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "fake_news_model.pkl"


def load_model():
    """Load the persisted pipeline and give a useful startup error if absent."""
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found at {MODEL_PATH}. Run `python train_model.py` first.")
    return joblib.load(MODEL_PATH)


def get_model_signals(classifier, content, predicted_label):
    """Return the most influential model vocabulary terms present in the text."""
    try:
        vectorizer = classifier.named_steps["tfidf"]
        logistic_regression = classifier.named_steps["classifier"]
        row = vectorizer.transform([content])
        feature_names = vectorizer.get_feature_names_out()
        classes = list(logistic_regression.classes_)
        class_index = classes.index(predicted_label)
        coefficients = logistic_regression.coef_

        if coefficients.shape[0] == 1:
            # In a binary logistic model, positive values support classes_[1].
            weights = coefficients[0] if class_index == 1 else -coefficients[0]
        else:
            weights = coefficients[class_index]

        contributions = [
            (feature_names[index], float(row[0, index] * weights[index]))
            for index in row.indices
            if row[0, index] != 0
        ]
        contributions.sort(key=lambda item: item[1], reverse=True)
        return [{"term": term, "strength": round(score, 4)} for term, score in contributions[:5] if score > 0]
    except (AttributeError, KeyError, ValueError):
        return []


def valid_source_url(value):
    """Accept an optional public HTTP(S) URL as contextual metadata only."""
    if not value:
        return ""
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def score_contents(classifier, contents):
    """Score one or more text values and return UI-ready credibility estimates."""
    probabilities = classifier.predict_proba(contents)
    predicted_labels = classifier.predict(contents)
    scores = []
    for probability_row, predicted_label in zip(probabilities, predicted_labels):
        probability_by_class = dict(zip(classifier.classes_, probability_row))
        fake_percentage = round(float(probability_by_class.get("FAKE", 0)) * 100, 2)
        real_percentage = round(float(probability_by_class.get("REAL", 0)) * 100, 2)
        scores.append({
            "result": "FAKE NEWS" if predicted_label == "FAKE" else "REAL NEWS",
            "fake_percentage": fake_percentage,
            "real_percentage": real_percentage,
            "confidence": fake_percentage if predicted_label == "FAKE" else real_percentage,
        })
    return scores


def create_app(model=None):
    """Application factory with optional model injection for tests."""
    load_dotenv(BASE_DIR / ".env")
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["MODEL"] = model if model is not None else load_model()

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_loaded": app.config["MODEL"] is not None})

    @app.get("/api/info")
    def api_info():
        return jsonify({
            "name": "TruthGuard AI",
            "version": "1.0.0",
            "endpoints": {"health": "GET /health", "predict": "POST /predict", "videos": "POST /videos"},
            "limits": {"analysis_characters": 20_000, "video_query_characters": 500},
            "notice": "Predictions are model estimates, not fact checks.",
        })

    @app.post("/predict")
    def predict():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Send a JSON object with news text."}), 400

        title = str(data.get("title", "")).strip()
        body = str(data.get("text", "")).strip()
        query = str(data.get("query", "")).strip()
        source_url = str(data.get("source_url", "")).strip()
        content = query or " ".join(part for part in (title, body) if part)
        if not content:
            return jsonify({"error": "Please enter a headline, article text, or topic."}), 400
        if len(content) > 20_000:
            return jsonify({"error": "Please limit analysis to 20,000 characters."}), 413
        if source_url and not valid_source_url(source_url):
            return jsonify({"error": "Source URL must begin with http:// or https://."}), 400

        classifier = app.config["MODEL"]
        score = score_contents(classifier, [content])[0]
        predicted_label = "FAKE" if score["result"] == "FAKE NEWS" else "REAL"
        signals = get_model_signals(classifier, content, predicted_label)
        return jsonify({
            **score,
            "model_signals": signals,
            "source_url": valid_source_url(source_url),
            "disclaimer": "This is a model estimate, not a fact-check. Verify with reliable sources.",
        })

    @app.post("/videos")
    def videos():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Send a JSON object with a search query.", "videos": []}), 400
        query = str(data.get("query", "")).strip()
        if not query:
            return jsonify({"videos": []})
        if len(query) > 500:
            return jsonify({"error": "Search query is too long.", "videos": []}), 400

        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return jsonify({"videos": [], "message": "Video search is unavailable until a YouTube API key is configured."})

        params = {"part": "snippet", "q": query, "type": "video", "maxResults": 6, "safeSearch": "strict", "key": api_key}
        url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            app.logger.warning("YouTube search request failed", exc_info=True)
            return jsonify({"videos": [], "error": "Unable to fetch related videos right now."}), 502

        video_list = []
        for item in payload.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = next((thumbnails[size].get("url") for size in ("high", "medium", "default") if thumbnails.get(size)), "")
            if video_id:
                video_list.append({
                    "video_id": video_id,
                    "title": snippet.get("title", "Untitled video"),
                    "channel": snippet.get("channelTitle", "YouTube"),
                    "published_at": snippet.get("publishedAt", ""),
                    "thumbnail": thumbnail,
                    "url": f"https://www.youtube.com/watch?v={urllib.parse.quote(video_id, safe='')}",
                })

        # Score each video's public title and channel metadata in a single model call.
        # It is intentionally labelled as a metadata score, not a review of video content.
        if video_list:
            metadata = [f"{video['title']} {video['channel']}" for video in video_list]
            for video, score in zip(video_list, score_contents(app.config["MODEL"], metadata)):
                video["credibility"] = score
                video["credibility_note"] = "Estimate based on the video title and channel text, not the video itself."
        return jsonify({"videos": video_list})

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
