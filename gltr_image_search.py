import requests
import json
import numpy as np
from PIL import Image, ImageFile
from io import BytesIO
import gzip
import torch
import cv2

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

    @staticmethod
    def count_faces(image_pil):
        cv_img = np.array(image_pil)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        return len(faces)

    @staticmethod
    def get_leftmost_face_crop(image_pil):
        cv_img = np.array(image_pil)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) == 0:
            return None

        # 왼쪽 얼굴 기준: x 좌표가 가장 작은 얼굴
        faces_sorted = sorted(faces, key=lambda rect: rect[0])
        x, y, w, h = faces_sorted[0]

        # 패딩 추가
        padding = 15
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(cv_img.shape[1] - x, w + 2 * padding)
        h = min(cv_img.shape[0] - y, h + 2 * padding)

        cropped = cv_img[y:y+h, x:x+w]
        cropped_pil = Image.fromarray(cropped).convert("RGB")
        return cropped_pil

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
                num_faces = self.count_faces(image_pil)

                if num_faces == 0:
                    continue
                else:
                    image_pil = self.get_leftmost_face_crop(image_pil)
                    if image_pil is None:
                        continue

                image_np = np.array(image_pil).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np).unsqueeze(0)

                return (image_tensor, query)

            except Exception:
                continue

        raise Exception("No valid image matching the constraints was found for query: " + query)

