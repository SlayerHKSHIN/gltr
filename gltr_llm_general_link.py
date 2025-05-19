import requests
import json

class GLTRLLMGeneralLink:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "forceInput": True,
                    "default": "You are a helpful assistant.",
                }),
                "user_prompt": ("STRING", {
                    "multiline": True,
                    "forceInput": True,
                    "default": "What is the capital of France?",
                }),
                "api_url": ("STRING", {
                    "default": "http://localhost:30000",
                }),
                "api_key": ("STRING", {
                    "default": "",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 1.5, "step": 0.1,
                }),
                "max_tokens": ("INT", {
                    "default": 512, "min": 1, "max": 4096,
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "call_llm"
    CATEGORY = "GLTR/LLM"

    def call_llm(self, system_prompt, user_prompt, api_url, api_key, temperature, max_tokens):
        if not api_url.endswith("/v1/chat/completions"):
            api_url = api_url.rstrip("/") + "/v1/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["X-API-Key"] = api_key

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            try:
                data = response.json()
                if "choices" in data and "message" in data["choices"][0] and "content" in data["choices"][0]["message"]:
                    return (data["choices"][0]["message"]["content"].strip(),)
                else:
                    return (f"[ERROR] Unexpected structure:\n{json.dumps(data, indent=2)}",)
            except Exception as decode_error:
                return (f"[ERROR] JSON decode error:\n{response.text}",)

        except requests.exceptions.RequestException as e:
            return (f"[ERROR] API connection failed:\n{str(e)}",)

