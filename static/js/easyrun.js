document.getElementById('send-btn').addEventListener('click', () => {
    const promptValue = document.getElementById('prompt').value;
    const gallery = document.getElementById('gallery');
    const imageElement = document.getElementById('streamed-image');
    
    gallery.innerHTML = ''; // Clear previous results

    // Hide the reconstructed image while generating
    const reconstructedImage = document.getElementById('reconstructed-image');
    if (reconstructedImage) {
        reconstructedImage.style.display = 'none'; // Hide the reconstructed image
    }

    // Create a loading spinner
    const loading = document.createElement('div');
    loading.textContent = 'Generating...';
    loading.style.color = '#ffffff';
    gallery.appendChild(loading);

    // Show the streaming image and the interrupt button
    imageElement.style.display = 'block'; // Show the streaming image
    const interruptButton = document.createElement('button');
    interruptButton.textContent = 'Interrupt Generation';
    gallery.appendChild(interruptButton);

    // Start the image generation
    fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ positive_prompt: promptValue })
    })
    .then(response => response.json())
    .then(data => {
        gallery.innerHTML = ''; // Clear loading message
        if (data.status === 'success') {
            data.images.forEach(imageUrl => {
                // Create a new image element for each generated image
                const img = document.createElement('img');
                img.src = imageUrl;
                img.alt = "Generated image";
                img.style.margin = "10px";
                img.style.borderRadius = "8px";
                img.style.width = "200px";
                img.style.height = "auto";
                img.style.transition = "all 0.3s ease"; // Smooth transition

                // Add click event to toggle fullscreen
                img.addEventListener('click', () => {
                    if (img.classList.contains('fullscreen')) {
                        img.classList.remove('fullscreen');
                        img.style.position = '';
                        img.style.transform = '';
                        img.style.width = '200px';
                        img.style.height = 'auto';
                        img.style.zIndex = '';
                    } else {
                        img.classList.add('fullscreen');
                        img.style.position = 'fixed';
                        img.style.top = '50%';
                        img.style.left = '50%';
                        img.style.transform = 'translate(-50%, -50%)';
                        img.style.width = '80%';
                        img.style.height = 'auto';
                        img.style.zIndex = '9999';
                    }
                });

                // Add the generated image to the gallery
                gallery.appendChild(img);
            });
        } else {
            // Display an error message if the generation failed
            const errorMsg = document.createElement('div');
            errorMsg.textContent = `Error: ${data.message}`;
            errorMsg.style.color = 'red';
            gallery.appendChild(errorMsg);
        }

        // Hide the interrupt button and streaming image after image generation
        interruptButton.style.display = 'none';
        imageElement.style.display = 'none';
    })
    .catch(err => {
        gallery.innerHTML = ''; // Clear loading message
        const errorMsg = document.createElement('div');
        errorMsg.textContent = `Error: ${err.message}`;
        errorMsg.style.color = 'red';
        gallery.appendChild(errorMsg);

        // Hide the interrupt button and streaming image if error occurs
        interruptButton.style.display = 'none';
        imageElement.style.display = 'none';
    });

    // Interrupt logic
    interruptButton.addEventListener('click', () => {
        fetch("/url", { method: "GET" })
            .then(response => response.json())
            .then(data => {
                const baseUrl = data.url.replace(/\/$/, ""); // Remove trailing slash

                // Send the interrupt request
                fetch(`${baseUrl}/interrupt`, { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Interrupt signal sent:', data);
                        // Hide the interrupt button and streaming image after interrupt
                        interruptButton.style.display = 'none';
                        imageElement.style.display = 'none';
                    })
                    .catch(err => {
                        console.error('Error sending interrupt:', err);
                    });
            });
    });

    // Stream image while generating
    fetch("/url", { method: "GET" })
        .then(response => response.json())
        .then(data => {
            const baseUrl = data.url.replace(/\/$/, ""); // Remove trailing slash

            // Function to update the image
            function updateStreamedImage() {
                const timestamp = new Date().getTime(); // Add a timestamp to bypass caching
                imageElement.src = `${baseUrl}/stream/image?t=${timestamp}`;
            }

            // Update the image every 2 seconds
            setInterval(updateStreamedImage, 500);

            // Initial image load
            updateStreamedImage();
        });
});
