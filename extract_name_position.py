import os
import json

class ExtractNamePosition:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "forceInput": True,
                    "default": "아버지 lee jae myung이 달리기를 한다"
                }),
                "name": ("STRING", {
                    "default": "lee jae myung"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("name", "start", "length")
    FUNCTION = "extract"
    CATEGORY = "GLTR/Text"

    def extract(self, text, name):
        start = text.find(name)
        if start == -1:
            return ("", "0", "0")
        length = len(name)
        return (name, str(start), str(length))
