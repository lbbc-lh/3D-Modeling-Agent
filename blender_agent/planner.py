# -*- coding: utf-8 -*-

BLENDER_KEYWORDS = (
    "blender",
    "立方体",
    "球体",
    "平面",
    "材质",
    "相机",
    "灯光",
    "渲染",
    "模型",
)


def is_blender_request(query):
    if not query:
        return False
    lowered = query.lower()
    return any(keyword in query or keyword in lowered for keyword in BLENDER_KEYWORDS)


def build_blender_actions(query):
    actions = []

    primitive = None
    if "立方体" in query or "cube" in query.lower():
        primitive = "cube"
    elif "球体" in query or "sphere" in query.lower():
        primitive = "sphere"
    elif "平面" in query or "plane" in query.lower():
        primitive = "plane"

    if primitive:
        actions.append(
            {
                "action": "create_primitive",
                "params": {"primitive": primitive, "name": primitive.title()},
            }
        )

    color_map = {
        "红": "red",
        "蓝": "blue",
        "绿": "green",
        "白": "white",
        "黑": "black",
    }
    for token, color in color_map.items():
        if token in query:
            actions.append(
                {
                    "action": "apply_material",
                    "params": {"target": primitive.title() if primitive else "Cube", "color": color},
                }
            )
            break

    if "相机" in query or "灯光" in query:
        actions.append({"action": "setup_camera_light", "params": {}})

    if "渲染" in query or "render" in query.lower():
        actions.append(
            {
                "action": "render_scene",
                "params": {"output_path": "outputs/render.png"},
            }
        )

    return actions
