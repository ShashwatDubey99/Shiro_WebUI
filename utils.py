import json
import requests
import urllib
import time
import random
import re
import logging
from typing import Dict, Tuple ,List
import urllib.parse
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComfyUIError(Exception):
    """Custom exception for ComfyUI interaction errors"""
    pass
def get_loras_list(url: str) -> List:

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ComfyUIError(f"Failed to retrieve list from {url}: {str(e)}")
def clean_prompt(prompt: str, url: str) -> Tuple[str, Dict]:
    """
    Extract parameters and remove them from the prompt
    Returns tuple of (cleaned_prompt, parameters_dict)
    """
    params = {
        'cfg': 5.0,
        'steps': 25,
        'batch_size': 1,
        'seed': random.randint(1, 0xFFFFFFFF),
        'lora': None,
        'model_strength': 0.0,
        'clip_strength': 0.0,
        'width': 512,
        'height': 512,
        'scale': 1.0
    }

    # Regex pattern to find parameters
    param_pattern = re.compile(
        r'(?i)(cfg|steps|batch_size|seed)\s*[:=]?\s*([\d.]+)',
        re.IGNORECASE
    )

    # Regex pattern for LoRA flag with optional strengths
    lora_pattern = re.compile(r'(?i)-l\s+([\w.:-]+)')
    # Regex patterns for -p and -s flags
    p_pattern = re.compile(r'(?i)-p\s+(\d+)x(\d+)')
    s_pattern = re.compile(r'(?i)-s\s+([\d.]+)')

    # Remove found parameters from prompt and collect values
    clean_prompt = prompt
    for match in param_pattern.finditer(prompt):
        full_match = match.group(0)
        key = match.group(1).lower()
        value = match.group(2)
        
        try:
            if key == 'cfg':
                params[key] = float(value)
            elif key in ['steps', 'batch_size']:
                params[key] = max(1, int(float(value)))
            elif key == 'seed':
                params['seed'] = int(float(value))
            clean_prompt = clean_prompt.replace(full_match, '')
        except ValueError as e:
            logger.warning(f"Invalid parameter value: {full_match} - {str(e)}")

    # Extract LoRA parameter
    lora_match = lora_pattern.search(clean_prompt)
    if lora_match:
        lora_spec = lora_match.group(1)
        parts = lora_spec.split(':')
        params['lora'] = parts[0]
        if len(parts) > 1:
            try:
                params['model_strength'] = float(parts[1])
            except ValueError:
                pass
        if len(parts) > 2:
            try:
                params['clip_strength'] = float(parts[2])
            except ValueError:
                pass
        clean_prompt = clean_prompt.replace(lora_match.group(0), '', 1)

    # Process -p parameter (width x height)
    p_match = p_pattern.search(clean_prompt)
    if p_match:
        width_str = p_match.group(1)
        height_str = p_match.group(2)
        try:
            params['width'] = int(width_str)
            params['height'] = int(height_str)
        except ValueError as e:
            logger.warning(f"Invalid width/height in -p flag {p_match.group(0)}: {str(e)}")
        clean_prompt = clean_prompt.replace(p_match.group(0), '', 1)

    # Process -s parameter (scale)
    s_match = s_pattern.search(clean_prompt)
    if s_match:
        scale_str = s_match.group(1)
        try:
            params['scale'] = float(scale_str)
        except ValueError as e:
            logger.warning(f"Invalid scale in -s flag {s_match.group(0)}: {str(e)}")
        clean_prompt = clean_prompt.replace(s_match.group(0), '', 1)

    # Set default lora from the list if not specified
    if params['lora'] is None:
        try:
            loras_list = get_loras_list(url + "models/loras")
            if loras_list:
                params['lora'] = loras_list[0]
            else:
                logger.warning(f"No LoRAs found at {url}")
        except ComfyUIError as e:
            logger.warning(f"Could not fetch LoRA list: {str(e)}")

    # Apply scale to width and height
    params['width'] = int(params['width'] * params['scale'])
    params['height'] = int(params['height'] * params['scale'])

    # Clean up prompt
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()
    return clean_prompt, params
def find_positive_negative_nodes(workflow: Dict) -> Tuple[str, str]:
    """Find positive and negative prompt nodes based on KSampler connections"""
    try:
        # Find KSampler node
        sampler_node = next(
            node for node in workflow.values() 
            if node.get('class_type') == 'SamplerCustom'
        )
        
        positive_id = sampler_node['inputs']['positive'][0]
        negative_id = sampler_node['inputs']['negative'][0]
        
        return positive_id, negative_id
        
    except (KeyError, StopIteration) as e:
        raise ComfyUIError("Could not find prompt nodes in workflow") from e

def update_workflow(workflow: Dict, clean_prompt: str, params: Dict) -> Dict:
    """Update workflow with cleaned prompt and parameters"""
    try:
        # Find nodes
        sampler_node_id = next(
            node_id for node_id, node in workflow.items()
            if node.get('class_type') == 'SamplerCustom'
        )
        AYS_node_id = next(
            node_id for node_id, node in workflow.items()
            if node.get('class_type') == 'AlignYourStepsScheduler'
        )
        
        latent_node_id = next(
            node_id for node_id, node in workflow.items()
            if node.get('class_type') == 'EmptyLatentImage'
        )
        lora_node_id= next(
            node_id for node_id, node in workflow.items()
            if node.get('class_type') == 'LoraLoader'
        )
        
        pos_id, neg_id = find_positive_negative_nodes(workflow)

        # Update KSampler parameters
        workflow[sampler_node_id]['inputs'].update({
            'noise_seed': params['seed'],
            'cfg': params['cfg'],
          
        })

        workflow[AYS_node_id]['inputs']['steps'] = params['steps']

        # Update latent image batch size
        workflow[latent_node_id]['inputs']['batch_size'] = params['batch_size']
        workflow[latent_node_id]['inputs']['width'] = params['width']
        workflow[latent_node_id]['inputs']['height'] = params['height']

        # Update prompts
        workflow[pos_id]['inputs']['text'] = replace_with_json_values(clean_prompt)
        workflow[neg_id]['inputs']['text'] = "low quality"
        workflow[lora_node_id]['inputs']['lora_name'] = params['lora'].replace(".safetensors","")+".safetensors"
        workflow[lora_node_id]['inputs']['strength_model'] = params['model_strength']
        workflow[lora_node_id]['inputs']['strength_clip"'] = params['clip_strength']

        return workflow

    except (KeyError, StopIteration) as e:
        raise ComfyUIError(f"Missing required workflow node: {str(e)}") from e

def queue_prompt(prompt: Dict, comfyui_url: str) -> str:
    """Submit prompt to ComfyUI and return prompt ID"""
    try:
        response = requests.post(
            f"{comfyui_url.rstrip('/')}/prompt",
            json={"prompt": prompt},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["prompt_id"]
    except requests.exceptions.RequestException as e:
        raise ComfyUIError(f"Failed to queue prompt: {str(e)}")

def getimgname(prompt_id, url):
    """Retrieve image URLs from ComfyUI with basic error handling"""
    try:
        base_url = url.rstrip('/')
        history_url = f"{base_url}/history/{prompt_id}"

        # Wait for prompt to appear in history
        while True:
            response = requests.get(history_url)
            response.raise_for_status()
            if prompt_id in response.json():
                break
            time.sleep(6)

        # Get outputs from node 9
        outputs = response.json()[prompt_id]["outputs"]
        images_data = next(
            (output["images"] for output in outputs.values() if "images" in output),
            []
        )
        
        # Build URLs
        return [
            f"{base_url}/view?{get_image(img['filename'], img.get('subfolder', ''), img['type'])}"
            for img in images_data
        ]

    except Exception as e:
        print(f"Error retrieving images: {str(e)}")
        return []

def get_image(filename, subfolder, folder_type):
    """URL parameter encoding helper"""
    return urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": folder_type
    })
def replace_with_json_values(text):
    """Replace specific words with values from a JSON file"""
    with open("template.json", "r", encoding="utf-8") as f:
        replacements = json.load(f)

    for key, value in replacements.items():
        text = text.replace(key, value.strip())

    return text