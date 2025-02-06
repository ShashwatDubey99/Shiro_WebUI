from flask import Flask, render_template, request, jsonify
import utils
import json

import logging
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Configuration
COMFYUI_URL = "http://127.0.0.1:9191/"
url=COMFYUI_URL
WORKFLOW_PATH = "./workflow_api.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/easyrun")
def easyrun():
    return render_template("easyrun.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        # Validate input
        data = request.get_json()
        if not data or "positive_prompt" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required 'positive_prompt' field"
            }), 400

        raw_prompt = data["positive_prompt"].strip()
        if not raw_prompt:
            return jsonify({
                "status": "error",
                "message": "Empty prompt provided"
            }), 400

        # Clean prompt and extract parameters
        clean_prompt, params = utils.clean_prompt(raw_prompt,url)
        logger.info(f"Processing prompt: '{raw_prompt}' -> Cleaned: '{clean_prompt}'")

        # Load workflow template
        try:
            with open("./workflow_api.json", "r") as f:
                workflow = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow template: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Server configuration error"
            }), 500

        # Update workflow with cleaned prompt and parameters
        try:
            updated_workflow = utils.update_workflow(
                workflow=workflow,
                clean_prompt=clean_prompt,
                params=params
            )
        except utils.ComfyUIError as e:
            logger.error(f"Workflow update failed: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to configure image generation"
            }), 500

        # Submit to ComfyUI
        try:
            prompt_id = utils.queue_prompt(updated_workflow, url)
            logger.info(f"Started generation with ID: {prompt_id}")
        except utils.ComfyUIError as e:
            logger.error(f"Generation failed to start: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to start image generation"
            }), 500

        # Retrieve generated images
        try:
            images = utils.getimgname(prompt_id, url)
            logger.info(f"Retrieved {len(images)} images")
        except utils.ComfyUIError as e:
            logger.error(f"Failed to retrieve images: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to retrieve generated images"
            }), 500

        return jsonify({
            "status": "success",
            "images": images,
            "parameters": {
                "clean_prompt": clean_prompt,
                "cfg": params["cfg"],
                "steps": params["steps"],
                "batch_size": params["batch_size"],
                "seed": params["seed"]
            }
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
@app.route("/url", methods=["GET"])
def get_comfyui_url():
    return jsonify({"url": COMFYUI_URL})

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )