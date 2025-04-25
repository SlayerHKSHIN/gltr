
# comfyui/custom_nodes/ComfyUI-gltr/gltr_image_search.py
import requests
import json
import numpy as np
from PIL import Image, ImageFile
from io import BytesIO
import gzip
import torch

ImageFile.LOAD_TRUNCATED_IMAGES = True

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
            "num": 5,
            "imgSize": "large",
            "imgType": "face",
            "safe": "off"
            # ⛔ rights 필터 제거됨
        }

        response = requests.get(search_url, params=params)
        data = response.json()

        if "items" not in data or len(data["items"]) == 0:
            raise Exception("No image found for query: " + query)

        for item in data["items"]:
            image_url = item.get("link")
            mime_type = item.get("mime", "")
            display_link = item.get("displayLink", "")

            if mime_type not in ["image/jpeg", "image/png"]:
                continue
            if "youtube.com" in image_url or "ytimg.com" in image_url or "youtube" in display_link:
                continue

            try:
                image_response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
                if image_response.status_code != 200:
                    continue
                if "image" not in image_response.headers.get("Content-Type", ""):
                    continue

                raw_bytes = image_response.content
                if image_response.headers.get("Content-Encoding") == "gzip":
                    raw_bytes = gzip.decompress(raw_bytes)

                image_pil = Image.open(BytesIO(raw_bytes)).convert("RGB")
                image_np = np.array(image_pil).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np).unsqueeze(0)

                return (image_tensor, query)

            except Exception:
                continue

        raise Exception("No valid image matching the constraints was found for query: " + query)
