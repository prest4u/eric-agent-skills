---
name: eric-qingyun-profile-pdf
description: 【档案约束】Create the 2-4 page 青云未来档案与家庭约束确认 PDF. This season default is 选科版 D3 (subjects and family floor). Use when locking 选科, hard constraints, or later score/rank before a volunteer plan, or when making 档案确认、约束确认单. Includes its own portable visual, ethics, build, and QA baseline. The next deliverable must project this page.
---

# D3 档案与家庭约束确认

先读本包 `references/visual-contract.md` 与 `references/ethics.md`；`assets/theme.typ` 和 `scripts/` 让本 Skill 可独立使用。若安装了 `$eric-qingyun-pdf`，可只读核对共享版本，但不是运行依赖。本页是下一份交付的事实底座。本季默认选科版。

## 何时用 / 不用

**用：** 访谈后、出选科报告或志愿方案前，家庭必须确认「这些约束是我们说的」。

**不用：** 直接出院校表或科目推荐结论（先有本页）；性格测评当专业结论；把 Life Journey / MBTI 写成录取依据。

## 规格

- 读者：家长核对、顾问建档、复核人
- 2–4 页 A4 竖
- 半文书：家庭确认原意

## 页面建筑

1. Cover：案例身份 + 确认用途（选科版 / 志愿版写清）
2. 选科版：科目意向、硬约束、软偏好、待补。志愿版另补位次来源与查询日
3. 家庭签字确认

## 必须 / 禁止

必须：省/年、硬约束、待补、签字、免责四句。选科版锁科目底线。志愿版必须有位次来源与查询日。

禁止：院校推荐表、冲稳保总表、概率、真实证件号、把软偏好写成硬限制而不标明。

## 相邻文书

选科报告投影选科版本页。志愿 D4 投影志愿版本页，不得混用。家庭改口：先改 D3 再改下一份交付。

## 文件名

`档案确认-案例{ID}-{省}{年}-V{n}-YYYYMMDD.pdf`

## 工作流

`--scene profile`，`check_pdf.py --scene profile`。

## 验收

硬约束与待补分开。有签字栏。无院校清单。志愿版才强制位次口径。
