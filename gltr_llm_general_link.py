import requests
import json
import difflib
import os
import re
import uuid
import datetime
from langdetect import detect
from unidecode import unidecode
from transliterate import translit

import os
import json
import uuid
import datetime
import requests

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
                    "default": "http://llm.gltr.app",
                }),
                "api_key": ("STRING", {
                    "default": "",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 1.5, "step": 0.1,
                }),
                "max_tokens": ("INT", {
                    "default": 512, "min": 1, "max": 35840,
                }),
                "force_recompute": ("BOOLEAN", {"default": True}),
                "use_rag": ("STRING", {
                    "default": "No",
                    "forceInput": True,
                    "multiline": False,
                    "tooltip": "Use RAG? Enter 'Yes' or 'No'."
                }),
            },
            "optional": {
                "rag_file_path": ("STRING", {
                    "multiline": False,
                    "default": "~/ComfyUI/gltr-data/character-lora-list.txt",
                }),
                "rag_query": ("STRING", {
                    "multiline": False,
                    "default": "",
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "call_llm"
    CATEGORY = "GLTR/LLM"

    def call_llm(
        self, system_prompt, user_prompt, api_url, api_key,
        temperature, max_tokens, force_recompute, use_rag,
        rag_file_path=None, rag_query=None
    ):
        if not api_url.endswith("/v1/chat/completions"):
            api_url = api_url.rstrip("/") + "/v1/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["X-API-Key"] = api_key

        if force_recompute:
            system_prompt += f"\n[recompute:{uuid.uuid4()}]"

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # === RAG 후보 파일 직접 읽어서 candidates로 전송 ===
        rag_candidates = None
        if use_rag == "Yes" and rag_file_path:
            expanded_path = os.path.expanduser(rag_file_path)
            try:
                with open(expanded_path, "r", encoding="utf-8") as f:
                    rag_candidates = json.load(f)
                print(f"[GLTR][RAG] 후보 리스트 파일 로딩 성공: {expanded_path}")
            except Exception as e:
                print(f"[GLTR][RAG] 후보 리스트 파일 로딩 실패: {e}")
                rag_candidates = []

            payload["rag_candidates"] = rag_candidates
            if rag_query:
                payload["rag_query"] = rag_query

        # ---------- 로그 ----------
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now}] [GLTRLLMGeneralLink] API 호출 시작")
        print(f"API URL: {api_url}")
        print(f"Headers: {headers}")
        print(f"Payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")
        with open('/tmp/gltr_llm_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"\n[{now}] [GLTRLLMGeneralLink] API 호출 시작\n")
            f.write(f"API URL: {api_url}\nHeaders: {headers}\n")
            f.write(f"Payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            try:
                data = response.json()
                print(f"[{now}] [GLTRLLMGeneralLink] API 응답:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
                with open('/tmp/gltr_llm_debug.log', 'a', encoding='utf-8') as f:
                    f.write(f"[{now}] [GLTRLLMGeneralLink] API 응답:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
                if "choices" in data and "message" in data["choices"][0] and "content" in data["choices"][0]["message"]:
                    return (data["choices"][0]["message"]["content"].strip(),)
                else:
                    return (f"[ERROR] Unexpected structure:\n{json.dumps(data, indent=2)}",)
            except Exception as e:
                return (f"[ERROR] JSON decode error:\n{response.text}\nException: {str(e)}",)
        except requests.exceptions.RequestException as e:
            return (f"[ERROR] API connection failed:\n{str(e)}",)


import os
import json
import difflib
import re
from unidecode import unidecode
# from langdetect import detect   # langdetect, translit 필요 시 주석 해제

class UniversalNameMatcher:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {}),
                "start": ("STRING", {"default": "0"}),
                "length": ("STRING", {"default": "0"}),
                "name_list_path": ("STRING", {"default": "~/ComfyUI/gltr-data/list_character_names.json"}),
                "lora_file_list_path": ("STRING", {"default": "~/ComfyUI/gltr-data/list_character_lora.json"}),
                "threshold": ("FLOAT", {"default": 0.8})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("matched_result_json",)
    FUNCTION = "match"
    CATEGORY = "GLTR"

    def normalize(self, name):
        if not name:
            return ""
        # langdetect/translit이 필요하면 주석 해제
        # try:
        #     lang = detect(name)
        #     if lang in ['ru', 'el']:
        #         return translit(name, reversed=True)
        # except:
        #     pass
        # 핵심: 언더스코어, 공백, 대소문자, diacritic 모두 제거
        return unidecode(name).replace(" ", "").replace("_", "").lower()

    def match(self, name, start, length, name_list_path, lora_file_list_path, threshold):
        print("[UniversalNameMatcher] match() started")
        print(f"name={name}, start={start}, length={length}")
        name_list_path = os.path.expanduser(name_list_path)
        lora_file_list_path = os.path.expanduser(lora_file_list_path)

        try:
            start = int(start)
            length = int(length)
        except Exception as e:
            print("[WARNING] start/length conversion failed")
            start = 0
            length = 0

        # 이름 리스트 읽기
        try:
            with open(name_list_path, "r", encoding="utf-8") as f:
                name_list = json.load(f)
            print(f"[DEBUG] Loaded {len(name_list)} names from JSON")
        except Exception as e:
            print(f"[ERROR] Failed to read name list JSON: {e}")
            return (json.dumps({"model": "", "start": "0", "length": "0"}),)

        normalized_input = self.normalize(name)
        print(f"[DEBUG] Normalized input: {normalized_input}")

        best_match = ""
        best_score = 0
        for candidate in name_list:
            norm_candidate = self.normalize(candidate)
            score = difflib.SequenceMatcher(None, normalized_input, norm_candidate).ratio()
            print(f"[DEBUG] Comparing '{normalized_input}' <-> '{norm_candidate}' | score={score:.3f}")
            if score > best_score:
                best_score = score
                best_match = candidate

        print(f"[DEBUG] Best match: {best_match} (score={best_score:.3f})")
        if best_score < threshold:
            print(f"[WARNING] Best match score too low: {best_score:.3f} < {threshold}")
            return (json.dumps({"model": "", "start": str(start), "length": str(length)}),)

        # LoRA 파일 리스트 읽기
        try:
            with open(lora_file_list_path, "r", encoding="utf-8") as f:
                lora_files = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read lora file list JSON: {e}")
            return (json.dumps({"model": "", "start": "0", "length": "0"}),)

        def normalize_all(name):
            return unidecode(name).replace(" ", "").replace("_", "").lower()

        norm_best_match = normalize_all(best_match)
        matching_files = [
            file for file in lora_files
            if norm_best_match in normalize_all(file)
        ]
        print(f"[DEBUG] norm_best_match: {norm_best_match}")
        print(f"[DEBUG] Found {len(matching_files)} matching files.")

        def extract_step_number(filename):
            match = re.search(r"step(\d+)", filename)
            return int(match.group(1)) if match else -1

        selected_file = ""
        if matching_files:
            matching_files_with_step = [f for f in matching_files if extract_step_number(f) >= 0]
            if matching_files_with_step:
                matching_files_with_step.sort(key=lambda f: extract_step_number(f), reverse=True)
                selected_file = matching_files_with_step[0]
            else:
                selected_file = matching_files[0]
            print(f"[DEBUG] Selected file: {selected_file}")

        if not selected_file:
            print(f"[UniversalNameMatcher] No matching files found for name: {best_match}")

        return (json.dumps({"model": selected_file, "start": str(start), "length": str(length)}),)

