import utils
from PIL import Image
import json
img=Image.open('ComfyUI_00369_.png')
metadata = img.info['prompt']
keys=utils.get_pos_neg_keys(json.loads(metadata))
print(keys)
prompt=utils.get_prompt(json.loads(metadata),
                        keys["positive_key"],
                        keys["negative_key"])
print(prompt)