# TruthGuard AI

TruthGuard AI is a full-stack Flask web app that provides a local machine-learning estimate of whether submitted news text resembles the real or fake examples in its training data. It is an educational signal, **not** a fact-checking service.

## Features

- Quick-claim and structured article analysis modes
- Optional source URL captured as context, without fetching the page
- Real/fake probability estimate, confidence level, and model-vocabulary signals
- Downloadable JSON result and copyable text summary
- Recent analysis history stored only in the current browser
- Optional YouTube related-video search with safe search enabled; each result shows Real %, Fake %, verdict, and confidence based on its title/channel metadata
- Health and service-information API endpoints

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Train (or refresh) the local model: `python train_model.py`
4. Start the site: `python app.py`
5. Open `http://127.0.0.1:5000`.

## Optional video search

Create a `.env` file in the project root containing:

```env
YOUTUBE_API_KEY=your_key_here
```

Without a key, claim analysis still works; the related-video area simply explains that video search is unavailable.

## Validate

Run the automated endpoint checks with:

```bash
python -m unittest -v
```

The sample training dataset is intentionally small. Before relying on this project beyond a demonstration, replace it with a large, representative, well-labeled dataset and evaluate the model for accuracy, bias, and drift.
