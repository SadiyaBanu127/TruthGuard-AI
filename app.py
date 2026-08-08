from flask import Flask, render_template, request, jsonify
import joblib

app = Flask(__name__)

# Load trained model
model = joblib.load("model/fake_news_model.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    title = data.get("title", "").strip()
    text = data.get("text", "").strip()

    news_content = title + " " + text

    # Get prediction probabilities
    probabilities = model.predict_proba([news_content])[0]

    # Get class names
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


if __name__ == "__main__":
    app.run(debug=True)