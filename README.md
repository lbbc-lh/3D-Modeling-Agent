# Blender Agent MVP

一个基于现有 Agent 项目副本演进出来的本地 Blender 智能助手雏形。它的目标不是做通用聊天，而是演示一条可落地的 `自然语言 -> 结构化建模动作 -> MCP 风格桥接 -> Blender Python 执行 -> 渲染输出` 链路。

## 项目定位

这个副本项目对应的简历表达是：

- 参与 `LLM + MCP` 的 3D 建模智能设计助手研发
- 实现自然语言到建模指令的自动生成
- 具备意图识别、拒识、参数抽取、自动化 benchmark 的最小雏形

当前版本是一个本地 MVP，范围刻意收紧，只保留最小可展示能力。

## 当前能力

支持的 5 个 Blender 动作：

- `create_primitive`
- `transform_object`
- `apply_material`
- `setup_camera_light`
- `render_scene`

当前链路分成 4 层：

1. `planner`
把自然语言粗略映射为 Blender 动作序列
2. `validator`
校验动作名、必填参数、基础枚举值
3. `mcp_core`
用本地 MCP 风格 client/server 组织工具调用
4. `blender_bridge`
通过真实 Blender 可执行文件运行 `bpy`，生成渲染图和 `.blend`

## 目录

- 入口与请求路由：[start.py](./start.py)
- Blender 规划与执行：[blender_agent](./blender_agent)
- MCP 风格桥接：[mcp_core](./mcp_core)
- Function calling schema：[function_call](./function_call)
- 测试与 benchmark：[test](./test)
- 设计与计划文档：[docs/superpowers](./docs/superpowers)
- 本地输出目录：[outputs](./outputs)

## 已验证结果

已经完成一次真实 Blender smoke test，执行动作链：

- 创建立方体
- 应用红色材质
- 添加相机和灯光
- 渲染输出

生成文件：

- 渲染图：[outputs/smoke_render.png](./outputs/smoke_render.png)
- 场景文件：[outputs/session.blend](./outputs/session.blend)

## 环境要求

- macOS
- 已安装 Blender
- Blender 可执行路径：

```bash
/Applications/Blender.app/Contents/MacOS/Blender
```

建议运行前设置：

```bash
export BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
```

## 快速演示

运行最小演示脚本：

```bash
BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender" \
PYTHONPATH=. \
python scripts/demo_blender_agent.py "创建一个红色立方体，添加相机和灯光，并渲染"
```

如果不传 query，脚本会使用默认示例。

## 测试

运行 Blender 雏形相关测试：

```bash
PYTHONPATH=. python -m unittest discover -s test -p 'test_blender*.py'
```

当前已验证输出：

```text
Ran 7 tests in 0.000s
OK
benchmark accepted=3/3 action_match=3/3
```

## Benchmark

benchmark 数据文件：

- [test/data/blender_benchmark.json](./test/data/blender_benchmark.json)

覆盖两类样本：

- Blender 正样本
- 非 Blender 拒识样本

当前 benchmark 检查：

- 请求是否被正确识别为 Blender 请求
- 动作序列是否匹配预期

## 当前限制

- planner 还是关键词级别的最小实现，不是完整 LLM 规划器
- 意图识别/拒识还没有替换成重新训练后的 Blender 专用模型
- 真实 Blender 执行目前更适合本地 demo，不是生产级任务调度
- `start.py` 里仍保留了原项目的旧入口逻辑，Blender 路由是优先分支，不是彻底重构

## 下一步可以怎么扩

- 把 planner 从关键词规则升级为真实 LLM function calling
- 把拒识和意图模型换成 Blender 领域训练数据
- 增加多对象、多轮建模和更复杂材质/灯光控制
- 为入口增加一组可直接演示的 API/SocketIO 样例
