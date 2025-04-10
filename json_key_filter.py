import json

class JSONKeyFilter:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {f"json{i+1}": ("STRING", {"multiline": True, "default": ""}) for i in range(10)}
        inputs["keys"] = ("STRING", {"multiline": True, "default": "name,age"})
        return {"required": inputs}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "filter_keys"
    CATEGORY = "GLTR Utils"

    def filter_keys(self, **kwargs):
        keys = kwargs["keys"].replace(" ", "").split(",")
        merged = {}

        for i in range(10):
            json_str = kwargs.get(f"json{i+1}", "").strip()
            if json_str:
                try:
                    data = json.loads(json_str)
                    for k in keys:
                        if k in data:
                            # 기존은 단일 값만 추출 → 여기서 Nested dict도 허용
                            merged[k] = data[k]
                except json.JSONDecodeError:
                    continue

        output = json.dumps([merged], ensure_ascii=False, indent=2)
        return (output,)
