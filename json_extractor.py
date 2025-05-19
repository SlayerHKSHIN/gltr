import json
import re
import ast

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

    def escape_double_quotes(self, obj):
        if isinstance(obj, dict):
            return {k: self.escape_double_quotes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.escape_double_quotes(v) for v in obj]
        elif isinstance(obj, str):
            return obj.replace('"', '\\"')
        else:
            return obj

    def extract_json(self, text):
        # JSON 블록 추출
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return (json.dumps({"error": "No JSON object found in text"}, ensure_ascii=False, indent=2),)

        json_str = json_match.group(0)

        # 1차 시도: json.loads
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            # 2차 시도: ast.literal_eval
            try:
                parsed = ast.literal_eval(json_str)
            except (ValueError, SyntaxError):
                return (json.dumps({"error": "Failed to parse JSON using both json and ast"}, ensure_ascii=False, indent=2),)

        escaped = self.escape_double_quotes(parsed)
        result = json.dumps(escaped, ensure_ascii=False, indent=2)
        return (result,)

