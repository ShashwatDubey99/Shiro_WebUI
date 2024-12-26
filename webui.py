from flask import Flask, render_template, request, jsonify
import utils
import random
import os
import ssl 
import json
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/easyrun")
def easyrun():  
    return render_template("easyrun.html")
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
        url = "https://2f7752bd42e07dedf8c2b52ac07c60e6.loophole.site/"
        prompt_id = utils.queue_prompt(updated_data, url)

        # Get generated image URLs
        img_list = utils.getimgname(prompt_id, url)

        return jsonify({"status": "success", "images": img_list})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)
