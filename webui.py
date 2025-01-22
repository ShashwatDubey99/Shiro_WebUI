from flask import Flask, render_template, request, jsonify 
import utils
import random
import os
import ssl 
import json
from flask_cors import CORS


app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
url = "http://127.0.0.1:9191/"
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/easyrun")
def easyrun():  
    return render_template("easyrun.html")
    
@app.route("/gallery")
def galler():  
    return render_template("gallery.html")    
@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.json
        positive_prompt = data.get("positive_prompt", "")

        # Load and update the workflow prompt data
        with open("./workflow_api.json", "r") as file:
            prompt_data = json.load(file)

        # Use main_parse to update the prompt data
        updated_data = utils.main_parse(prompt_data, positive_prompt)

        # Queue the prompt and get the prompt ID
        
        prompt_id = utils.queue_prompt(updated_data, url)

        # Get generated image URLs
        img_list = utils.getimgname(prompt_id, url)

        return jsonify({"status": "success", "images": img_list})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/url", methods=["GET"])
def get_url():
    return jsonify({"url": url})

if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)
