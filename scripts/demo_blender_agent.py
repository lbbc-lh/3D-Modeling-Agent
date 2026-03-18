# -*- coding: utf-8 -*-

import json
import sys

from blender_agent.executor import execute_actions
from blender_agent.planner import build_blender_actions, is_blender_request


DEFAULT_QUERY = "创建一个红色立方体，添加相机和灯光，并渲染"


def main():
    query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY
    accepted = is_blender_request(query)
    actions = build_blender_actions(query) if accepted else []

    result = {
        "query": query,
        "accepted": accepted,
        "actions": actions,
        "execution": execute_actions(actions) if actions else None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
