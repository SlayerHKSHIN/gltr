import json
import re

class JSONExtractor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_json"
    CATEGORY = "GLTR Utils"

    def extract_json(self, text):
        # 정규식으로 { } 블록 추출 (가장 바깥 쌍 기준)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return ("",)

        json_str = json_match.group(0)

        try:
            parsed = json.loads(json_str)  # 유효한 JSON인지 확인
            result = json.dumps(parsed, ensure_ascii=False, indent=2)  # 포맷팅해서 반환
            return (result,)
        except json.JSONDecodeError:
            return ("",)

