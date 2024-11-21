async function fetchImages() {
    const url = 'https://civitai.com/api/v1/images?limit=10';
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return response.json();
}

async function displayImages() {
    const data = await fetchImages();
    const gallery = document.getElementById('gallery');
    data.items.forEach(item => {
        const { url, meta } = item;

        const card = document.createElement('div');
        card.classList.add('image-card');

        card.innerHTML = `
            <div class="image-container">
                <img src="${url}" alt="Image">
            </div>
            <div class="prompt-container positive-prompt">
                <div class="prompt-title">Positive Prompt:</div>
                <p>${meta.prompt || 'N/A'}</p>
            </div>
            <div class="prompt-container negative-prompt">
                <div class="prompt-title">Negative Prompt:</div>
                <p>${meta.negativePrompt || 'N/A'}</p>
            </div>
        `;

        gallery.appendChild(card);
    });
}

displayImages();