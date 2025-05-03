from .gltr_switch import GLTRSwitchNodeImage
from .chart_renderer import ChartRenderer
from .tag_remover import TagRemover
from .json_extractor import JSONExtractor
from .json_key_filter import JSONKeyFilter
from .gltr_image_search import gltr_image_search
from .save_json import SaveJSON

NODE_CLASS_MAPPINGS = {
    "GLTRSwitchNodeImage": GLTRSwitchNodeImage,
    "ChartRenderer": ChartRenderer,
    "TagRemover": TagRemover,
    "JSONExtractor": JSONExtractor,
    "JSONKeyFilter": JSONKeyFilter,
    "gltr_image_search": gltr_image_search,
    "SaveJSON": SaveJSON
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GLTRSwitchNodeImage": "GLTR Switch Node (Image)",
    "ChartRenderer": "Render Chart from JSON",
    "TagRemover": "Tag Remover",
    "JSONExtractor": "Leaves Nothing but JSON",
    "JSONKeyFilter": "JSON Key Filter",
    "gltr_image_search": "gltr image search (Single)",
    "SaveJSON": "Save JSON"
}