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

    def strip_json_block(self, text):
        # 코드블록 전체 제거 (앞/뒤 줄바꿈도 함께)
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)

    def fix_common_escape(self, s):
        try:
            return s.encode().decode('unicode_escape')
        except Exception:
            return s  # 이스케이프가 필요 없으면 원본 유지

    def extract_json(self, text):
        # 1. 코드블록 등 불필요한 것 제거
        text = self.strip_json_block(text)

        # 2. 중간에 여러 JSON이 있을 수도 있음. 가장 큰 블록 추출
        json_match = re.search(r'\{[\s\S]*\}', text)
        if not json_match:
            return (json.dumps({"error": "No JSON object found in text"}, ensure_ascii=False, indent=2),)

        json_str = json_match.group(0).strip()

        # 3. 이스케이프 등 자주 깨지는 것 보정
        json_str_fixed = self.fix_common_escape(json_str)

        # 4. 파싱 시도 (여러 전략)
        parsed = None
        for try_json in [json_str_fixed, json_str, json_str.replace("'", '"')]:
            try:
                parsed = json.loads(try_json)
                break
            except Exception:
                try:
                    parsed = ast.literal_eval(try_json)
                    break
                except Exception:
                    continue

        if parsed is None:
            return (json.dumps({"error": "Failed to parse JSON using all strategies"}, ensure_ascii=False, indent=2),)

        # 5. 이스케이프된 쌍따옴표 등 보정
        result = json.dumps(parsed, ensure_ascii=False, indent=2)
        return (result,)
