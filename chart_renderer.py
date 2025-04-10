import os
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import torch
from io import BytesIO
from PIL import Image

class ChartRenderer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_input": ("STRING", {"multiline": True}),  # JSON 문자열 입력
                "chart_key": ("STRING", {"default": "chart_idea_1"}),  # 선택할 차트 키
                "output_filename": ("STRING", {"default": "chart_output.png"}),  # 출력 파일명
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "render_chart"
    CATEGORY = "Chart Rendering"

    def render_chart(self, json_input, chart_key, output_filename):
        try:
            # JSON 데이터 로드
            data = json.loads(json_input)
            if chart_key not in data:
                raise ValueError(f"Chart key '{chart_key}' not found in JSON.")

            chart_code = data[chart_key].get("code", "").strip()
            if not chart_code:
                raise ValueError(f"No valid code found for '{chart_key}'. Received: {chart_code}")

            # 안전한 실행 환경 설정
            safe_globals = {"plt": plt, "np": np, "range": range, "len": len, "max": max, "min": min}
            local_scope = {}

            # exec() 실행 (보안 강화)
            try:
                exec(chart_code, safe_globals, local_scope)
            except Exception as e:
                raise RuntimeError(f"Execution error in chart_code: {e}")

            # Matplotlib이 실제로 그래프를 생성했는지 확인
            fig = plt.gcf()
            if not fig.axes:
                raise RuntimeError("No active figure was created. Check the input Python code.")

            # ComfyUI의 기본 출력 디렉토리 설정 (홈 디렉토리 기준)
            comfyui_root = os.path.expanduser("~/ComfyUI")
            output_dir = os.path.join(comfyui_root, "output")

            # 디렉토리가 없으면 생성
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 파일 이름 중복 방지 (타임스탬프 추가)
            timestamp = int(time.time())
            output_filename = f"{output_filename.replace('.png', '')}_{timestamp}.png"
            output_path = os.path.join(output_dir, output_filename)

            # 그래프를 이미지로 변환 (메모리 버퍼 사용, PNG 형식)
            buf = BytesIO()
            plt.savefig(buf, format="PNG")
            plt.close()
            buf.seek(0)

            # 이미지가 정상적으로 생성되었는지 확인
            if not buf.getvalue():
                raise RuntimeError("Failed to generate image from Matplotlib.")

            # 이미지를 ComfyUI에서 사용할 수 있는 형식으로 변환 (PIL Image -> NumPy -> Torch Tensor)
            img = Image.open(buf).convert("RGB")
            img_np = np.array(img)
            img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).float() / 255.0  # CHW, 0~1 범위

            return (img_tensor,)  # 튜플 형태로 이미지 텐서 반환

        except Exception as e:
            print(f"Error in ChartRenderer: {e}")
            return None

# 노드 등록
NODE_CLASS_MAPPINGS = {"ChartRenderer": ChartRenderer}
NODE_DISPLAY_NAME_MAPPINGS = {"ChartRenderer": "Render Chart from JSON"}
