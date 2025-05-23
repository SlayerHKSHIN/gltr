import requests
import json

class GLTRCallLLMAPI:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "base_url": ("STRING", {"default": "http://llm.gltr.app", "tooltip": "Base URL without /v1/..."}),
                "max_tokens": ("INT", {"default": 4096, "min": 1, "max": 35840}),
            }
        }

    RETURN_TYPES = ("CUSTOM",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "GLTR/LLM"

    def load_model(self, api_key, base_url, max_tokens):
        class Model:
            def __init__(self, api_key, base_url, max_tokens):
                self.api_key = api_key
                self.max_tokens = max_tokens
                self.url = base_url.rstrip("/") + "/v1/chat/completions"

            def create_chat_completion(self, messages, temperature, max_tokens, stream=False, **kwargs):
                system_prompt = kwargs.pop("system_prompt", None)
                if system_prompt:
                    if not any(m.get("role") == "system" for m in messages):
                        messages = [{"role": "system", "content": system_prompt}] + messages

                payload = {
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": min(max_tokens, self.max_tokens),
                    "stream": stream,
                    **kwargs
                }

                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }

                try:
                    print("Payload being sent to the API:", json.dumps(payload, indent=4)) 
                    response = requests.post(self.url, headers=headers, json=payload, timeout=120)
                    response.raise_for_status()
                    data = response.json()
                    reply = data["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": reply})
                    return {
                        "response": reply,
                        "history": messages,
                        "reasoning": ""
                    }
                except Exception as e:
                    error_msg = f"GLTR API Error: {e}"
                    print(error_msg)
                    return {
                        "response": error_msg,
                        "history": messages,
                        "reasoning": ""
                    }

            def send(self, user_prompt, temperature, max_length, history,
                     tools, is_tools_in_sys_prompt, images,
                     imgbb_api_key, img_URL, stream, **extra_parameters):
                messages = history if isinstance(history, list) else []
                if user_prompt:
                    messages.append({"role": "user", "content": user_prompt})

                result = self.create_chat_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_length,
                    stream=stream,
                    **extra_parameters
                )
                return result["response"], result["history"], result["reasoning"]

        return (Model(api_key, base_url, max_tokens),)

