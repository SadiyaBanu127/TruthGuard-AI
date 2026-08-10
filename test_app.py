import os
import json
import unittest
from unittest.mock import patch

from app import create_app


class FakeModel:
    classes_ = ["FAKE", "REAL"]

    def predict_proba(self, texts):
        return [[0.2, 0.8] for _ in texts]

    def predict(self, texts):
        return ["REAL" for _ in texts]


class TruthGuardTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(model=FakeModel()).test_client()
        self.previous_key = os.environ.pop("YOUTUBE_API_KEY", None)

    def tearDown(self):
        if self.previous_key:
            os.environ["YOUTUBE_API_KEY"] = self.previous_key

    def test_home_and_health(self):
        self.assertEqual(self.app.get("/").status_code, 200)
        response = self.app.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_api_info_describes_service(self):
        response = self.app.get("/api/info")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["name"], "TruthGuard AI")
        self.assertEqual(payload["limits"]["analysis_characters"], 20_000)

    def test_predict_returns_percentages(self):
        response = self.app.post("/predict", json={"query": "Scientists publish a report."})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"], "REAL NEWS")
        self.assertEqual(payload["real_percentage"], 80.0)
        self.assertIn("disclaimer", payload)
        self.assertIn("model_signals", payload)

    def test_predict_rejects_empty_and_oversized_input(self):
        self.assertEqual(self.app.post("/predict", json={}).status_code, 400)
        self.assertEqual(self.app.post("/predict", json={"query": "a" * 20_001}).status_code, 413)
        self.assertEqual(
            self.app.post("/predict", json={"query": "a claim", "source_url": "ftp://example.com"}).status_code,
            400,
        )

    def test_predict_returns_valid_source_url(self):
        response = self.app.post("/predict", json={"query": "A report", "source_url": "https://example.com/report"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["source_url"], "https://example.com/report")

    def test_videos_without_key_is_graceful(self):
        response = self.app.post("/videos", json={"query": "climate news"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["videos"], [])

    def test_videos_include_real_fake_percentages(self):
        class YouTubeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({"items": [{
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Scientists publish a report",
                        "channelTitle": "Trusted Channel",
                        "publishedAt": "2026-08-10T12:00:00Z",
                        "thumbnails": {"default": {"url": "https://example.com/image.jpg"}},
                    },
                }]}).encode("utf-8")

        os.environ["YOUTUBE_API_KEY"] = "test-key"
        with patch("app.urllib.request.urlopen", return_value=YouTubeResponse()):
            response = self.app.post("/videos", json={"query": "science news"})

        self.assertEqual(response.status_code, 200)
        video = response.get_json()["videos"][0]
        self.assertEqual(video["credibility"]["real_percentage"], 80.0)
        self.assertEqual(video["credibility"]["fake_percentage"], 20.0)
        self.assertEqual(video["credibility"]["result"], "REAL NEWS")
        self.assertEqual(video["published_at"], "2026-08-10T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
