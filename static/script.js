async function analyzeNews() {

    const searchInput = document.getElementById("searchInput").value.trim();

    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("resultSection");

    const predictionResult = document.getElementById("predictionResult");

    const realPercentage = document.getElementById("realPercentage");
    const fakePercentage = document.getElementById("fakePercentage");

    const confidenceFill = document.getElementById("confidenceFill");
    const confidenceText = document.getElementById("confidenceText");

    const videoResults = document.getElementById("videoResults");


    // ==============================
    // CHECK EMPTY SEARCH
    // ==============================

    if (!searchInput) {
        alert("Please enter a news topic or search query.");
        return;
    }


    // ==============================
    // SHOW LOADING
    // ==============================

    loading.style.display = "block";
    resultSection.style.display = "none";

    videoResults.innerHTML = `
        <div class="video-placeholder">
            🎥 Searching for related news videos...
        </div>
    `;


    try {

        // ==============================
        // AI FAKE NEWS PREDICTION
        // ==============================

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                title: searchInput,
                text: searchInput,
                query: searchInput
            })

        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }


        // ==============================
        // SHOW RESULT
        // ==============================

        loading.style.display = "none";
        resultSection.style.display = "block";


        // Real percentage
        realPercentage.textContent =
            data.real_percentage + "%";


        // Fake percentage
        fakePercentage.textContent =
            data.fake_percentage + "%";


        // Confidence
        confidenceText.textContent =
            data.confidence + "%";

        confidenceFill.style.width =
            data.confidence + "%";


        // ==============================
        // PREDICTION RESULT
        // ==============================

        if (data.result === "FAKE NEWS") {

            predictionResult.className = "prediction-fake";

            predictionResult.innerHTML = `
                <h2>⚠️ LIKELY FAKE NEWS</h2>
                <p>
                    The AI model predicts that this information
                    may be misleading.
                </p>
            `;

        } else {

            predictionResult.className = "prediction-real";

            predictionResult.innerHTML = `
                <h2>✅ LIKELY REAL NEWS</h2>
                <p>
                    The AI model predicts that this information
                    is more likely to be real.
                </p>
            `;
        }


        // ==============================
        // FETCH RELATED YOUTUBE VIDEOS
        // ==============================

        try {

            const videoResponse = await fetch("/videos", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    query: searchInput
                })

            });


            const videoData = await videoResponse.json();


            if (
                videoResponse.ok &&
                videoData.videos &&
                videoData.videos.length > 0
            ) {

                videoResults.innerHTML = "";


                videoData.videos.forEach(video => {

                    const videoCard = document.createElement("div");

                    videoCard.className = "video-card";


                    videoCard.innerHTML = `
                        <img
                            src="${video.thumbnail}"
                            alt="News video thumbnail"
                            class="video-thumbnail"
                        >

                        <div class="video-info">

                            <h3>${escapeHTML(video.title)}</h3>

                            <p>
                                📺 ${escapeHTML(video.channel)}
                            </p>

                            <a
                                href="${video.url}"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="watch-video"
                            >
                                ▶ Watch Video
                            </a>

                        </div>
                    `;


                    videoResults.appendChild(videoCard);

                });


            } else {

                videoResults.innerHTML = `
                    <div class="video-placeholder">
                        🎥 No related videos found.
                    </div>
                `;

            }


        } catch (videoError) {

            console.error("YouTube error:", videoError);

            videoResults.innerHTML = `
                <div class="video-placeholder">
                    🎥 Unable to load related videos.
                </div>
            `;

        }


    } catch (error) {

        loading.style.display = "none";

        console.error("Analysis error:", error);

        alert(
            error.message ||
            "Something went wrong. Please try again."
        );
    }
}


// ==============================
// SECURITY HELPER
// ==============================

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}