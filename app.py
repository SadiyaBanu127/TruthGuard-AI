from flask import Flask, render_template, request, jsonify
import joblib
import os
import json
import urllib.parse
import urllib.request

app = Flask(__name__)

# ==============================
# LOAD FAKE NEWS MODEL
# ==============================

model = joblib.load("model/fake_news_model.pkl")


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# FAKE NEWS PREDICTION
# ==============================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json() or {}

    # Accept title + text
    title = data.get("title", "").strip()
    text = data.get("text", "").strip()

    # Also support a single search query
    query = data.get("query", "").strip()

    if query:
        news_content = query
    else:
        news_content = title + " " + text

    if not news_content.strip():
        return jsonify({
            "error": "Please enter some news or topic."
        }), 400

    # ==============================
    # PREDICTION PROBABILITY
    # ==============================

    probabilities = model.predict_proba([news_content])[0]
    classes = model.classes_

    probability_dict = dict(zip(classes, probabilities))

    fake_percentage = probability_dict.get("FAKE", 0) * 100
    real_percentage = probability_dict.get("REAL", 0) * 100

    prediction = model.predict([news_content])[0]

    if prediction == "FAKE":
        result = "FAKE NEWS"
        confidence = fake_percentage
    else:
        result = "REAL NEWS"
        confidence = real_percentage

    return jsonify({
        "result": result,
        "fake_percentage": round(fake_percentage, 2),
        "real_percentage": round(real_percentage, 2),
        "confidence": round(confidence, 2)
    })


# ==============================
# LOAD YOUTUBE API KEY
# ==============================

def get_api_key():

    # First check system environment
    api_key = os.getenv("YOUTUBE_API_KEY")

    if api_key:
        return api_key

    # Read .env manually
    if os.path.exists(".env"):

        with open(".env", "r", encoding="utf-8") as file:

            for line in file:
                line = line.strip()

                if line.startswith("YOUTUBE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None


# ==============================
# RELATED YOUTUBE VIDEOS
# ==============================

@app.route("/videos", methods=["POST"])
def videos():

    data = request.get_json() or {}

    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "videos": []
        })

    api_key = get_api_key()

    if not api_key:
        return jsonify({
            "videos": [],
            "error": "YouTube API key not configured."
        })

    # YouTube Search API
    api_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 6,
        "key": api_key
    }

    try:

        url = api_url + "?" + urllib.parse.urlencode(params)

        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

        video_list = []

        for item in result.get("items", []):

            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            thumbnails = snippet.get("thumbnails", {})

            if "high" in thumbnails:
                thumbnail = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                thumbnail = thumbnails["medium"]["url"]
            else:
                thumbnail = thumbnails["default"]["url"]

            video_list.append({
                "video_id": video_id,
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "thumbnail": thumbnail,
                "url": "https://www.youtube.com/watch?v=" + video_id
            })

        return jsonify({
            "videos": video_list
        })

    except Exception as error:

        print("YouTube Error:", error)

        return jsonify({
            "videos": [],
            "error": "Unable to fetch YouTube videos."
        })


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":
    app.run(debug=True)