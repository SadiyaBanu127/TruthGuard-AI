# 🛡️ TruthGuard AI

### AI-Powered Fake News Detection & News Verification Platform

TruthGuard AI is a full-stack Flask web application that uses Machine Learning to estimate whether submitted news text resembles **real or fake news** based on its training data.

The application also provides **Real/Fake probability percentages, AI confidence, related YouTube news videos, analysis history, downloadable results, and source context** in a modern web interface.

> ⚠️ **Disclaimer:** TruthGuard AI is an educational machine-learning project. It provides an estimated signal based on its training data and should not be treated as a professional fact-checking service.

---

## 🚀 Features

### 🤖 AI News Analysis

- Analyze news claims and article text using Machine Learning.
- Predict whether the submitted information is likely:
  - ✅ Real News
  - ⚠️ Fake News
- Display:
  - Real probability percentage
  - Fake probability percentage
  - AI confidence
  - Model prediction
- Provides model-vocabulary signals for additional context.

### 🔎 Two Analysis Modes

- **Quick Claim Analysis** – Quickly analyze a news claim or topic.
- **Structured Article Analysis** – Analyze more detailed news content.

### 🔗 Source URL Context

- Users can optionally provide the original news source URL.
- The URL is stored as context for the analysis.
- TruthGuard AI does **not automatically fetch or scrape the webpage**.

### 🎥 Related YouTube News Videos

- Searches YouTube for related news videos.
- Uses the **YouTube Data API v3**.
- Displays relevant videos with:
  - Video thumbnail
  - Video title
  - Channel name
  - Published information
  - YouTube link
- Provides estimated Real/Fake percentages and confidence based on available video metadata.
- Uses safe-search settings where supported.

### 📊 Analysis Results

Each analysis can provide:

- Prediction
- Real %
- Fake %
- Confidence level
- Model signals
- Search context

### 📥 Download Results

- Download the analysis result as a JSON file.
- Copy a text summary of the result.

### 🕘 Recent Analysis History

- Keeps recent analysis results in the browser.
- History is stored locally in the current browser.
- No server-side personal history is required.

### 🏥 Health & Service APIs

The application also includes health/service-information API endpoints for checking application availability and service status.

---

# 🛠️ Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Responsive UI

## Backend

- Python
- Flask

## Machine Learning

- Scikit-learn
- Logistic Regression
- TF-IDF / text-based feature processing
- Joblib

## APIs

- YouTube Data API v3

## Other Tools

- Python-dotenv
- Requests
- Git & GitHub

---

# 📂 Project Structure

```text
TruthGuard-AI/
│
├── app.py
├── train_model.py
├── test_app.py
├── requirements.txt
├── README.md
├── news.csv
├── .gitignore
├── .env
│
├── model/
│   └── fake_news_model.pkl
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js