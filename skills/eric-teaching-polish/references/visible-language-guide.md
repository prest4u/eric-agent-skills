# Visible Language Guide

Use this when polishing teaching materials for students, parents, or public-facing use.

## Goal

Make the text sound like a real teacher giving useful material:

- concrete
- readable
- exam-grounded
- not over-explained
- not full of production/workflow labels

## Internal-To-Visible Replacements

| Avoid in visible text | Better visible wording |
|---|---|
| 入口 | 从这里开始 / 第一步 / 先看这个例句 / 先做这组题 |
| 回收 | 复习 / 回看 / 重新巩固 / 再练一遍 |
| 卡片 | 练习页 / 小题 / 例句 / 知识点整理 / 任务单 |
| 动作卡 / 自检卡 / 得分动作 | 练习页 / 证据记录 / 下一步练习点 / 先看证据再作答 |
| 私人自检 / 优先动作卡 / 班级动作热区 | 个人回看 / 下一步练习点 / 班级易错点 |
| score moves / scorecard / self-check card | evidence check / practice note / next practice point / before-you-leave review |
| 路由 | 后续安排 / 这次先做... / 本节课先处理... |
| 维修 / 短程维修 | 补一补 / 巩固一下 / 把这个点练稳 |
| 动作链 | 做题步骤 / 判断顺序 / 检查顺序 |
| 得分场景 | 题型 / 考点 / 拿分点 |
| 能力场景 | 能力点 / 练习重点 |
| 后台 | 删除，或改成老师内部记录 |
| 机制 | 方法 / 规律 / 为什么这样做 |
| 抓手 | 重点 / 练习点 / 可以先抓住的地方 |
| 闭环 | 完成一轮练习 / 讲完后再检查 |
| 沉淀 | 整理 / 记下来 / 形成错题记录 |
| 赋能 | 帮助 / 让学生能... |
| 对齐 / 拉通 | 统一 / 串起来 / 放在一起看 |
| 课堂安排 / 课堂动作 / 教师节奏 / 学生产出 | 删除教师执行视角；学生版改为练习环节 / 我会完成 |
| 0-10 / 10-27 等教师课堂分钟段 | 学生版删除；教师版可保留。学生自己的限时练习计划可以保留 |
| 学生版 / 教师版 / 教师用 / 22讲 / 第N讲 | 学生版删除身份标签；标题直接写学习对象，如“动词形式判断” |
| 第07-08讲 / 第10-13讲 / 02-06 / 07-09 / 前四讲 / 本阶段分钟 | 前面几次训练 / 前一阶段 / 阶段名 / 本次限时练习 |
| reading/cloze 表格里的裸行号范围 `1-2` / `3-4` / `5-6` | `Line 1, Line 2` / `Lines 1 and 2` / `line group: start/support/result` |
| 课程地图 / 22讲路线 / Course Map | 学生单课包默认不放；把使用说明放第一课，把阶段回顾放单元结尾 |
| source_id / TJGK-PAPER / SIM-... / 天津高考真题 / 真题精拆 / 真题审题 / 真题改编 / 原创仿真 / 完整仿真篇章 / 复用材料 / 回看材料 | 放在 manifest 或教师备注；学生版改成 Guided Exam Practice / Exam-Style Practice / Timed Practice / Review Passage / Additional Practice |
| source_unit_no / reader_order / build_order / canonical_id / golden sample / thick unit / quality gate | 放在 manifest、progress ledger 或教师内部说明；学生版只显示最终 Unit 名称、页码、学习任务 |
| TJGK-2025A-CLOZE-18 / CLOZE-18 / READ-36 / L12-EC03 / T16 / B16 / G16 | 学生版删除；教师版正文改成 Cloze Blank 18 / Reading Q36 / Lesson 12 response item 3 / Blank 16，原始 id 只留 manifest/source 层 |
| Unseen Full Practice 用在已见材料上 | 改成 Timed Review / Review Passage / Additional Practice，并在 source manifest 记录复用关系 |
| 调用工具 / 高错工具 / 前序工具 / 关键工具 / 工具阶段 / 工具带走 / 五类工具 / 5 类工具 / 训练工具 / 高错 | 学生版改成所用策略 / 易错提醒 / 前面练过的方法 / 关键方法 / 表达方法 |
| Stage 1 / Stage 2 / Unit Review | 学生版改成 Practice Focus / Review Checkpoint 或直接用自然标题 |
| Soft Signal / publication edition / lesson pack / combined book / generated from | 学生总册或学生讲义中删除生产说明；改成本册 / 课堂练习 / 目录页码 / 本讲页码 |
| sibling course title / master course title / old package name / student_total_a4 / lesson01_student_a4 / outputs/ / src/ / qa/ / validator/ / archive | 学生可见包只保留当前课程身份；构建名、母版名、目录名、归档名放进 manifest 或内部说明 |
| folder names / build slugs / internal lesson names copied into covers, TOCs, or running heads | 先做 visible-title 清洗；把“闭环、入口、回收、track”等内部词改成学生能读懂的学习动作 |
| 讲评 | 学生版改为核对 / 订正 / 回看错题；教师版可保留为教师处理提示 |
| 时间安排 / 课堂中必须保留 / 不可被课堂核对占用 | 练习节奏 / 30分钟写一稿 / 留给真实写作和修改 |
| 样文只能展示 / 教师样文 | 完成一稿后再看示范结构；教师版可写 teacher-only benchmark |
| Backup Passage / Backup Full Passage / 备用阅读 / 备用任务 / 备用补测 | Optional Passage / Additional Practice / 加练阅读 / 加练任务 |
| A轨 / B轨 / C轨 / Track A / Foundation Track / Core Track / Advanced Track / 基础差 / 差生版 / 快班 / 慢班 | 学生端改成正向课程身份，如稳基线课堂练习 / 标准提升课堂练习 / 高分冲刺课堂练习；内部轨道名只留在 manifest、教师说明或生产计划 |
| A38 / B01 / B05 / B41 / C01 / D01 / T1 / SOLO 等内部码 | 删除，或改成真实题号 / 练习组名称 |
| 参考答案 / 答案解析 / 答案： / 解析： | 学生版删除；教师版或答案册单独保留 |
| prototype / draft / drafts / 本地路径 `/Users/...` | 删除构建状态和本机路径；写作课可改成 version / revision / 修改稿 |
| 中文标题 + 第N空，如“博物馆导览与灵活执行 第16空” | English-forward exam label, e.g. `Museum Tour and Flexible Guiding, Blank 16` |
| OCR 噪音如 `ev- ery`, `a- gainshe`, `whenI__18`, `confusio`, `expectationoi`, `fourweek` | 回源校对，不做语言润色式猜改 |

Do not replace mechanically. If `入口` literally means a physical entrance in a reading passage, keep it.

## Teaching-Specific Anti-AI Patterns

Remove or rewrite:

- "本节课围绕...展开，进行了系统化梳理"
- "通过本节课的学习，学生能够..."
- "这为后续学习打下坚实基础"
- "从知识输入到能力输出形成闭环"
- "真正重要的是..."
- "不是...而是..." when it is only a lecture shell
- "先...再...最后..." when it describes the teacher's workflow rather than a student's task
- "我们可以看到 / 接下来我们 / 下面来看" in student-facing worksheets
- "一套完整的学习路径 / 能力矩阵 / 训练框架" unless it is a parent-facing course overview and written naturally
- "动作得分卡 / 自检卡 / scorecard" when the material is meant to feel like a textbook or workbook page
- visible class execution tables like "0-10 / 课堂安排 / 学生产出" in student-facing worksheets
- visible version/course-route labels like "学生版 / 教师版 / 22讲 / 第20讲" in student-facing PDFs
- standalone course maps in ordinary student lesson packs, especially route tables that show lesson ranges instead of telling the student what to do today
- raw bank or route labels like "B01-B05", "T1", "SOLO" when students do not need to know the production system
- raw source-management labels like "source_id", "TJGK-PAPER", "SIM-001", "天津高考真题", "真题精拆", "完整仿真篇章", "原创天津高考仿真", "复用材料", or "回看材料"; students should see the practice role, not the production provenance
- production sequence labels like "source_unit_no", "reader_order", "build_order", "canonical_id", "golden sample", "thick unit", or "quality gate"; students should see the final learning sequence, not maintenance fields
- raw source/question codes like "TJGK-2025A-CLOZE-18", "CLOZE-18", "READ-36", "L12-EC03", or short cloze labels like "T16/B16/G16" in visible teaching text; teacher guides should print readable item names, not source ids
- tool-routing language such as "调用工具", "高错工具", "工具阶段收束", "工具带走", "五类工具", "5 类工具", "训练工具", or "关键工具"; students should see strategy instructions, not internal routing labels
- visible series-management labels such as "Stage 1" or "Unit Review"; use natural page labels like Practice Focus or Review Checkpoint
- covers, tables of contents, running heads, or total-book front matter generated directly from folder names or build slugs. Clean them through a visible-title map before PDF build.
- total-book front matter or teacher front matter that describes production packaging instead of reader use, such as "A4 teacher total book", "front matter plus classroom guide bodies", "combined book", or "generated from lesson packs"
- build/prototype residue like "draft", "prototype", or local paths when they are not authentic source text
- machine replacement residue after automated cleanup, especially strings like "今天承接今天", "今天把今天", "合格我的作答", "Blanks 本阶段", "Objectivequestion", or "four week round-two"
- title/cleanup residue after course rebuilds, especially strings like "Sprint High-Score Sprint Setup", "加练加练", "第本课程", or "内部翻找"
- fake exam blank placeholders such as "(blank)" in student-facing question stems. Use a real printed blank line (`____`) or natural exam wording; high-score and exam-simulation pages must not show replacement artifacts.
- teacher-control words like "讲评" in ordinary student worksheets
- answer/explanation headers in ordinary student handouts, unless the file is explicitly an answer key
- Chinese-only reading-task labels in later K12 English exam practice, when the target exam asks students to read English stems and instructions
- half-translated labels such as "Evidence链", "第本阶段讲", or "圈but/however/instead/yet"; translate the full label or keep a natural Chinese support sentence
- Chinese passage title plus `第N空` in cloze/exam simulation labels
- OCR residue in official exam materials: split words, glued words, corrupted option text, accidental symbols, or fused PDF words
- teacher control instructions in student worksheets, including "时间安排", "课堂中必须保留", "不可被课堂核对占用", and "样文只能..."
- repeated generic teacher-guide control notes such as "先给学生30至60秒独立观察", "学生回答后，把依据写在题目旁边", or "请两名学生复述方法"; if the note is not tied to the actual task, consolidate it once or remove it
- generic teacher extension fallback residue such as "顺利学生做；若低错不稳，退回 core" or "顺利学生做；若证据不稳，退回 line band"; replace with the actual repair move for that lesson
- numeric teacher route residue such as "Start + 01-07 + 09-10" or "01 + 05 one row + 07 first item + 09"; teacher-facing route tables should name the classroom sequence, not generator sections
- bare hyphen line ranges such as "1-2 / 3-4 / 5-6" in reading or cloze line-band tables; use "Line 1, Line 2" or "Lines 1 and 2" so the text does not look like timing, lesson-range, or route residue
- main-idea/structure lesson residue such as "Line-Band Rescue", "line band + one evidence word", or "主旨题找证据即可"; use paragraph job, title scope, ending result, wrong-title rejection, and safer-title repair
- reading-set/timed-combination lesson residue such as "Line-Band Rescue", "line band + one evidence word", or "组合限时阅读找证据即可"; use easy first, skip-return, proof count, return point, and hard-first repair
- integrated objective-reading lesson residue such as "Objective Reading: Line-Band Rescue", "客观题综合找证据即可", or "顺利学生做；若证据不稳，退回 line band"; use question type, evidence, boundary, review/next action, and one concrete repair
- reading-response locate/rewrite lesson residue such as "Line-Band Rescue", "Line Bank only", or "阅读表达找证据即可"; use question form, needed words, answer starter, cut words, subject match, and tense check
- open reading-response lesson residue such as "Open Response: Line Bank only", "开放回答题找证据即可", "retell the whole story", or "personal opinion first"; use answer position, text fact, because link, boundary, retelling cut, slogan-only rejection, and safe personal link
- sentence-upgrade writing lesson residue such as "Sentence Upgrade: reader/purpose only", "Prompt card + rescue + repeat", or "顺利学生做；若句子不稳，退回简单句"; use safe base, connector meaning, one upgrade, added-verb check, and stop/return-to-base
- timed-writing lesson residue such as "Timed Writing: reader/purpose only", "Prompt card + rescue + repeat", or "顺利学生做；若句子不稳，退回简单句"; use reader/purpose, topic-time-place-reason outline, opening/small text, missing-point check, and plan-write-check
- final-review lesson residue such as "Final Review: Plan Before Writing", "Tiny Prompt Repeat", "Low-Risk Writing Extension", "reader/purpose/required points only", "全卷讲评", or "be careful" as the only review action; use one repeated error, proof place, next first step, transfer check, and vague-review repair
- overstrong inference wording such as "What must be true?" in student reading lessons when the method is about avoiding unsupported conclusions; use "What is directly true in the text?", "Text fact", or "What follows without adding a new reason?"
- backstop wording such as "Backup Passage", "Backup Full Passage", "备用阅读", or "备用补测" in student-facing handouts; use Optional/Additional Practice or a concrete task label
- internal tier labels such as "A轨", "B轨", "C轨", "Track A", "Foundation Track", "Core Track", "Advanced Track", "基础差", or "差生版" in student-facing course packs; use the outward course identity and keep placement logic internal
- fake tiering in course-pack language: do not call a version foundation/advanced only because titles, page counts, or timing labels changed. Foundation wording should make the task smaller and more doable; advanced wording should make evidence, distractor review, risk control, and next-sprint behavior more precise.
- reused reading/cloze materials presented as "Unseen Full Practice"; call them review/timed recovery tasks and track reuse internally
- in dual-course packaging, one student package mentioning the sibling course title, old course wrapper, master source name, raw build filename, or source/QA/archive directory
- visible production/layout rationale in finished student or teacher PDFs, such as "This page breaks the answer-key rhythm"; rewrite it as the classroom action, for example "Use this pause to decide which step deserves board time."

## Preserve

Do not weaken:

- exam terms: 单项选择、完形填空、阅读理解、首字母、完成句子、非谓语、定语从句
- grammar terms needed for accuracy: 主谓宾、主系表、状语、定语、宾语从句
- source facts: year, school, exam paper, question number, answer key
- concrete student tasks: 背诵、默写、重做、圈出、划出、改错、限时
- authentic Chinese writing prompts or identity setups from exams such as Tianjin English writing tasks

## Good Visible Style

Prefer:

- "先圈出句子的主语和谓语。"
- "这组题重点练的是动词形式。"
- "做完后回看错题，标出自己是卡在词义、词性还是时态。"
- "这个知识点不用背复杂定义，先能在句子里认出来。"
- "今天先把基础句型写准，再进入更复杂的从句。"
- Early reading scaffold: "Detail Questions: Evidence First (细节证据)"
- Later reading practice: "Locate the sentence that answers the question."
- Later reading response: "Rewrite the answer in your own words."

Avoid:

- "通过入口卡片回收动作链。"
- "本节课建立了完整的能力闭环。"
- "后续将进入短程维修路由。"
- "教师动作：先让学生暴露错误。"
- "填写动作得分卡和自检卡。"
- "0-10 五题热身 个人预测。"
- "B01-B05 句子入口。"
- "第20讲 学生版。"
- "first draft / prototype / local absolute path"
- "讲评：教师用处理。"
- "参考答案：A。解析：..."
- "阅读细节定位：题干关键词 / 定位句 / 同义改写" as the main task surface in later English reading practice
- "Evidence链 / 第本阶段讲阅读工具 / 圈but/however/instead/yet"
- "博物馆导览与灵活执行 第16空："
- "第07-08讲工具 / 第10-13讲阅读工具"
- "课程地图：第01-06讲语法，07-09讲完形，10-16讲阅读"
- "source_id: TJGK-PAPER-2024-T1"
- "Teacher Evidence: TJGK-2025A-CLOZE-18 / L12-EC03 / T16"
- "reading · 原创天津高考仿真"
- "真题精拆：2021 Pruitt 修自行车"
- "完整仿真篇章 20 空"
- "Stage 2"
- "Unit Review"
- "工具阶段收束"
- "错因记录与工具带走"
- "五类工具示范：升级与不用条件"
- "20 分钟示范 5 类工具"
- "训练工具"
- "复用材料：回看上一阶段 Passage B"
- "Unseen Full Practice: Old Maps and City Reading" when the passage has already appeared
- "今天承接今天的最小证据。"
- "主观题不是抄原文，是把证据变成合格我的作答。"
- "B. Cloze: 2025 Tianjin A, Blanks 本阶段"
- "Objectivequestion pacing"
- "four week round-two plan"
- "Sprint High-Score Sprint Setup"
- "加练加练"
- "第本课程"
- "目录页码用于全册查找；正文页眉用于每一节内部翻找。"
- "A kid is allowed to visit the Garden when they are (blank)."
- "A4 total book with stage openers and lesson bodies."
- "A4 teacher total book: front matter plus classroom guide bodies."
- "This combined book was generated from lesson packs."
- "正文页眉用于本讲内部查找。"
- "工具调用 / 工具选择 / Tool to use / tool selection" in student-facing exam packs
- "Backup Passage: Old Maps and City Reading"
- "备用阅读：旧地图展与城市阅读"
- "Teaching control: 执行时先给学生30至60秒独立观察。学生回答后，把依据写在题目旁边。"
- "顺利学生做；若低错不稳，退回 core。"
- "顺利学生做；若证据不稳，退回 line band。"
- "词义/态度题：找证据即可。"
- "态度不稳就退回 line band。"
- "Start + mood labels + evidence table + repeat."
- "主旨结构题：Line-Band Rescue。先找 line band + one evidence word。"
- "Main idea: just find evidence lines."
- "主旨题找证据即可。"
- "组合限时阅读：Line-Band Rescue。先找 line band + one evidence word。"
- "Reading Set: just follow line bands and answer in order."
- "Timed reading rescue: 找证据即可，不需要 skip-return。"
- "Objective Reading: Line-Band Rescue。客观题综合找证据即可。"
- "综合客观阅读：顺利学生做；若证据不稳，退回 line band。"
- "阅读表达题：Line-Band Rescue。Line Bank only，找到原句即可。"
- "Reading Response: copy full sentence from the line bank."
- "开放回答题：Line-Band Rescue。只找 line band，不写 answer position。"
- "Open Response: Line Bank only, copy facts and then add personal opinion."
- "Open response page: retell the whole story; no answer position needed."
- "Paragraph Expansion: reader/purpose only; Prompt card + rescue + repeat."
- "段落展开：只拆 reader / purpose，顺利学生做；若句子不稳，退回简单句。"
- "Final Review: Plan Before Writing. Read reader/purpose/required points only."
- "Low-Risk Writing Extension：全卷讲评后，顺利学生做；若句子不稳，退回简单句。"
- "Review cue After the key table, ask students to name the clue type before the answer."
- "This page breaks the answer-key rhythm and gives the teacher a live decision point."
- "02-06 / 07-09" in a student-facing route or stage table
- "1-2 / 3-4 / 5-6" as bare line-band labels in a student reading table
- "本阶段分钟"
- "课堂中必须保留30分钟连续写作"
- "示范样文只能在学生一稿完成后展示"
- "ev- ery / a- gainshe / expectationoi / fourweek"

## English-Forward Reading Practice

For K12 English reading handouts, match the visible language to the stage of training:

- Early bridge lessons may use bilingual labels, especially when a method is new.
- Middle lessons should use English headings, table labels, and short task instructions with only minimal Chinese support.
- Later reading, reading-response, and integrated exam-practice lessons should use English section titles, English question stems, and Gaokao-style task wording whenever the target exam expects students to process English.
- Do not translate authentic Chinese writing prompts away just to make the page look English. If the exam prompt is naturally Chinese, preserve it and make the surrounding labels English-forward.
- For cloze and reading exam-simulation pages, label blanks/questions in English (`Blank 16`, `Question 40`, `Evidence`) instead of Chinese production titles plus `第N空`.
- For cloze practice, verify that the passage actually contains every visible `Blank N`, the evidence-record table uses the same blank numbers, and answer keys/options are real rather than placeholder repetitions.
- If a reading set reuses previously taught passages, label it as review or timed recovery. Do not make it look like unseen full exam simulation.

## Final Readback

Before finalizing visible text:

1. Could a student or parent understand it without knowing Eric's internal system?
2. Does it tell the learner what to do, not what the teacher-agent did?
3. Are all internal terms removed or translated?
4. Is every praise, warning, or instruction tied to real teaching content?
5. Does the text sound like a teacher, not a lesson-production pipeline?
6. For student PDFs, are name/date fields limited to the cover or first identity area unless there is a real per-page collection need?
7. For worksheet tables, do answer lines sit at the lower writing position rather than floating through the middle of cells?
8. In cloze, do passage blank numbers, question labels, evidence tables, and answer keys all agree?
9. Does student-facing strategy language avoid tool-routing words such as "工具调用", "阅读工具", or "Tool to use"?
10. Does a student lesson avoid standalone course maps unless Eric explicitly requested a visible overview?
11. Are source labels and reuse status kept in manifests/teacher notes, with student pages using only the practice role?
12. For English reading practice, does the amount of English increase as the course moves toward real exam simulation?
13. For cloze practice, do passage blanks, question labels, evidence tables, and teacher keys all refer to the same blank numbers?
14. For teacher guides, are source/question codes converted to classroom-readable labels rather than printed raw?
15. Are repeated teacher-control notes concrete enough to help teach this exact task, rather than generic boilerplate repeated block by block?
16. If the same content is packaged into two courses, does this student-facing file show only its own course identity, with no sibling title, master title, build filename, source path, QA path, or archive residue?
17. In inference lessons, does the wording separate direct text facts from safe conclusions, instead of pushing students toward overstrong `must be true` claims?
17. Do navigation notes sound like reader-facing book language (`定位每一节内容`) rather than production/search language (`内部翻找`)?
18. Do exam-style question stems use real blanks or natural wording rather than generator placeholders such as `(blank)`?
19. Does total-book front matter describe student/teacher use in natural book language, rather than production packaging such as `A4 total book`, `combined book`, `generated from`, or `stage openers and lesson bodies`?
20. Does total-book navigation avoid internal-workflow words such as `内部查找` or `内部翻找`, using reader language such as `快速查找` instead?
21. For paragraph-expansion writing lessons, does the page make students practise point, support detail, because/link, low-error sentence check, and vague-word repair instead of only reader/purpose analysis?
22. For sentence-upgrade writing lessons, does the page make students practise safe base, connector meaning, one upgrade, added-verb check, and stop/return-to-base instead of only reader/purpose or generic prompt analysis?
23. For timed-writing lessons, does the page make students practise reader/purpose, topic-time-place-reason outline, opening/small text, missing-point check, and plan-write-check instead of only reader/purpose or generic prompt analysis?
24. For integrated objective-reading lessons, does the page make students practise question type, evidence, boundary, and review/next action instead of only line locating or a generic evidence table?
25. For final-review lessons, does the page make students practise one repeated error, proof place, next first step, transfer check, and vague-review repair instead of only generic writing prompt analysis?
26. For teacher guides, did any one-sentence `Review cue` or `Teaching cue` become a standalone page? Merge it into the answer/evidence/control layer or rewrite it as a real classroom decision table.
27. For teacher guides, did any wording explain the layout repair itself, such as `breaks the answer-key rhythm` or `page rhythm`? Replace it with a teacher decision or classroom action.
28. Does total-book front matter avoid label collisions such as `RoutinePage Routine`, `Teacher Control`, or production descriptions like `A4 teacher total book`?
29. If a source contract legitimately names a teacher-only step such as `教师反馈`, is the student-visible renderer filtering it instead of rewriting the upstream teaching contract into a weaker or test-breaking term?
30. Do tiered-course covers avoid abstract role chips such as `Small Step / Evidence / Low Error` or `Timed / Risk / Transfer`, keeping the visible cover aligned with the core/B book family?
