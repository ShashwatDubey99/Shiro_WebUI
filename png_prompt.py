import json
import utils
import random
import requests
import urllib

file = open("./workflow_api.json","r")
prompt_text = file.read()
prompt = json.loads(prompt_text)
#set the text prompt for our positive CLIPTextEncode
positive_prompt = input("Enter the positive prompt: ")
negative_prompt = input("Enter the negative prompt: ")
seed=random.randrange(1,4294967296)
url="https://9f227634715297c102bc19f40b3dd546.loophole.site/"
prompt["6"]["inputs"]["text"] = positive_prompt
prompt["3"]["inputs"]["seed"] = seed
prompt["7"]["inputs"]["text"] = negative_prompt
prompt_id=utils.queue_prompt(prompt, url)

img_list=utils.getimgname(prompt_id,url)

#download the image
for i in range(len(img_list)):
    urllib.request.urlretrieve(img_list[i], "./static/"+str(i)+".png")
