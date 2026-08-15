# Eric PPT Skill

Eric 的私人演示文稿工作流，用于在 Codex 等兼容 Agent 中创建、编辑、复刻、读取并导出 PPT/PPTX。

默认交付两份成果：

1. 可继续编辑的 PPTD 项目目录；
2. 可直接演示和继续修改的 PPTX 文件。

这套版本保留了设计教程、版式规则、可移植导出脚本、测试样例与主题索引，并统一整理为 **Eric PPT Skill** 的命名与使用说明。默认导出器由本仓库自有 Python 代码实现，不包含 Kimi/Moonshot 产品前端镜像、patched WASM 或来源不明的字体与模板。

## 主要能力

- 从主题、文章或大纲生成完整演示文稿；
- 按现有 PPTX、PDF、截图或网页迁移内容与视觉风格；
- 使用 YAML 风格的 PPTD 中间格式逐页编辑；
- 导出原生可编辑 PPTX，而不是把每一页压成整张图片；
- 支持图片素材、图表、版式系统、页面切换和可选元素动画；
- 执行结构检查，并在本机已有授权渲染器时完成页面图片质检；
- 提供咨询、财务、工作汇报、品牌推广与学术教育等设计系统说明。

## 安装

默认导出需要 Python 3 与 PyYAML 6.0.3。通过总仓库安装：

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-ppt-skill \
  --agent codex \
  --global \
  --yes
```

安装后，Codex 中显示的名称为 **Eric PPT Skill**，机器标识为 `eric-ppt-skill`。

## 使用示例

```text
使用 Eric PPT Skill，制作一份 12 页的 AI 产品战略汇报。
风格采用 pine-green-strategy，包含市场判断、产品路线图、关键指标和行动计划。
```

```text
使用 Eric PPT Skill，把我提供的 PPTX 调整成简洁的年度汇报风格。
保留原有数据和图片，重新整理标题层级、图表配色与页面节奏。
```

```text
使用 Eric PPT Skill，基于这份研究报告制作一份学术答辩 PPT。
使用 teal-green-academic-defense，控制在 15 页，并加入必要的来源标注。
```

## 默认交付结构

```text
deck/
  deck.pptd
  pages/
    01-cover.page
    02-overview.page
  media/
  deck.pptx
```

- `deck.pptd`：项目清单与全局主题；
- `pages/`：每页一个可编辑页面文件；
- `media/`：图片、图标及其他本地素材；
- `deck.pptx`：最终导出的 PowerPoint 文件。

## 主题索引

完整索引见同目录下的 `eric-ppt-skill-themes.md`，执行用设计系统位于 Skill 的 `reference/design_system/`。公开仓库不附带来源不明的预览截图、产品界面镜像或模板二进制。

## 工作流程

1. 明确用途、受众、页数与视觉方向；
2. 阅读 `reference/pptd.md` 和对应场景教程；
3. 批量准备可信的图片、数据与引用来源；
4. 编写 PPTD 清单及逐页 `.page` 文件；
5. 检查边界、溢出、遮挡、对比度与阅读层级；
6. 用可移植导出器生成 PPTX，检查文件完整性、可编辑对象与页面切换；
7. 使用本机已有授权办公软件渲染页面并完成视觉复核；若没有授权渲染器，则明确记录结构性 QA 的范围；
8. 同时交付 PPTD 项目和 PPTX 成品。

## 目录说明

```text
agents/        Codex 界面显示配置
reference/     PPTD、版式和设计系统教程
scripts/       可移植 PPTX 导出器、可选页面图片 QA 工具
tests/         导出逻辑与最小项目测试
SKILL.md       Agent 执行规范
```

## 本地检查

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

## 使用边界

- 只在用户指定的项目目录内创建或修改演示文件；
- 下载外部图片、字体或资料时，核对来源、授权与引用要求；
- 不把登录凭证、Cookie、私有文稿或其他敏感数据提交到仓库；
- 对外发布前，逐页检查内容准确性、版权标注与视觉质量。

## 许可

本 Skill 保留上游 MIT 许可与原作者版权声明，详见 Skill 目录内的 `LICENSE`。上游产品前端镜像及缺少独立再分发证据的资产未进入公开仓库。
