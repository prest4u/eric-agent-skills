# Eric Visual Memory Translator

把照片转译成克制的编辑设计、艺术出版或视觉手札图像。

它不是滤镜，也不是把照片重新画一遍。它先判断什么值得保留，再用版式、留白、抽象、色彩与少量文字重新组织记忆。

## 能做什么

- 分析主体、构图、情绪与主题色。
- 选择原图呈现、版式、风格与抽象度。
- 生成可直接交给图像生成或编辑工具的指令。
- 对旅行、人像、建筑、风景与日常照片建立统一的艺术出版语气。

默认使用高抽象、极高留白、暖米白纸面与短句中文文案。完整参数、预设和失败修正规则都保留在 `references/` 中。

## 安装

使用统一的公开仓库安装命令，只替换目标 Agent ID：

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-visual-memory-translator \
  --agent <agent-id> --copy --yes
```

首批正式验证的 ID 是 `codex`、`claude-code`、`kimi-code-cli`、`opencode` 和 `cursor`。例如安装到 Codex：

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-visual-memory-translator \
  --agent codex --copy --yes
```

调用：

```text
$eric-visual-memory-translator 把这张照片转译成安静的旅行记忆页。
```

### 其他兼容 Agent

先用 CLI 帮助或项目文档确认 agent 标识：

```bash
npx -y skills@latest --help
```

CLI 已支持的 Agent 可使用：

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-visual-memory-translator \
  --agent <supported-agent-id> --copy --yes
```

若目标 Agent 不在 CLI 支持列表，但兼容开放的 `SKILL.md` 目录格式，可以复制整个 Skill 目录。必须保留 `SKILL.md`、`examples.md`、`references/` 与 `agents/openai.yaml` 的相对结构。

## 使用

上传一张照片后明确调用：

```text
$eric-visual-memory-translator 默认模式。
```

```text
$eric-visual-memory-translator 不展示原图，极致抽象，不要文字。
```

```text
$eric-visual-memory-translator 用展览票模式，把这次旅行看成一次展览。
```

更多调用方式见 [examples.md](../../skills/eric-visual-memory-translator/examples.md)。核心参数包括：

- `original_display_mode`：原图是否出现、如何出现。
- `layout_mode`：页面构图。
- `style_mode`：视觉转译风格。
- `abstraction_level`：信息保留比例。
- `text_mode`：文字来源与强度。
- `ratio`：输出比例。

## 文件结构

```text
eric-visual-memory-translator/
├── SKILL.md
├── agents/openai.yaml
├── examples.md
├── references/
│   ├── defaults-and-presets.md
│   ├── display-and-layout.md
│   ├── parameters.md
│   ├── quality.md
│   ├── styles.md
│   └── systems.md
└── LICENSE
```

## 来源与许可

本项目基于 [jinwyp/visual-memory-translator-SKILL](https://github.com/jinwyp/visual-memory-translator-SKILL) 的 MIT 许可版本 `170ae15c331ec4bdee49334b4a818ba4b8a335a7` 衍生并重新命名。核心教程、示例与参考资料均被保留；面向 Agent 的名称、调用方式和安装说明已改为 Eric 版本。

MIT License，完整文本见 [LICENSE](../../skills/eric-visual-memory-translator/LICENSE)。上游版权声明与许可条件保持不变。
