
# comfyui/custom_nodes/ComfyUI-gltr/gltr_image_search.py
import requests
import json
import numpy as np
from PIL import Image
from io import BytesIO
import torch

class gltr_image_search:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "query": ("STRING", {"default": "Joe Biden"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("image", "filename_prefix",)
    FUNCTION = "search_and_load"
    CATEGORY = "Google"

    def search_and_load(self, query):
        api_key = "AIzaSyAbQOZX4l0nRHEgTcamjQXHmP-OdU3jprE"
        search_engine_id = "b784d29a3fee44f02"
        search_url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": api_key,
            "cx": search_engine_id,
            "searchType": "image",
            "q": query,
            "num": 1,
            "imgSize": "large",
            "safe": "off"
        }

        response = requests.get(search_url, params=params)
        data = response.json()

        print("[gltr_image_search] Response JSON:")
        print(json.dumps(data, indent=2))

        if "items" not in data or len(data["items"]) == 0:
            raise Exception("No image found for query: " + query)

        image_url = data["items"][0]["link"]
        print("[gltr_image_search] Image URL:", image_url)

        image_response = requests.get(image_url)
        image_pil = Image.open(BytesIO(image_response.content)).convert("RGB")

        image_np = np.array(image_pil).astype(np.float32) / 255.0  # (H, W, C)
        image_tensor = torch.from_numpy(image_np).unsqueeze(0)  # ✅ (1, H, W, C)

        return (image_tensor, query)

