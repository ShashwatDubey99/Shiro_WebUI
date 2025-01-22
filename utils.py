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

def clean_prompt(prompt: str) -> Tuple[str, Dict]:
    """
    Extract parameters and remove them from the prompt
    Returns tuple of (cleaned_prompt, parameters_dict)
    """
    params = {
        'cfg': 7.0,
        'steps': 25,
        'batch_size': 1,
        'seed': random.randint(1, 0xFFFFFFFF)
    }

    # Regex pattern to find parameters
    param_pattern = re.compile(
        r'(?i)(cfg|steps|batch_size|seed)\s*[:=]?\s*([\d.]+)',
        re.IGNORECASE
    )

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

    # Clean up prompt
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()
    return clean_prompt, params

def find_positive_negative_nodes(workflow: Dict) -> Tuple[str, str]:
    """Find positive and negative prompt nodes based on KSampler connections"""
    try:
        # Find KSampler node
        sampler_node = next(
            node for node in workflow.values() 
            if node.get('class_type') == 'KSampler'
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
            if node.get('class_type') == 'KSampler'
        )
        
        latent_node_id = next(
            node_id for node_id, node in workflow.items()
            if node.get('class_type') == 'EmptyLatentImage'
        )
        
        pos_id, neg_id = find_positive_negative_nodes(workflow)

        # Update KSampler parameters
        workflow[sampler_node_id]['inputs'].update({
            'seed': params['seed'],
            'cfg': params['cfg'],
            'steps': params['steps']
        })

        # Update latent image batch size
        workflow[latent_node_id]['inputs']['batch_size'] = params['batch_size']

        # Update prompts
        workflow[pos_id]['inputs']['text'] = clean_prompt
        workflow[neg_id]['inputs']['text'] = "text, watermark"

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
        history_url = f"{base_url}/history"

        # Wait for prompt to appear in history
        while True:
            response = requests.get(history_url)
            response.raise_for_status()
            if prompt_id in response.json():
                break
            time.sleep(6)

        # Get outputs from node 9
        outputs = response.json()[prompt_id]["outputs"]
        images_data = outputs["9"]["images"]
        
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