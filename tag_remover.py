import re

class TagRemover:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "tag": ("STRING", {"default": "think"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "remove_tag"
    CATEGORY = "GLTR Utils"

    def remove_tag(self, text, tag):
        pattern = rf"<{tag}>.*?</{tag}>"
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return (cleaned_text.strip(),)
