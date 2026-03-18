# Blender Agent 简历项目介绍与面试讲法

## 1. 简历项目名称

`LLM + MCP 3D 建模智能设计助手（Blender Agent MVP）`

## 2. 简历表述版本

### 版本 A：偏完整

- 基于现有多服务 Agent 架构改造本地 Blender 智能助手，完成自然语言到结构化建模动作的转换，并通过 MCP 风格工具桥接调用 Blender Python API 执行
- 设计并实现 5 类核心建模动作能力：`create_primitive`、`transform_object`、`apply_material`、`setup_camera_light`、`render_scene`，打通从请求解析到场景生成、材质设置、布光和渲染输出的闭环
- 抽象 `planner / validator / mcp_bridge / blender_executor` 分层架构，降低动作解析与执行层耦合，支持本地 dry-run 与真实 Blender 执行双模式
- 构建最小 benchmark 与自动化测试，覆盖 Blender 请求识别、拒识、参数归一化、动作序列校验及真实渲染 smoke test，验证输出 `.blend` 场景文件与渲染图片

### 版本 B：偏精简

- 参与 `LLM + MCP` 的 3D 建模智能设计助手研发，完成自然语言到 Blender 结构化建模指令的自动生成与本地执行闭环
- 设计动作规划、参数校验、MCP 风格工具桥接与自动化 benchmark，支持基础建模、材质、相机灯光与渲染输出

## 3. 面试讲法

建议按 4 段讲，控制在 2 到 3 分钟。

### 第一段：问题定义

“我做的是一个 Blender Agent 的本地 MVP，目标不是做通用聊天，而是把自然语言请求变成可执行的 3D 建模动作。比如用户说‘创建一个红色立方体，添加相机和灯光，并渲染’，系统会拆成结构化动作，再实际驱动 Blender 生成场景和图片。”

### 第二段：架构拆分

“我把链路拆成 4 层：`planner` 负责把自然语言转成动作序列，`validator` 做动作名和参数校验，`mcp_bridge` 把动作抽象成工具调用，`blender_executor` 负责把动作批量下发到 Blender Python。这样做的原因是解析层和执行层边界更清楚，后面不管是换成真正的 LLM function calling，还是扩更多 3D 工具，改动都比较集中。”

### 第三段：技术难点

“最大的一个点是多动作必须在同一个 Blender 进程里执行。因为如果 `create_primitive` 和 `render_scene` 分别跑在不同进程里，前面创建的物体不会保留下来。所以我把真实执行入口收敛到批量执行层，在一个 Blender 后台进程里完成建模、上材质、布光、渲染和保存 `.blend`。另一个点是我保留了 dry-run 模式，这样在本地没有 Blender 或 CI 环境里也能先验证动作链。”

### 第四段：结果和验证

“最后我做了 benchmark 和自动化测试，覆盖 Blender 请求识别、拒识、参数归一化和动作执行。并且我实际跑通了 smoke test，生成了渲染图和 `.blend` 文件，所以这个项目不是停留在动作 JSON，而是真正打通了从自然语言到 3D 输出的闭环。”

## 4. 高频追问答法

### 为什么要加 MCP 这一层？

“主要是为了把动作生成和执行解耦。对上层来说它只是在调用工具，不需要知道底层是直接 `bpy`、本地进程还是远程服务。这样结构更稳，也更符合后续接更多 3D 工具或外部执行器的扩展方向。”

### 这个项目里 LLM 成分强不强？

“当前这个 MVP 为了先验证闭环，planner 是关键词级最小实现，但 function schema、参数归一化和 MCP 工具边界都已经准备好了。下一步很自然就是把 planner 替换成真正的 LLM function calling 或 Blender 领域意图模型，所以我更重视先把执行闭环和系统边界做对。”

### 这个项目最体现你的什么能力？

“不是单点写了个 Blender 脚本，而是把 Agent、动作抽象、执行桥接、自动化验证串起来了。也就是说我做的是一条可以继续扩展成 3D 智能设计助手的工程骨架。”

## 5. 一句话总结

“这是一个把自然语言转成 Blender 可执行动作，并通过 MCP 风格桥接完成真实建模与渲染输出的本地 Agent MVP。”
