function toggleSeedInput() {
    const rand = document.getElementById('rand').checked;
    const seedGroup = document.getElementById('seed-group');
    seedGroup.style.display = rand ? 'none' : 'block';
}

function updateStepsValue(value) {
    document.getElementById('stepsValue').textContent = value;
}
function updateUpValue(value) {
    document.getElementById('UpValue').textContent = value;
}
function updateCfgValue(value) {
    document.getElementById('cfgValue').textContent = value;
}
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/get-model-options')
        .then(response => response.json())
        .then(data => {
            const modelSelect = document.getElementById('model');
            data.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.text = model;
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching model options:', error);
        });
});
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/get-aspect-options')
        .then(response => response.json())
        .then(data => {
            const modelSelect = document.getElementById('aspect');
            data.forEach(aspect => {
                const option = document.createElement('option');
                option.value = aspect;
                option.text = aspect;
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching model options:', error);
        });
});

async function generateImage() {
    const model = document.getElementById('model').value;
    const positive = document.getElementById('positive').value;
    const negative = document.getElementById('negative').value;
    const steps = document.getElementById('steps').value;
    const cfg = document.getElementById('cfg').value;
    const aspect = document.getElementById('aspect').value;
    const upscale_factor = document.getElementById('upscale_factor').value;
    const batch = document.getElementById('batch').value;
    const rand = document.getElementById('rand').checked;
    const seed = rand ? "No" : document.getElementById('seed').value;
    const test = JSON.stringify({
        model, positive, negative, steps, cfg, aspect, upscale_factor, rand, seed,batch,
    });
    console.log(test);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model, positive, negative, steps, cfg, aspect, upscale_factor, rand, seed ,batch
            })
        });

        const data = await response.json();
        console.log(data);

        if (data.image_urls && data.image_urls.length > 0) {
            const outputDiv = document.getElementById('output');
            outputDiv.innerHTML = '';

            data.image_urls.forEach(url => {
                const img = document.createElement('img');
                img.height="512";
                img.src = url;
                img.alt = 'Generated Image';
                img.onload = () => console.log(`Loaded image: ${url}`);
                img.onerror = () => console.error(`Error loading image: ${url}`);
                outputDiv.appendChild(img);
            });
        } else {
            console.error('No images found in response.');
        }
    } catch (error) {
        console.error('Error generating image:', error);
    }
}
const words = ["beautiful", "sunset", "landscape", "portrait", "dream", "abstract", "colorful", "blur", "noise", "artifact", "distorted", "unwanted", "dark", "low-quality"];
let currentFocus = -1;

function showSuggestions(input) {
    const container = input.nextElementSibling;
    container.innerHTML = '';
    const inputValue = input.value.toLowerCase();
    const wordsArray = inputValue.split(' ');
    const lastWord = wordsArray[wordsArray.length - 1];
    if (!lastWord) {
        return;
    }

    words.forEach((word, index) => {
        if (word.toLowerCase().includes(lastWord)) {
            const suggestionDiv = document.createElement('div');
            suggestionDiv.classList.add('autocomplete-suggestion');
            suggestionDiv.textContent = word;
            suggestionDiv.onclick = function() {
                wordsArray[wordsArray.length - 1] = word;
                input.value = wordsArray.join(' ');
                container.innerHTML = '';
                currentFocus = -1;
            };
            container.appendChild(suggestionDiv);
        }
    });

    currentFocus = -1; // Reset focus when new suggestions appear
}

function navigateSuggestions(e) {
    const input = e.target;
    const container = input.nextElementSibling;
    const suggestions = container.getElementsByClassName('autocomplete-suggestion');

    if (e.key === 'ArrowDown') {
        currentFocus++;
        addActive(suggestions);
    } else if (e.key === 'ArrowUp') {
        currentFocus--;
        addActive(suggestions);
    } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        if (currentFocus > -1 && suggestions) {
            suggestions[currentFocus].click();
        } else if (e.key === 'Tab' && suggestions.length > 0) {
            suggestions[0].click();
        }
    }
}

function addActive(suggestions) {
    if (!suggestions) return false;
    removeActive(suggestions);
    if (currentFocus >= suggestions.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = suggestions.length - 1;
    suggestions[currentFocus].classList.add('active');
}

function removeActive(suggestions) {
    for (let i = 0; i < suggestions.length; i++) {
        suggestions[i].classList.remove('active');
    }
}


document.addEventListener('click', function(event) {
    const containers = document.getElementsByClassName('autocomplete-container');
    for (let i = 0; i < containers.length; i++) {
        const container = containers[i];
        if (!container.contains(event.target)) {
            const suggestions = container.getElementsByClassName('autocomplete-suggestions')[0];
            suggestions.innerHTML = '';
        }
    }
});
