# -*- coding: utf-8 -*-

SUPPORTED_ACTIONS = {
    "create_primitive": {"required": ["primitive"]},
    "transform_object": {"required": ["target"]},
    "apply_material": {"required": ["target", "color"]},
    "setup_camera_light": {"required": []},
    "render_scene": {"required": []},
}

SUPPORTED_PRIMITIVES = {"cube", "sphere", "plane"}


def build_execution_response(query="", trace_id="", intent="Blender建模", function=""):
    return {
        "query": query,
        "trace_id": trace_id,
        "intent": intent,
        "function": function,
        "actions": [],
        "execution": {
            "success": False,
            "executed_actions": 0,
            "results": [],
            "output_image": "",
            "scene_file": "",
            "errors": [],
        },
    }
