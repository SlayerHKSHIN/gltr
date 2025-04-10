import os

class GLTRSwitchNodeImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "tooltip": "If True, route to output1. If False, route to output2."}),
                "input_data": ("IMAGE", {"tooltip": "Primary image input to route."}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    OUTPUT_NAMES = ("output1", "output2")
    FUNCTION = "process"

    CATEGORY = "Logic"
    DESCRIPTION = "Re-routes image data to output1 or output2 based on the condition."

    @staticmethod
    def load_dummy_image():
        # dummy.jpg 경로 설정
        dummy_image_path = os.path.expanduser("~/ComfyUI/custom_nodes/ComfyUI-gltr/dummy.jpg")

        # 파일 존재 여부 확인
        if not os.path.exists(dummy_image_path):
            raise FileNotFoundError(f"Dummy image not found at {dummy_image_path}")

    @staticmethod
    def process(condition, input_data):
        # 기본 더미 이미지 로드
        dummy_image = GLTRSwitchNodeImage.load_dummy_image()

        # 조건에 따른 출력
        if condition:
            return (input_data, dummy_image)  # output1에 데이터 전달, output2에 더미 이미지 전달
        else:
            return (dummy_image, input_data)  # output1에 더미 이미지 전달, output2에 데이터 전달


