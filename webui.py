from flask import Flask, jsonify, render_template , request ,url_for,redirect
import requests
import utils
import json
'''
Whoever is reading this I feel sorry for you but i can't write better code 
than this so , if you can just make a PR and I will Accept it (If it works)

'''

app = Flask(__name__,static_folder="static",template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")
with open ("./static/url.txt","r") as file:
    #IDK What The fuck i am doing with Urls But its working (KINDA.. Yeh..kinda)
    URL=file.read()

@app.route('/generate', methods=['POST'])
def generate():
    with open ("./static/url.txt","r") as file:
      URL=file.read()
    data = request.json

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
  
    #Prompt Parsing and returning the urls for Images 
    with open('./static/api.json',"r+", encoding="utf-8" ) as f:
        template_data = json.load(f)
    updated_data = utils.main_parse(template_data, model, positive, negative, steps, cfg, aspect, upscale_factor, rand, seed,batch)
    prompt_id = utils.queue_prompt(updated_data, URL)
    print(prompt_id)
    image_urls = utils.getimgname(prompt_id, URL)
    
    return jsonify({'image_urls': image_urls})



@app.route('/api/get-model-options', methods=['GET'])
def get_model_options():
    with open ("./static/url.txt","r") as file:
     URL=file.read()
    
    response=requests.get(URL+"/object_info/CheckpointLoaderSimple")

    models=response.json()["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    return jsonify(models)


@app.route('/api/get-aspect-options', methods=['GET'])
def get_aspect_options():
    with open ("./static/url.txt","r") as file:
       URL=file.read()
    
    response=requests.get(URL+"/object_info/CR Aspect Ratio")

    aspect=response.json()["CR Aspect Ratio"]["input"]["required"]["aspect_ratio"][0]
    return jsonify(aspect)

@app.route('/api/get-upscale-models', methods=['GET'])
def UpScaleModels():

    return jsonify(utils.Up())

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


@app.route('/geturl')
def url():
    with open ("./static/url.txt","r") as file:
     URL=file.read()
     return jsonify(URL)
    

@app.route('/gallary')
def gallary():
    return render_template('gallary.html')



@app.route('/outputs')
def out():
    with open ("./static/url.txt","r") as file:
       URL=file.read()
    response=requests.get(f"{URL}/outputs")
    return jsonify(response.json())


@app.route('/delete_image', methods=['POST'])
def delete_image():
    with open ("./static/url.txt","r") as file:
        URL=file.read()
    from flask import request
    image_name = request.json.get('filename')
    if not image_name:
        return jsonify({'error': 'filename is required'}), 400
    print(image_name)
    delete_url = f"{URL}/api/outputs/{image_name}"
    response = requests.delete(delete_url)
    
    if response.status_code == 200:
        return jsonify({'message': 'Image deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete image'}), response.status_code

 
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
