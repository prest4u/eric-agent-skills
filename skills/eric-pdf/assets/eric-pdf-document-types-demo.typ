#import "eric-pdf-template.typ": *

#setup-hermes-page()

#hermes-cover(
  [Eric PDF 类型模板],
  [亮暖编辑风格样张],
  [2026-06-16 · Anthropic-light 方向，保留课堂纸面秩序，减少灰白框感],
)

#eric-body(title: [Eric PDF 类型模板])[
= 文件类型总览

#eric-meta[
适用：课堂练习、课上笔记、课后作业、教师教案、复习手册、表达手册#linebreak()
原则：同一套纸面气质，不同文件靠功能组件区分。
]

#v(8pt)
#hermes-table(
  (1fr, 1.25fr, 1.45fr),
  (
    [文件类型], [页面任务], [优先组件],
    [课堂练习], [让学生在课堂中完成、记录、对照], [限时条、题目区、答案格、线索表、错因表],
    [课上笔记], [让学生课后 30 秒能找回规则], [规则框、速查表、检查清单、个人记录],
    [课后作业], [让学生每天照着执行], [任务卡、打卡表、短练习、完成标准],
    [教师教案], [让老师控制节奏和讲评], [教师条、分钟流程、答案依据、观察记录],
    [复习/词库手册], [让学生先会查，再能调用], [使用方法、场景目录、调用入口、词库表、小练],
    [表达手册], [让学生写得出来、改得上去], [表达库、句式框架、改写对照、书写线],
  )
)

#pagebreak()
= 场景词库手册页

#eric-meta[
目标：像《首字母填空场景词汇手册》一样，让学生先按场景调用候选词，再用句子位置和词形落地。
]

== 使用方法

#eric-method-steps(
  [先看场景],
  [判断文章是在科技、家庭、安全、交通还是自然气候中展开。],
  [再看功能],
  [空格表达的是动作、状态、对象、连接，还是语篇推进。],
  [最后词形],
  [检查单复数、时态、三单、过去式、比较级、副词化和搭配。],
)

== 场景目录

#grid(
  columns: (1fr, 1fr),
  column-gutter: 12pt,
  row-gutter: 10pt,
  eric-directory-card([01], [科技服务], [机器人、餐厅、设备、新技术进入生活。], count: [32 个可调用词]),
  eric-directory-card([02], [安全灾害], [地震、危险、救援、避险动作和安全训练。], count: [28 个可调用词]),
  eric-directory-card([03], [时间发明], [时间、发明、测量工具、技术改进和历史发展。], count: [32 个可调用词]),
  eric-directory-card([04], [家庭生活], [家庭成员、房间、家务、陪伴和日常活动。], count: [32 个可调用词]),
)

#pagebreak()
= 01 科技服务

#text(size: 12pt)[机器人、餐厅、服务、设备和新技术进入生活。]

#v(8pt)
#eric-lookup-strip([调用入口], [服务动作 / 设备运行 / 评价状态 / 费用数量])

#text(size: 10pt, weight: 700, fill: c-amber)[真题里出现过的核心词]
#v(4pt)
#eric-vocab-table(
  (
    [词], [首], [词性], [中文义], [调用与词形],
    [experience], [e], [n.], [经验；经历], [主题对象；先确定词义，再按句子位置检查词性和拼写。],
    [prepared], [p], [v.], [准备；筹备], [动作发生；重点检查时态、三单、过去式、被动和非谓语。],
    [delicious], [d], [adj.], [美味的], [状态评价；重点检查修饰对象、比较级和副词化。],
    [electricity], [e], [n.], [电；电力], [主题对象；常与设备、能源和生活服务相关。],
  )
)

#text(size: 10pt, weight: 700, fill: c-amber)[同场景扩展候选词]
#v(4pt)
#eric-vocab-table(
  (
    [词], [首], [词性], [中文义], [调用功能],
    [robot], [r], [n.], [机器人], [事物对象],
    [restaurant], [r], [n.], [餐厅], [事物对象],
    [serve], [s], [v.], [服务；提供], [动作发生],
    [technology], [t], [n.], [技术], [事物对象],
  )
)

#text(size: 10pt, weight: 700, fill: c-amber)[首字母小练]
#v(4pt)
#eric-initial-drill-table(
  (
    [序号], [线索], [我填], [依据],
    [练习 1], [科技服务场景中，空格要表达“服务动作”，首字母是 s。], [], [],
    [练习 2], [科技服务场景中，空格要表达“主题对象”，首字母是 r。], [], [],
    [练习 3], [科技服务场景中，空格要表达“状态评价”，首字母是 d。], [], [],
  )
)

#pagebreak()
= 课堂练习页

#eric-meta[
学生：示例学生#linebreak()
日期：2026-06-16#linebreak()
目标：限时完成后，能说清每一空的依据。
]

== 一、限时首字母 R1

#eric-timed-strip([8 分钟 · 到时间停笔], [先标结构类型，再画跨句线索，最后填词。])

*《The Speech》*

Maya had always been the quietest person in her class. She never raised her hand, never volunteered for anything, and s#blank  ① spoke in front of others. So when her teacher announced that every student had to give a five-minute speech, Maya felt her heart drop.

"I can't do it," she told her grandfather that evening. "Everyone will l#blank  ② at me."

Her grandfather handed her an old coin. "Before he gave an important speech, he would hold it in his pocket. Not for luck — to r#blank  ③ himself that his words mattered."

#v(4pt)
#hermes-table(
  (0.6fr, 0.8fr, 1.8fr, 0.7fr),
  (
    [空号], [答案], [线索来源], [自检],
    [①], [], [], [#checkbox],
    [②], [], [], [#checkbox],
    [③], [], [], [#checkbox],
  )
)

#eric-rule-box(
  [本页编排要点],
  [练习页不做花哨分栏。先保证题目连续可读，再用表格承接答案、线索和自检。]
)

#pagebreak()
= 完形填空页

#eric-meta[
目标：ABCD 选项呈现要像正式试卷，不能做成表格框。
]

== 二、限时完形 R1

#eric-timed-strip([8 分钟 · 10 空], [先通读，把握人物关系和情绪变化，再逐空判断。])

*《The Note》*

Nina and Rosa had been best friends since kindergarten. They did everything together — walked to school, shared lunch, and told each other every (1)#blank . But three weeks ago, something changed.

It started with a small thing. Nina forgot to invite Rosa to her birthday dinner. It wasn't on purpose — Nina's mother had planned everything at the last minute, and Nina simply (2)#blank  to tell Rosa.

#v(4pt)
#eric-choice-row([1], [story], [secret], [lesson], [subject])
#eric-choice-row([2], [remembered], [tried], [forgot], [refused])
#eric-choice-row([3], [break], [keep], [fill], [enjoy])
#eric-choice-row([4], [lost], [found], [stuck], [hidden])

#v(4pt)
#eric-choice-answer-grid(count: 4)

#eric-rule-box(
  [完形选项编排要点],
  [选项本身用横排试卷感，不加边框。答案记录区可以用表格，因为它是答题工具，不是题目选项。]
)

#pagebreak()
= 课上笔记页

#eric-meta[
核心：把课堂规则压缩成考前能快速翻看的纸面。
]

== 一、虚拟语气规则速查

#eric-note-box(
  [两条主规则],
  [现在虚拟：if + 过去式，would + 动词原形#linebreak()
过去虚拟：if + had done，would + have done#linebreak()
as if / as though 后常用虚拟表达非真实情境。]
)

#hermes-table(
  (1fr, 1fr, 1fr, 1fr),
  (
    [类型], [if 从句], [主句], [用于],
    [现在虚拟], [if + 过去式], [would + 动原], [和现在事实相反],
    [过去虚拟], [if + had done], [would + have done], [和过去事实相反],
  )
)

== 二、考试时三问

#eric-rule-box(
  [每做完 5 个空，停下来问自己],
  [1. 词性对吗？#linebreak()
2. 线索够吗？#linebreak()
3. 变形查了吗？]
)

#pagebreak()
= 课后作业页

#eric-meta[
原则：临考作业不追求长，追求每天能执行、能打卡、能保持手感。
]

== 每日 3 件事

#eric-task-card(
  [1. 高频短语默写 · 5 分钟],
  [用纸挡住英文，看中文写英文。错的短语写 3 遍，第二天优先复查。]
)

#eric-task-card(
  [2. 首字母 1 篇限时 · 5 分钟],
  [先标结构类型，再画至少 1 条跨句线索。到时间必须停笔。]
)

#eric-task-card(
  [3. 错词本翻看 · 5 分钟],
  [只看最近错过的 5 个词，说出正确形式和当时为什么写错。]
)

#hermes-table(
  (1fr, 1fr, 1fr, 1fr),
  (
    [日期], [短语], [首字母], [错词本],
    [周一], [#checkbox], [#checkbox], [#checkbox],
    [周二], [#checkbox], [#checkbox], [#checkbox],
    [周三], [#checkbox], [#checkbox], [#checkbox],
  )
)

#pagebreak()
= 教师教案页

#eric-teacher-strip[含完整流程、答案、观察记录]

#eric-meta[
课型：限时稳定性冲刺#linebreak()
目标：观察学生在限时压力下哪一步先脱落，并转化为下一轮讲评。
]

== 课堂流程

#hermes-table(
  (0.75fr, 1.1fr, 1.8fr, 1fr),
  (
    [时间], [环节], [课堂动作], [观察],
    [0-5], [快查], [口头激活旧知识，不展开新讲解], [反应速度],
    [5-13], [限时 R1], [计时完成，停笔后先记录空题数], [是否跳步骤],
    [13-23], [讲评], [按答案、依据、词形三栏讲], [错因类别],
  )
)

#eric-rule-box(
  [教师页编排要点],
  [教师教案可以更密，但必须让时间、动作、答案、观察一眼分开。学生版不能出现教师专用语言。]
)

#pagebreak()
= 表达手册页

#eric-meta[
目标：让学生从"知道表达"走到"能写出来"。
]

== 观点表达句式

#hermes-table(
  (1fr, 1.4fr, 1.4fr),
  (
    [功能], [基础表达], [升级表达],
    [提出观点], [I think reading is useful.], [In my opinion, reading helps us understand the world better.],
    [解释原因], [It is good for us.], [This is because it gives us both knowledge and confidence.],
    [总结], [So we should read more.], [Therefore, it is worth building a daily reading habit.],
  )
)

== 我的仿写

#eric-writing-area(lines: 8, label: [写作区：每行留足高度，适合双面打印后手写。])
]
