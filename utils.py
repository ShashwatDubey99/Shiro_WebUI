import json
import requests
import urllib
import time
import random
from PIL import Image
def getimgname(prompt_id,url):
      URL=url
      
      print(prompt_id)
      respons=requests.get(url+"/history")
      while prompt_id not in respons.json():
          respons=requests.get(url+"/history")
          time.sleep(1)
      print(respons.json())
      f=(respons.json()[prompt_id]["outputs"]["16"]["images"])
      a=[]
      for i in f:
          filename = i["filename"]
          subfolder = i["subfolder"]
          folder_type = i["type"]
          z=(URL+"/"+"view?"+get_image(filename, subfolder, folder_type))
          a.append(URL+"/"+"view?"+get_image(filename, subfolder, folder_type))
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
    prompt_id = req.json()["prompt_id"]
    return prompt_id

def find_node_id_by_title(data, title):
    for key, value in data.items():
        if value.get('_meta', {}).get('title') == title:
            return key
    return None
def main_parse(data,Model,Positive,Negetive,steps,cfg , Aspect,upscale_factor,rand,seed,batch):
    data[find_node_id_by_title(data,'Model')]["inputs"]["ckpt_name"]=Model
    data[find_node_id_by_title(data,"Positive")]["inputs"]["text"]=Positive
    data[find_node_id_by_title(data,"Negetive")]["inputs"]["text"]=Negetive
    data[find_node_id_by_title(data,"AYS")]["inputs"]["steps"]=steps
    data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["cfg"]=cfg
    if rand=="No":
        data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["noise_seed"]=seed
    else:
        data[find_node_id_by_title(data,"SamplerCustom")]["inputs"]["noise_seed"]=random.randrange(1,4294967296)
    data[find_node_id_by_title(data,"Aspect")]["inputs"]["aspect_ratio"]=Aspect  
    data[find_node_id_by_title(data,"Aspect")]["inputs"]["prescale_factor"]=float(upscale_factor)
    data[find_node_id_by_title(data,"Aspect")]["inputs"]["batch_size"]=int(batch)
    return data

def download_img(url):
    response = requests.get(url)
    if response.status_code == 200:
        with open("./static/upscale/input.png", 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}") 
def get_workflow_img(img_path):
   
    img = Image.open(img_path)
    metadata = img.info
    return metadata    
def Quick2xUp():
    with open ("./static/upscale.json","r+") as file:
        data = file.json()
    data[find_node_id_by_title(data,'Model')]["inputs"]["ckpt_name"]=Model
    data[find_node_id_by_title(data,"Positive")]["inputs"]["text"]=Positive
    data[find_node_id_by_title(data,"Negetive")]["inputs"]["text"]=Negetive
    data[find_node_id_by_title(data,"UpModel")]["inputs"]["model_name"]=UpModel

    return data
    
