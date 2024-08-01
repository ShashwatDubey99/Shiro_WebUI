from flask import Flask, jsonify, render_template , request ,url_for,redirect
import requests
import utils
import json

app = Flask(__name__,static_folder="static",template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")
with open ("./static/url.txt","r") as file:
    url=file.read()

@app.route('/generate', methods=['POST'])
def generate():
    with open ("./static/url.txt","r") as file:
      url=file.read()
    data = request.json
    print(data)
    model = data.get('model')
    positive = data.get('positive')
    negative = data.get('negative')
    steps = data.get('steps')
    cfg = data.get('cfg')
    aspect = data.get('aspect')
    upscale_factor = data.get('upscale_factor')
    rand = data.get('rand')
    seed = data.get('seed') 
    batch=data.get('batch')
    print(batch)

    # Retrieve your initial JSON template
    with open('./static/api.json',"r+", encoding="utf-8" ) as f:
        template_data = json.load(f)

    # Parse and update the JSON data
    updated_data = utils.main_parse(template_data, model, positive, negative, steps, cfg, aspect, upscale_factor, rand, seed,batch)
    
    # Queue the prompt and get the prompt ID
 
   # Replace with your actual backend URL
    prompt_id = utils.queue_prompt(updated_data, url)
    print(prompt_id)
    # Retrieve the generated image URLs
    image_urls = utils.getimgname(prompt_id, url)
    
    return jsonify({'image_urls': image_urls})



@app.route('/api/get-model-options', methods=['GET'])
def get_model_options():
    with open ("./static/url.txt","r") as file:
       url=file.read()
    
    response=requests.get(url+"/object_info/CheckpointLoaderSimple")

    models=response.json()["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    return jsonify(models)
@app.route('/api/get-aspect-options', methods=['GET'])
def get_aspect_options():
    with open ("./static/url.txt","r") as file:
       url=file.read()
    
    response=requests.get(url+"/object_info/CR Aspect Ratio")

    aspect=response.json()["CR Aspect Ratio"]["input"]["required"]["aspect_ratio"][0]
    return jsonify(aspect)
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        url = request.form['url']
        if url.endswith('/'):
            url = url[:-1]

        with open('./static/url.txt', 'w') as f:
            f.write(url)

        return redirect(url_for('success'))

    return render_template('url.html')

@app.route('/success')
def success():
    return redirect("/")


 
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
