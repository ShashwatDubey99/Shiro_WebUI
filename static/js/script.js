document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector(".container");
    const apiUrl = "https://civitai.com/api/v1/images?nsfw=true&";
    let nextCursor = null; // Track the next cursor for pagination

    // Function to fetch image data from the API
    async function fetchImageData(limit = 10) {
        const params = new URLSearchParams({ limit });
        if (nextCursor) {
            params.append("cursor", nextCursor);
        }
        const url = `${apiUrl}?${params.toString()}`;

        try {
            const response = await fetch(url, { headers: { "Content-Type": "application/json" } });
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            const data = await response.json();
            nextCursor = data.metadata?.nextCursor || null; // Update the cursor for the next fetch
            return data.items; // Return the items array
        } catch (error) {
            console.error("Error fetching image data:", error);
            return [];
        }
    }

    // Function to create a single Hall of Fame entry
    function createHallOfFameEntry(imageData) {
        // Create main Hall of Fame div
        const hallOfFameDiv = document.createElement("div");
        hallOfFameDiv.className = "hall-of-fame";

        // Create image container
        const imgContainer = document.createElement("div");
        imgContainer.className = "img-container";
        const img = document.createElement("img");
        img.src = imageData.url;
        img.alt = `Image by ${imageData.username}`;
        imgContainer.appendChild(img);

        // Create text content container
        const textContent = document.createElement("div");
        textContent.className = "text-content";

        // Positive prompt section
        const positivePromptTitle = document.createElement("h2");
        positivePromptTitle.textContent = "Positive Prompt:";
        const positivePromptText = document.createElement("div");
        positivePromptText.className = "text1";
        const positivePrompt = imageData.meta?.prompt || "N/A";
        positivePromptText.textContent = positivePrompt.length > 200 ? positivePrompt.slice(0, 200) + "..." : positivePrompt;
        positivePromptText.title = positivePrompt;
        positivePromptText.addEventListener("click", () => {
            navigator.clipboard.writeText(positivePrompt);
            alert("Positive prompt copied!");
        });

        // Negative prompt section
        const negativePromptTitle = document.createElement("h2");
        negativePromptTitle.textContent = "Negative Prompt:";
        const negativePromptText = document.createElement("div");
        negativePromptText.className = "text2";
        const negativePrompt = imageData.meta?.negativePrompt || "N/A";
        negativePromptText.textContent = negativePrompt.length > 200 ? negativePrompt.slice(0, 200) + "..." : negativePrompt;
        negativePromptText.title = negativePrompt;
        negativePromptText.addEventListener("click", () => {
            navigator.clipboard.writeText(negativePrompt);
            alert("Negative prompt copied!");
        });

        // Append text content
        textContent.appendChild(positivePromptTitle);
        textContent.appendChild(positivePromptText);
        textContent.appendChild(negativePromptTitle);
        textContent.appendChild(negativePromptText);

        // Append image and text containers to the Hall of Fame div
        hallOfFameDiv.appendChild(imgContainer);
        hallOfFameDiv.appendChild(textContent);

        return hallOfFameDiv;
    }

    // Function to load images
    async function loadImages() {
        const images = await fetchImageData(10);

        if (images.length === 0) {
            loadMoreButton.textContent = "No More Images";
            loadMoreButton.disabled = true;
            return;
        }

        images.forEach(imageData => {
            const hallOfFameEntry = createHallOfFameEntry(imageData);
            container.appendChild(hallOfFameEntry);
        });
    }

    // Create "Load More" button
    const loadMoreButton = document.createElement("button");
    loadMoreButton.textContent = "Load More";
    loadMoreButton.className = "load-more";
    loadMoreButton.addEventListener("click", loadImages);

    // Add the Load More button to the container
    container.appendChild(loadMoreButton);

    // Initial load
    loadImages();
});

