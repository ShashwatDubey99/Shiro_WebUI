import os
import json
from PIL import Image

def read_exif_and_create_json(image_path):

    img = Image.open(image_path)



    metadata = img.info

    if "workflow" in metadata:
        workflow_value = metadata["workflow"]

        try:
            workflow_dict = json.loads(workflow_value)
            print(workflow_dict['nodes'][17]['widgets_values'][0])
        except json.JSONDecodeError:
            print(f"Pata Nahi {image_path}")
            return

        if workflow_dict:
            
            json_file_path = os.path.splitext(image_path)[0] + ".json"
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(workflow_dict, json_file, ensure_ascii=False, indent=1)  

            print(f"--> {image_path}")
