# -*- coding: utf-8 -*-

import json
import os
import subprocess
import tempfile
from pathlib import Path

from blender_agent.bpy_runner import build_bpy_script


def detect_blender_binary():
    blender_bin = os.getenv("BLENDER_BIN", "").strip()
    if blender_bin and os.path.exists(blender_bin):
        return blender_bin
    return ""


def run_blender_action(action_payload):
    blender_bin = detect_blender_binary()
    if not blender_bin:
        return {
            "success": True,
            "mode": "dry_run",
            "artifacts": {},
            "error": "",
        }

    return {
        "success": True,
        "mode": "blender",
        "artifacts": {"blender_bin": blender_bin},
        "error": "",
    }


def run_blender_actions(actions):
    blender_bin = detect_blender_binary()
    if not blender_bin:
        return {
            "success": True,
            "mode": "dry_run",
            "executed_actions": len(actions),
            "results": [
                {
                    "success": True,
                    "action": action["action"],
                    "artifacts": {},
                    "error": "",
                }
                for action in actions
            ],
            "errors": [],
            "output_image": "",
            "scene_file": "",
        }

    project_root = str(Path(__file__).resolve().parent.parent)
    outputs_dir = Path(project_root) / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="blender-agent-") as tmpdir:
        tmp_path = Path(tmpdir)
        actions_path = tmp_path / "actions.json"
        result_path = tmp_path / "result.json"
        script_path = tmp_path / "run_blender_actions.py"

        actions_path.write_text(json.dumps(actions, ensure_ascii=False), encoding="utf-8")
        script_path.write_text(
            build_bpy_script(str(actions_path), str(result_path), project_root),
            encoding="utf-8",
        )

        command = [
            blender_bin,
            "--background",
            "--factory-startup",
            "--python",
            str(script_path),
        ]
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0:
            return {
                "success": False,
                "mode": "blender",
                "executed_actions": 0,
                "results": [],
                "errors": [proc.stderr.strip() or proc.stdout.strip() or "blender execution failed"],
                "output_image": "",
                "scene_file": "",
            }

        if not result_path.exists():
            return {
                "success": False,
                "mode": "blender",
                "executed_actions": 0,
                "results": [],
                "errors": ["missing blender result payload"],
                "output_image": "",
                "scene_file": "",
            }
        return json.loads(result_path.read_text(encoding="utf-8"))
