document.getElementById('send-btn').addEventListener('click', () => {
    const promptValue = document.getElementById('prompt').value;
    const gallery = document.getElementById('gallery');
    const imageElement = document.getElementById('streamed-image');
    
    // Clear previous results with fade animation
    gallery.style.opacity = '0';
    setTimeout(() => {
        gallery.innerHTML = '';
        gallery.style.opacity = '1';
    }, 300);

    // Create loading spinner
    const loading = document.createElement('div');
    loading.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
            <div class="loading-spinner"></div>
            <div style="color: #fff;">Generating your artwork...</div>
        </div>
    `;
    gallery.appendChild(loading);

    // Show streaming image and interrupt button
    imageElement.style.display = 'block';
    const interruptButton = document.getElementById('interrupt-btn');
    interruptButton.style.display = 'inline-block';

    // Image generation logic
    fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ positive_prompt: promptValue })
    })
    .then(response => response.json())
    .then(data => {
        gallery.innerHTML = '';
        if (data.status === 'success') {
            data.images.forEach(imageUrl => {
                const img = document.createElement('img');
                img.src = imageUrl;
                img.alt = "Generated image";
                img.className = 'gallery-image';
                
                // Improved zoom functionality
                img.addEventListener('click', () => {
                    if (!document.fullscreenElement) {
                        const clone = img.cloneNode();
                        clone.classList.add('fullscreen');
                        document.body.appendChild(clone);
                        
                        clone.onclick = () => clone.remove();
                    }
                });

                // Add fade-in animation
                img.style.opacity = '0';
                gallery.appendChild(img);
                setTimeout(() => img.style.opacity = '1', 50);
            });
        } else {
            const errorMsg = document.createElement('div');
            errorMsg.textContent = `Error: ${data.message}`;
            errorMsg.style.color = '#ff4757';
            errorMsg.style.padding = '1rem';
            gallery.appendChild(errorMsg);
        }
    })
    .catch(err => {
        const errorMsg = document.createElement('div');
        errorMsg.textContent = `Connection error: ${err.message}`;
        errorMsg.style.color = '#ff4757';
        gallery.appendChild(errorMsg);
    })
    .finally(() => {
        interruptButton.style.display = 'none';
        imageElement.style.display = 'none';
    });

    // Interrupt logic
    interruptButton.addEventListener('click', () => {
        fetch("/url").then(response => response.json()).then(data => {
            fetch(`${data.url}/interrupt`, { method: "POST" });
        });
    });

    // Streaming image logic
    fetch("/url").then(response => response.json()).then(data => {
        const baseUrl = data.url.replace(/\/$/, "");
        const updateStreamedImage = () => {
            imageElement.src = `${baseUrl}/stream/image?t=${Date.now()}`;
        };
        setInterval(updateStreamedImage, 1000);
        updateStreamedImage();
    });
});