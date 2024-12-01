document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector(".container");
    const sidebar = document.createElement("div");
    sidebar.className = "sidebar";

    // Default API URL
    let currentApiUrl = "https://civitai.com/api/v1/images?sort=Newest";
    let nextCursor = null;

    // Function to fetch image data from the API
    async function fetchImageData(limit = 10) {
        const params = new URLSearchParams({ limit });
        if (nextCursor) {
            params.append("cursor", nextCursor);
        }
        const url = `${currentApiUrl}&${params.toString()}`;

        try {
            const response = await fetch(url, { headers: { "Content-Type": "application/json" } });
            if (!response.ok) throw new Error(`Error: ${response.statusText}`);
            const data = await response.json();
            nextCursor = data.metadata?.nextCursor || null;
            return data.items;
        } catch (error) {
            console.error("Error fetching image data:", error);
            return [];
        }
    }

    // Function to create a single Hall of Fame entry
    function createHallOfFameEntry(imageData) {
        const hallOfFameDiv = document.createElement("div");
        hallOfFameDiv.className = "hall-of-fame";

        const imgContainer = document.createElement("div");
        imgContainer.className = "img-container";
        const img = document.createElement("img");
        img.src = imageData.url;
        img.alt = `Image by ${imageData.username}`;
        imgContainer.appendChild(img);

        const textContent = document.createElement("div");
        textContent.className = "text-content";

        const positivePromptTitle = document.createElement("h2");
        positivePromptTitle.textContent = "Positive Prompt:";
        const positivePromptText = document.createElement("div");
        positivePromptText.className = "text1";
        const positivePrompt = imageData.meta?.prompt || "N/A";
        positivePromptText.textContent = positivePrompt.length > 200 ? positivePrompt.slice(0, 200) + "..." : positivePrompt;
        positivePromptText.title = positivePrompt;
        positivePromptText.addEventListener("click", () => {
            navigator.clipboard.writeText(positivePrompt);
            showCopiedMessage();
        });

        const negativePromptTitle = document.createElement("h2");
        negativePromptTitle.textContent = "Negative Prompt:";
        const negativePromptText = document.createElement("div");
        negativePromptText.className = "text2";
        const negativePrompt = imageData.meta?.negativePrompt || "N/A";
        negativePromptText.textContent = negativePrompt.length > 200 ? negativePrompt.slice(0, 200) + "..." : negativePrompt;
        negativePromptText.title = negativePrompt;
        negativePromptText.addEventListener("click", () => {
            navigator.clipboard.writeText(negativePrompt);
            showCopiedMessage();
        });

        textContent.appendChild(positivePromptTitle);
        textContent.appendChild(positivePromptText);
        textContent.appendChild(negativePromptTitle);
        textContent.appendChild(negativePromptText);

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
   
    // Create a sidebar with API options
    const apis = [
        { name: "Safe", url: "https://civitai.com/api/v1/images?sort=Newest" },
        { name: "X)", url: "https://civitai.com/api/v1/images?sort=Newest&nsfw=true" },
        
    ];

    apis.forEach(api => {
        const button = document.createElement("button");
        button.textContent = api.name;
        button.className = "api-button";
        button.addEventListener("click", () => {
            currentApiUrl = api.url; // Update the API URL
            nextCursor = null; // Reset pagination
            container.innerHTML = ""; // Clear current images
            container.appendChild(loadMoreButton); // Re-add Load More button
            loadImages(); // Load new images
        });
        sidebar.appendChild(button);
    });

    document.body.appendChild(sidebar);
    

    // Initial load
    loadImages();
    const loadMoreButton = document.createElement("button");
    loadMoreButton.textContent = "Load More";
    loadMoreButton.className = "load-more";
    loadMoreButton.addEventListener("click", loadImages);

    container.appendChild(loadMoreButton);

});

// Function to show a temporary "Text Copied" message
function showCopiedMessage() {
    const message = document.createElement("div");
    message.className = "copied-message";
    message.textContent = "Text Copied!";

    Object.assign(message.style, {
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        backgroundColor: "#333",
        color: "#fff",
        padding: "10px 20px",
        borderRadius: "5px",
        fontSize: "16px",
        zIndex: "1000",
        opacity: "0",
        transition: "opacity 0.3s",
    });

    document.body.appendChild(message);

    requestAnimationFrame(() => {
        message.style.opacity = "1";
    });

    setTimeout(() => {
        message.style.opacity = "0";
        setTimeout(() => message.remove(), 300);
    }, 1000);
}
