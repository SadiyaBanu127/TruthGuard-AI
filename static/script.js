async function analyzeNews() {

    const searchInput = document.getElementById("searchInput").value.trim();

    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("resultSection");

    const predictionResult = document.getElementById("predictionResult");

    const realPercentage = document.getElementById("realPercentage");
    const fakePercentage = document.getElementById("fakePercentage");

    const confidenceFill = document.getElementById("confidenceFill");
    const confidenceText = document.getElementById("confidenceText");


    // Check empty search
    if (!searchInput) {

        alert("Please enter a news topic or search query.");

        return;
    }


    // Show loading
    loading.style.display = "block";
    resultSection.style.display = "none";


    try {

        /*
        The current ML model expects text.
        We send the user's search query to the Flask backend.
        */

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                title: searchInput,
                text: searchInput
            })

        });


        const data = await response.json();


        loading.style.display = "none";
        resultSection.style.display = "block";


        // Update percentages
        realPercentage.textContent =
            data.real_percentage + "%";

        fakePercentage.textContent =
            data.fake_percentage + "%";


        // Update confidence
        confidenceText.textContent =
            data.confidence + "%";

        confidenceFill.style.width =
            data.confidence + "%";


        // Prediction result
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


        // Temporary video message
        document.getElementById("videoResults").innerHTML = `
            <div class="video-placeholder">
                🎥 Related news videos will appear here.
                <br><br>
                Video search integration will be added next.
            </div>
        `;


    } catch (error) {

        loading.style.display = "none";

        alert("Something went wrong. Please try again.");

        console.error(error);
    }
}