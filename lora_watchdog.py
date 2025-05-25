import os
import re
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

def update_lora_json(folder_path, save_path, lora_save_path):
    # 추출된 고유 문자열 집합
    extracted_strings = set()

    # 폴더 내 파일들을 순회
    for filename in os.listdir(folder_path):
        if filename.startswith("Flux_Lora_") and "_rank16_" in filename:
            match = re.search(r"Flux_Lora_(.*?)_rank16_", filename)
            if match:
                extracted_strings.add(match.group(1))

    # 리스트로 변환 및 정렬
    names = sorted(extracted_strings)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)
    print(f"Total {len(names)} names were extracted and saved into {save_path} file.")

    # 모든 파일명 리스트로 수집 (확장자 포함)
    all_files = sorted(os.listdir(folder_path))
    os.makedirs(os.path.dirname(lora_save_path), exist_ok=True)
    with open(lora_save_path, "w", encoding="utf-8") as f:
        json.dump(all_files, f, ensure_ascii=False, indent=2)
    print(f"Total {len(all_files)} files were extracted and saved into {lora_save_path} file.")

class LoraFolderHandler(FileSystemEventHandler):
    def __init__(self, folder_path, save_path, lora_save_path):
        self.folder_path = folder_path
        self.save_path = save_path
        self.lora_save_path = lora_save_path

    def on_any_event(self, event):
        if not event.is_directory:
            print("폴더에 변경 감지됨, JSON 파일 업데이트!")
            update_lora_json(self.folder_path, self.save_path, self.lora_save_path)

if __name__ == "__main__":
    folder_path = os.path.expanduser("~/ComfyUI/models/loras/")
    save_path = os.path.expanduser("~/ComfyUI/models/loras/list_character_names.json")
    lora_save_path = os.path.expanduser("~/ComfyUI/models/loras/gltr/list_character_lora.json")

    # 최초 1회 실행
    update_lora_json(folder_path, save_path, lora_save_path)

    # watchdog 감시 시작
    event_handler = LoraFolderHandler(folder_path, save_path, lora_save_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print("폴더 변경 감시 중... (종료: Ctrl+C)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
