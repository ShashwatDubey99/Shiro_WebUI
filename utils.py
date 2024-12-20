import json
import requests
import urllib
import time
import random
from PIL import Image
'''
Whoever is reading this I feel sorry for you but i can't write better code 
than this so , if you can just make a PR and I will Accept it (If it works)

'''


def getimgname(prompt_id,url):
      URL=url
      print(prompt_id)
      respons=requests.get(url+"/history")
      while prompt_id not in respons.json():
          respons=requests.get(url+"/history")
          time.sleep(1)
      print(respons.json())
      f=(respons.json()[prompt_id]["outputs"]["9"]["images"])
      a=[]
      for i in f:
          filename = i["filename"]
          subfolder = i["subfolder"]
          folder_type = i["type"]
          z=(URL+"view?"+get_image(filename, subfolder, folder_type))
          a.append(URL+"view?"+get_image(filename, subfolder, folder_type))
      print( a)    
      return a    

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    return url_values

#api json as prompt
def queue_prompt(prompt, url):
    p = {"prompt": prompt}
    
    data = json.dumps(p).encode('utf-8')
    req = requests.post(f"{url}/prompt", data=data)
    global prompt_id
    print(req.json())
    prompt_id = req.json()["prompt_id"]
    return prompt_id

def find_node_id_by_title(data, title):
    for key, value in data.items():
        if value.get('_meta', {}).get('title') == title:
            return key
    return None
def main_parse(data,Model,Positive,Negetive,steps,cfg , Aspect,upscale_factor,rand,seed,batch):
    data[find_node_id_by_title(data,'Model')]["inputs"]["ckpt_name"]=Model
    data[get_pos_neg_keys(data)["positive_key"]]["inputs"]["text"]=Positive
    data[get_pos_neg_keys(data)["negative_key"]]["inputs"]["text"]=Negetive
    data[find_node_id_by_title(data,"AYS")]["inputs"]["steps"]=steps
    data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["cfg"]=cfg
    if seed=="No":
        data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["noise_seed"]=random.randrange(1,4294967296)
    else:
        data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["noise_seed"]=seed
    data[find_node_id_by_title(data,"Aspect")]["inputs"]["batch_size"]=int(batch)
    return data

def download_img(url):
    response = requests.get(url)
    if response.status_code == 200:
        with open("./static/upscale/input.png", 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}") 
def get_meta_img(img_path):
   
    img = Image.open(img_path)
    metadata = img.info['prompt']
    return metadata  
def Up():
    with open ("./static/url.txt","r") as file:
       URL=file.read()
    
       response=requests.get(URL+"/object_info/CR Aspect Ratio")

       modelsUP=response.json()["UpscaleModelLoader"]["input"]["model_name"]["aspect_ratio"][0]
       return modelsUP
    
#takes dict
def get_pos_neg_keys(img_metadata):
    positive_key=None
    negative_key=None
    for key, value in img_metadata.items():
        if "inputs" in value:
            inputs = value["inputs"]
            if "positive" in inputs:
                positive_key = inputs["positive"][0]
            if "negative" in inputs:
                negative_key = inputs["negative"][0]
    return {"positive_key": positive_key, "negative_key": negative_key}



def get_prompt(data, positive_key, negative_key):
    positive=data[positive_key]["inputs"]["text"]
    negative=data[negative_key]["inputs"]["text"]
    return {"positive": positive, "negative": negative}

    
   