# -*- coding: utf-8 -*-
# --------------------------------------------
# 项目名称: Blender Agent MVP
# --------------------------------------------


BLENDER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_primitive",
            "description": "Create a primitive object in Blender such as a cube, sphere, or plane.",
            "parameters": {
                "type": "object",
                "properties": {
                    "primitive": {
                        "type": "string",
                        "description": "Primitive type. Supported values: cube, sphere, plane.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional object name.",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional XYZ location.",
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional XYZ rotation in radians.",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional XYZ scale.",
                    },
                },
                "required": ["primitive"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transform_object",
            "description": "Move, rotate, or scale an existing Blender object.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target object name.",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                },
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_material",
            "description": "Apply a basic material color to a Blender object.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target object name.",
                    },
                    "color": {
                        "type": "string",
                        "description": "Material color name or RGB-like expression.",
                    },
                    "material_name": {
                        "type": "string",
                        "description": "Optional material name.",
                    },
                },
                "required": ["target", "color"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "setup_camera_light",
            "description": "Set up a simple camera and light for rendering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "camera_location": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "camera_rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "light_type": {
                        "type": "string",
                        "description": "Light type such as SUN, POINT, AREA.",
                    },
                    "light_location": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "light_energy": {
                        "type": "number",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_scene",
            "description": "Render the current Blender scene to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Output image path.",
                    },
                    "resolution_x": {
                        "type": "number",
                    },
                    "resolution_y": {
                        "type": "number",
                    },
                    "samples": {
                        "type": "number",
                    },
                },
                "required": [],
            },
        },
    },
]

tools1 = BLENDER_TOOLS
