---
name: eric-qingyun-subject-pdf
description: 【选科指导报告】Create the 4-8 page 青云未来选科指导报告 PDF. First-to-sell deliverable for 高一/高二 选科与学业规划. Use when making 选科指导、科目组合、选科报告. Includes its own portable visual, ethics, build, and QA baseline. Same Slate White skin as later volunteer plans, different modules. Do not shrink a 冲稳保 volunteer list into this file.
---

# 选科指导报告（本季主交付）

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。青云未来 9–10 月先卖这一份，不是缩小版志愿方案。

## 何时用 / 不用

**用：** 新高一/高二家庭决定科目组合；刘月牵头的选科产品化交付。

**不用：** 出分后填报（`$eric-qingyun-plan-pdf`）；早鸟定金说明（`--scene early-bird`）；把冲稳保院校表塞进来。

## 规格

- 读者：学生与家长
- 4–8 页 A4 竖
- 给人看的报告，须签发

## 页面建筑

1. Cover：青云未来 · 选科指导 · 标明不是志愿表
2. 科目组合与放弃某科的代价
3. 专业门 + 轻度学业规划（课程负担、跟得上与否）——事实 / 判断 / 待观察
4. 下一步（何时复核选科要求；若买早鸟，另附早鸟页，不写进本册当志愿承诺）
5. 免责

## 必须 / 禁止

必须：组合、代价、待观察、免责四句、署名「青云未来」、回当年选科要求核对。

禁止：冲稳保院校总表、录取概率、用测评直接定组合、印知路、假装覆盖全部专业门。

## 相邻文书

选科版 D3 锁科目与家庭底线。D6 签发后才称正式。同一学生明年做志愿时另开志愿 D3/D4，只继承已确认科目。

## 文件名

`选科指导-案例{ID}-{省}{年}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene subject`，`check_pdf.py --scene subject`。

## 验收

无冲稳保院校表。有「选科」「待观察」。页脚为青云未来。灰印可读。
