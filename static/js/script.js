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
                <p class="prompt-content" data-prompt="${meta.prompt || ''}">
                    ${meta.prompt ? meta.prompt.slice(0, 100) : 'N/A'}
                </p>
            </div>
            <div class="prompt-container negative-prompt">
                <div class="prompt-title">Negative Prompt:</div>
                <p class="prompt-content" data-prompt="${meta.negativePrompt || ''}">
                    ${meta.negativePrompt ? meta.negativePrompt.slice(0, 100) : 'N/A'}
                </p>
            </div>
        `;

        card.querySelectorAll('.prompt-content').forEach(prompt => {
            prompt.addEventListener('mouseover', showPopup);
            prompt.addEventListener('mouseout', hidePopup);
            prompt.addEventListener('click', copyToClipboard);
        });

        gallery.appendChild(card);
    });
}

function showPopup(event) {
    const fullText = event.target.dataset.prompt;
    if (!fullText) return;

    const popup = document.createElement('div');
    popup.className = 'popup';
    popup.innerText = fullText;

    document.body.appendChild(popup);

    const rect = popup.getBoundingClientRect();
    popup.style.left = `calc(50% - ${rect.width / 2}px)`;
    popup.style.top = `calc(50% - ${rect.height / 2}px)`;

    event.target.dataset.popupId = popup;
}

function hidePopup(event) {
    const popup = document.querySelector('.popup');
    if (popup) popup.remove();
}

function copyToClipboard(event) {
    const text = event.target.dataset.prompt;
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        const copiedPopup = document.createElement('div');
        copiedPopup.className = 'copied-popup';
        copiedPopup.innerText = 'Copied!';
        document.body.appendChild(copiedPopup);

        // Center the copied popup
        const rect = copiedPopup.getBoundingClientRect();
        copiedPopup.style.left = `calc(50% - ${rect.width / 2}px)`;
        copiedPopup.style.top = `calc(50% - ${rect.height / 2}px)`;

        setTimeout(() => copiedPopup.remove(), 1500);
    });
}

displayImages();
