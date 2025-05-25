import os
import json

class StrengthFinder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_character": ("STRING", {"default": ""}),
                "lora_style": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("strength_character", "strength_style")
    FUNCTION = "find_strength"
    CATEGORY = "GLTR/LoRA"

    CANDIDATE_JSON_PATHS = [
        "~/ComfyUI/custom_nodes/gltr/best_strength_result_full.json",
        "~/ComfyUI/custom_nodes/ComfyUI-gltr/best_strength_result_full.json"
    ]

    def __init__(self):
        self.json_data = None
        self.last_path = None

    def resolve_json_path(self):
        for path in self.CANDIDATE_JSON_PATHS:
            real_path = os.path.expanduser(path)
            if os.path.exists(real_path):
                return real_path
        raise FileNotFoundError(f"None of the candidate files exist: {self.CANDIDATE_JSON_PATHS}")

    def load_json(self):
        path = self.resolve_json_path()
        if self.last_path == path and self.json_data is not None:
            return self.json_data
        with open(path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f)
        self.last_path = path
        return self.json_data

    def find_strength(self, lora_character, lora_style):
        data = self.load_json()
        for key, val in data.items():
            if val["lora_character"] == lora_character and val["lora_style"] == lora_style:
                return (
                    str(val["strength_character"]),
                    str(val["strength_style"]),
                )
        # Not found fallback
        return (
            "1.4",
            "ask_llm",
        )
