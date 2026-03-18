# -*- coding: utf-8 -*-

import json


def build_bpy_script(actions_path, result_path, project_root):
    payload = {
        "actions_path": actions_path,
        "result_path": result_path,
        "project_root": project_root,
    }
    escaped = json.dumps(payload)
    return f"""# -*- coding: utf-8 -*-
import json
import os
import sys

import bpy


CONFIG = json.loads({escaped!r})


def ensure_parent(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


def get_object(name):
    return bpy.data.objects.get(name)


def create_primitive(params):
    primitive = params.get("primitive", "cube")
    if primitive == "cube":
        bpy.ops.mesh.primitive_cube_add(location=tuple(params.get("location", [0, 0, 0])))
    elif primitive == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=tuple(params.get("location", [0, 0, 0])))
    elif primitive == "plane":
        bpy.ops.mesh.primitive_plane_add(location=tuple(params.get("location", [0, 0, 0])))
    else:
        raise ValueError(f"unsupported primitive: {{primitive}}")
    obj = bpy.context.active_object
    if params.get("name"):
        obj.name = params["name"]
    if params.get("rotation"):
        obj.rotation_euler = tuple(params["rotation"])
    if params.get("scale"):
        obj.scale = tuple(params["scale"])
    return {{"object": obj.name}}


def transform_object(params):
    obj = get_object(params["target"])
    if obj is None:
        raise ValueError(f"target object not found: {{params['target']}}")
    if params.get("location"):
        obj.location = tuple(params["location"])
    if params.get("rotation"):
        obj.rotation_euler = tuple(params["rotation"])
    if params.get("scale"):
        obj.scale = tuple(params["scale"])
    return {{"object": obj.name}}


def apply_material(params):
    obj = get_object(params["target"])
    if obj is None:
        raise ValueError(f"target object not found: {{params['target']}}")
    color_map = {{
        "red": (1.0, 0.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0, 1.0),
    }}
    material = bpy.data.materials.new(name=params.get("material_name", f"Mat_{{obj.name}}"))
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color_map.get(params["color"], color_map["white"])
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
    return {{"material": material.name}}


def setup_camera_light(params):
    if bpy.data.objects.get("Camera") is None:
        bpy.ops.object.camera_add(location=tuple(params.get("camera_location", [3, -3, 3])))
        camera = bpy.context.active_object
        camera.name = "Camera"
    else:
        camera = bpy.data.objects["Camera"]
    if params.get("camera_rotation"):
        camera.rotation_euler = tuple(params["camera_rotation"])
    else:
        camera.rotation_euler = (1.109, 0.0, 0.785)
    bpy.context.scene.camera = camera

    if bpy.data.objects.get("KeyLight") is None:
        bpy.ops.object.light_add(
            type=params.get("light_type", "SUN"),
            location=tuple(params.get("light_location", [4, -4, 6])),
        )
        light = bpy.context.active_object
        light.name = "KeyLight"
    else:
        light = bpy.data.objects["KeyLight"]
    light.data.energy = params.get("light_energy", 3.0)
    return {{"camera": camera.name, "light": light.name}}


def render_scene(params):
    scene = bpy.context.scene
    output_path = params.get("output_path", "outputs/render.png")
    if not os.path.isabs(output_path):
        output_path = os.path.join(CONFIG["project_root"], output_path)
    ensure_parent(output_path)
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    if params.get("resolution_x"):
        scene.render.resolution_x = int(params["resolution_x"])
    if params.get("resolution_y"):
        scene.render.resolution_y = int(params["resolution_y"])
    if params.get("samples") and hasattr(scene, "cycles"):
        scene.cycles.samples = int(params["samples"])
    bpy.ops.render.render(write_still=True)
    return {{"output_image": output_path}}


HANDLERS = {{
    "create_primitive": create_primitive,
    "transform_object": transform_object,
    "apply_material": apply_material,
    "setup_camera_light": setup_camera_light,
    "render_scene": render_scene,
}}


def main():
    with open(CONFIG["actions_path"], "r", encoding="utf-8") as fh:
        actions = json.load(fh)

    clear_scene()
    results = []
    errors = []
    output_image = ""

    for action in actions:
        action_name = action["action"]
        params = action.get("params", {{}})
        try:
            artifacts = HANDLERS[action_name](params)
            results.append({{
                "success": True,
                "action": action_name,
                "artifacts": artifacts,
                "error": "",
            }})
            if "output_image" in artifacts:
                output_image = artifacts["output_image"]
        except Exception as exc:
            results.append({{
                "success": False,
                "action": action_name,
                "artifacts": {{}},
                "error": str(exc),
            }})
            errors.append(str(exc))
            break

    scene_file = os.path.join(CONFIG["project_root"], "outputs", "session.blend")
    ensure_parent(scene_file)
    bpy.ops.wm.save_as_mainfile(filepath=scene_file)

    payload = {{
        "success": not errors,
        "mode": "blender",
        "executed_actions": len(results),
        "results": results,
        "errors": errors,
        "output_image": output_image,
        "scene_file": scene_file,
    }}
    with open(CONFIG["result_path"], "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)


main()
"""
