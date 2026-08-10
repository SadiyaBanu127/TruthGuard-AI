const input = document.getElementById("searchInput");
const button = document.getElementById("analyzeButton");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("resultSection");
const message = document.getElementById("formMessage");

button.addEventListener("click", analyzeNews);
input.addEventListener("keydown", (event) => { if (event.key === "Enter") analyzeNews(); });

function showMessage(text = "") { message.textContent = text; }
function setLoading(active) { loading.hidden = !active; button.disabled = active; button.textContent = active ? "Analyzing..." : "Analyze News"; }
function placeholder(text) { const area = document.getElementById("videoResults"); const item = document.createElement("p"); item.className = "video-placeholder"; item.textContent = text; area.replaceChildren(item); }

async function analyzeNews() {
  const query = input.value.trim();
  if (!query) { showMessage("Please enter a news topic or search query."); input.focus(); return; }
  showMessage(""); setLoading(true); resultSection.hidden = true; placeholder("Searching for related news videos...");
  try {
    const response = await fetch("/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prediction failed.");
    renderResult(data); resultSection.hidden = false; loadVideos(query);
  } catch (error) { showMessage(error.message || "Something went wrong. Please try again."); } finally { setLoading(false); }
}

function renderResult(data) {
  const fake = data.result === "FAKE NEWS"; const result = document.getElementById("predictionResult"); result.className = fake ? "prediction-fake" : "prediction-real";
  const heading = document.createElement("h2"); heading.textContent = fake ? "LIKELY FAKE NEWS" : "LIKELY REAL NEWS";
  const text = document.createElement("p"); text.textContent = fake ? "The AI model predicts this information may be misleading." : "The AI model predicts this information is more likely to be real.";
  result.replaceChildren(heading, text);
  document.getElementById("realPercentage").textContent = `${data.real_percentage}%`; document.getElementById("fakePercentage").textContent = `${data.fake_percentage}%`; document.getElementById("confidenceText").textContent = `${data.confidence}%`;
  document.getElementById("confidenceFill").style.width = `${data.confidence}%`; document.getElementById("disclaimer").textContent = data.disclaimer;
}

async function loadVideos(query) { try { const response = await fetch("/videos", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query }) }); const data = await response.json(); if (!response.ok || !data.videos?.length) { placeholder(data.message || data.error || "No related videos found."); return; } document.getElementById("videoResults").replaceChildren(...data.videos.map(videoCard)); } catch { placeholder("Unable to load related videos."); } }
function videoCard(video) { const card = document.createElement("article"); card.className = "video-card"; if (video.thumbnail?.startsWith("https://")) { const image = document.createElement("img"); image.src = video.thumbnail; image.alt = ""; image.loading = "lazy"; card.append(image); } const details = document.createElement("div"); details.className = "video-info"; const title = document.createElement("h3"); title.textContent = video.title; const channel = document.createElement("p"); channel.textContent = `Channel: ${video.channel}`; details.append(title, channel); if (video.published_at) { const date = new Date(video.published_at); const published = document.createElement("p"); published.textContent = `Published: ${Number.isNaN(date.getTime()) ? video.published_at : date.toLocaleDateString()}`; details.append(published); } if (video.credibility) { const score = document.createElement("div"); score.className = `video-score ${video.credibility.result === "FAKE NEWS" ? "video-score-fake" : "video-score-real"}`; const verdict = document.createElement("strong"); verdict.textContent = video.credibility.result === "FAKE NEWS" ? "Likely Fake" : "Likely Real"; const values = document.createElement("span"); values.textContent = `Real: ${video.credibility.real_percentage}% | Fake: ${video.credibility.fake_percentage}%`; score.append(verdict, values); details.append(score); } const link = document.createElement("a"); link.href = video.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = "Watch Video"; details.append(link); card.append(details); return card; }
