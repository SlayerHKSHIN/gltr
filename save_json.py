import json
import os
from datetime import datetime
from pathlib import Path

class SaveJSON:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True}),
            }
        }

    # ⬇️ 출력 타입: 저장된 경로 문자열
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "save"
    CATEGORY = "utils"

    def save(self, json_string):
        # 저장 디렉토리 생성
        base_dir = Path.home() / "ComfyUI" / "output" / "workflow_json"
        base_dir.mkdir(parents=True, exist_ok=True)

        # 실행 시간 기반 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.json"
        filepath = base_dir / filename

        # JSON 파싱 및 저장
        try:
            json_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"[save_json] 유효하지 않은 JSON 문자열입니다: {e}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"[save_json] JSON 저장 완료: {filepath}")
        return (str(filepath),)  # ⬅️ 경로를 문자열로 반환

NODE_CLASS_MAPPINGS = {
    "SaveJSON": SaveJSON
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveJSON": "Save JSON"
}
