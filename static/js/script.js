document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector(".container");
    let currentFilters = {
        limit: 100,
        nsfw: null,
        sort: 'Newest',
        period: 'AllTime',
        postId: null,
        modelId: null,
        modelVersionId: null,
        username: null,
        cursor: null
    };
    let nextCursor = null;
    let isLoading = false;

    // DOM Elements
    const toggleButton = document.querySelector(".toggle-sidebar");
    const sidebar = document.querySelector(".sidebar");
    const filterElements = {
        limit: document.getElementById("limit"),
        nsfw: document.getElementById("nsfw"),
        sort: document.getElementById("sort"),
        period: document.getElementById("period"),
        postId: document.getElementById("postId"),
        modelId: document.getElementById("modelId"),
        modelVersionId: document.getElementById("modelVersionId"),
        username: document.getElementById("username")
    };

    // Initialize filters from elements
    Object.entries(filterElements).forEach(([key, element]) => {
        if (element) element.value = currentFilters[key] || '';
    });

    // Event Listeners
    toggleButton?.addEventListener("click", () => {
        sidebar.classList.toggle("visible");
        container.classList.toggle("shifted");
    });

    document.querySelector(".apply-filters")?.addEventListener("click", applyFilters);
    window.addEventListener("scroll", handleScroll);

    // API Functions
    async function fetchImageData() {
        if (isLoading) return;
        isLoading = true;
        
        const params = new URLSearchParams();
        
        // Add validated parameters
        Object.entries(currentFilters).forEach(([key, value]) => {
            if (value !== null && value !== '') {
                params.append(key, value);
            }
        });

        try {
            const response = await fetch(`https://civitai.com/api/v1/images?${params.toString()}`);
            const data = await response.json();
            nextCursor = data.metadata?.nextCursor || null;
            return data.items;
        } catch (error) {
            console.error("Error fetching images:", error);
            showError("Failed to load images");
            return [];
        } finally {
            isLoading = false;
        }
    }

    // Filter Application
    function applyFilters() {
        currentFilters = {
            ...currentFilters,
            limit: parseInt(filterElements.limit.value) || 100,
            nsfw: filterElements.nsfw.value || null,
            sort: filterElements.sort.value || 'Newest',
            period: filterElements.period.value || 'AllTime',
            postId: filterElements.postId.value || null,
            modelId: filterElements.modelId.value || null,
            modelVersionId: filterElements.modelVersionId.value || null,
            username: filterElements.username.value || null
        };

        nextCursor = null;
        container.innerHTML = "";
        loadImages();
    }

    // UI Functions
    function createHallOfFameEntry(item) {
        const entry = document.createElement("div");
        entry.className = "hall-of-fame";
        
        entry.innerHTML = `
            <div class="img-container">
                <img src="${item.url}" 
                     alt="Image by ${item.username}" 
                     loading="lazy" 
                     decoding="async">
            </div>
            <div class="text-content">
                <div class="meta-info">
                    <div>Model: ${item.meta?.Model || 'N/A'}</div>
                    <div>User: ${item.username || 'Anonymous'}</div>
                    <div>Date: ${new Date(item.createdAt).toLocaleDateString()}</div>
                </div>
                ${createPromptSection('Positive Prompt', item.meta?.prompt)}
                ${createPromptSection('Negative Prompt', item.meta?.negativePrompt)}
            </div>
        `;

        entry.querySelectorAll(".prompt-content").forEach(el => {
            el.addEventListener("click", () => copyToClipboard(el.textContent));
        });

        return entry;
    }

    function createPromptSection(title, content) {
        return `
            <div class="prompt-group">
                <h3>${title}</h3>
                <div class="prompt-content" title="${content || 'N/A'}">
                    ${content?.substring(0, 200) || 'N/A'}${content?.length > 200 ? '...' : ''}
                </div>
            </div>
        `;
    }

    // Utility Functions
    async function loadImages() {
        const items = await fetchImageData();
        items.forEach(item => {
            container.appendChild(createHallOfFameEntry(item));
        });
    }

    function handleScroll() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadImages();
        }
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text);
        showCopiedMessage();
    }

    function showCopiedMessage() {
        const msg = document.createElement("div");
        msg.className = "copied-message";
        msg.textContent = "Copied to clipboard!";
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 1000);
    }

    function showError(message) {
        const errorDiv = document.createElement("div");
        errorDiv.className = "error-message";
        errorDiv.textContent = message;
        container.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }

    // Initial Load
    loadImages();
});