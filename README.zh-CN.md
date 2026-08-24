# Eric Agent Skills

[English](README.md)

这是 Eric 的 37 个跨脚手架 Agent Skill 权威仓库，覆盖学生与企业文档、PDF、PPT、网站、视频和交付质量工作流。

五个 PDF Skill 始终保持独立目录、独立安装和独立版本：

- `eric-designed-pdf`
- `eric-pdf`
- `eric-moss-ivory-pdf`
- `eric-slate-white-pdf`
- `eric-pdf-vocabulary`

`pdf` 集合只是批量安装清单，不会生成统一 PDF 超级 Skill，也不会让五者互相依赖。

新增的 `professional-pdf-series` 集合包含八个彼此独立的职业 PDF Skill，分别覆盖战略咨询、交易尽调、政策影响、技术图谱、学习指南、高管读本、研究专著与知识档案。

## 安装单个 Skill

```bash
npx -y skills@latest add prest4u/eric-agent-skills \
  --skill eric-pdf \
  --agent codex \
  --copy \
  --yes
```

已验证的 Agent ID：`codex`、`claude-code`、`kimi-code-cli`、`opencode`、`cursor`。将 `eric-pdf` 换成 [`catalog/skills.yaml`](catalog/skills.yaml) 中任一名称即可。

若机器上已有同名旧版全局 Skill，部分脚手架会优先加载旧版。验收前应移除或升级旧版，不要永久改机器名称；`skills-lock.json` 会记录安装来源和内容哈希。

## 原生入口

- Codex：`.codex-plugin/plugin.json`
- Kimi Code CLI：`kimi.plugin.json`
- Claude Code：`.claude-plugin/marketplace.json`
- OpenCode、Cursor：通过标准 Agent Skills 目录复制安装

## 多工具共用同一版本

在本仓库运行：

```bash
python3 scripts/sync_user_install.py --apply
```

同步器会先备份冲突副本，再让 Codex、Kimi Code、Kimi Desktop、Cursor、Claude Code 与 Hermes Agent 指向同一份 GitHub checkout。使用 `--check` 只检查漂移；使用 `--update --apply` 先从 GitHub 快进更新，再修复本机发现路径。

## 上游与镜像

本仓库是唯一可编辑权威源。精选上游锁定 Commit、目录哈希和许可证证据，只更新 `references/upstream/` 机器管理区；每周自动化仅提出 PR，不自动合并。

18 个单 Skill 仓库均由本仓库单向生成。`.mirror-manifest.json` 会校验上次受管文件状态；发现人工分叉即停止，不覆盖、不 force-push。

## 隐私与许可

公开仓库只含匿名或合成夹具，以及有明确再分发许可的素材。真实学生、客户或企业回归材料只进入独立私有夹具仓库，并且必须先有精确文件清单和明确批准。

第三方与字体许可见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)，维护与发布流程见 [`docs/maintenance.md`](docs/maintenance.md)。

首版候选的验收矩阵与尚未解除的发布门禁见 [`docs/release/hub-v1.0.0-acceptance.md`](docs/release/hub-v1.0.0-acceptance.md)。
