#import "eric-pdf-template.typ": *

#let version = sys.inputs.at("version", default: "teacher")
#let version-label = if version == "teacher" { [教师版] } else { [学生版] }

#setup-hermes-page()

#hermes-cover(
  [数学专题方案模板],
  [函数压轴与几何证明 · #version-label],
  [2026-06-16 · Anthropic-light 数学框架样张 · 概念入口到错因闭环],
)

#eric-body(title: [数学专题方案模板])[
= 使用方法与专题地图

#eric-meta[
版本：#version-label#linebreak()
目标：用亮暖、克制的纸面，把数学材料从“看懂解析”改成“会定位条件、会写步骤、会订正错因”。
]

#eric-method-steps(
  [先定对象],
  [题目研究的是函数、图形、数列还是概率；先把变量和已知条件写出来。],
  [再选工具],
  [判断要用公式、图形、方程、导数、相似、面积还是分类讨论。],
  [最后落笔],
  [每一步写依据；计算区不跳步，结论要回到题目问题。],
)

== 专题地图

#hermes-table(
  (1fr, 1.3fr, 1.7fr, 1.2fr),
  (
    [模块], [核心动作], [典型题型], [记录方式],
    [概念入口], [定义条件], [函数单调性、最值、零点], [公式框],
    [解答题流程], [观察到结论], [导数大题、函数压轴], [流程表],
    [几何证明], [读图到理由], [相似、圆、角度、辅助线], [证明表],
    [错因归档], [订正复查], [漏条件、算错、跳步], [错因表],
  )
)

#pagebreak()
= 概念入口页

#eric-math-formula-box(
  [导数判断单调性],
  [$f'(x) > 0 => f(x) "在该区间单调递增", quad f'(x) < 0 => f(x) "在该区间单调递减"$],
  [函数在区间内可导；需要先确定定义域和分界点。],
  note: [导数符号表不是答案本身，必须回到原函数的区间和题目问题。],
  misuse: [只写 $f'(x)=0$，没有检查区间、端点和左右符号。],
)

#eric-math-formula-box(
  [几何证明的三段式],
  [$"已知条件" -> "中间结论" -> "目标结论"$],
  [每一步都要有理由：平行、相似、全等、圆周角、垂直或等量代换。],
  note: [证明题不是把图看懂就结束，必须把“为什么”写在理由栏。],
  misuse: [只写结论，不写定理依据。],
)

== 考前 30 秒自检

#eric-rule-box(
  [做数学题先问三件事],
  [1. 定义域、变量范围或图形条件写了吗？#linebreak()
2. 每一步有没有依据？#linebreak()
3. 最终答案有没有回到原题问题？]
)

#eric-math-error-log(rows: 3)

#pagebreak()
= 函数压轴页

#eric-math-example(
  [1],
  [含参数函数的单调性与最值],
  [已知函数 $f(x)=x^3-3x^2+a$。讨论 $f(x)$ 在区间 $(0,+infinity)$ 上的单调性，并说明参数 $a$ 是否影响单调性。],
  tags: [高考基础模型 · 导数符号表 · 参数识别],
  difficulty: [Level 2],
)

#eric-math-diagram-panel(
  [导数符号观察],
  [
    #eric-math-coordinate-grid(cols: 10, rows: 6, height: 120pt, x-label: [$x$], y-label: [$f'(x)$], origin-label: [$0$])
  ],
  note: [在坐标平面或符号线上标出 $x=0$、$x=2$ 以及 $f'(x)$ 的正负变化。],
)

#eric-math-solution-block(
  [安全双版本 · 例 1 解题流程],
  [
    #eric-math-large-question-table(
      (
        [阶段], [学生动作], [数学表达], [结论],
        [观察], [先看参数是否影响导数], [$f'(x)=3x^2-6x$], [$a$ 不进入导函数],
        [设点], [找导数分界点], [$3x(x-2)=0$], [$x=0,2$],
        [转化], [在给定区间判断符号], [$(0,2)$ 负，$(2,+infinity)$ 正], [先减后增],
        [回题], [写单调区间和参数结论], [与 $a$ 无关], [$a$ 不影响单调性],
      )
    )
    #eric-math-final-answer-box(body: [$f(x)$ 在 $(0,2)$ 上单调递减，在 $(2,+infinity)$ 上单调递增，$a$ 不影响单调性。])
  ],
  version: version,
  student: [
    #eric-rule-box(
      [提示],
      [先求 $f'(x)$，再把导函数因式分解；注意参数 $a$ 是否出现在导函数里。]
    )
  ],
)

#pagebreak()
= 解答题流程页

#eric-math-example(
  [2],
  [闭区间上的最值],
  [已知 $g(x)=x^3-6x^2+9x+1$，求 $g(x)$ 在 $[0,4]$ 上的最大值和最小值。],
  tags: [端点 · 驻点 · 列表比较],
  difficulty: [Level 2],
)

#eric-math-known-target-table(
  (
    [对象], [$g(x)=x^3-6x^2+9x+1$],
    [区间], [$[0,4]$],
    [目标], [最大值、最小值以及对应的 $x$],
    [必须检查], [端点 $0,4$ 与区间内驻点],
  )
)

#eric-math-workspace(lines: 9, mode: "ruled", label: [规范书写区：求导、找驻点、代入端点和驻点、比较。])

#eric-math-final-answer-box()

#eric-math-solution-block(
  [例 2 评分点],
  [
    #eric-math-score-rubric(
      (
        [项], [得分点], [分值],
        [计算], [正确求出 $g'(x)=3(x-1)(x-3)$], [2],
        [比较], [端点和驻点全部代入], [2],
        [表达], [最大值/最小值结论完整], [1],
      )
    )
  ],
  version: version,
)

#pagebreak()
= 几何证明页

#eric-math-example(
  [3],
  [相似三角形证明],
  [如图，$triangle A B C$ 中，$D$ 在 $"BC"$ 上，$A D$ 是辅助线。若 $angle B A D = angle A C B$，证明 $triangle A B D ~ triangle C A B$。],
  tags: [中考几何 · 读图标角 · 证明链],
  difficulty: [Level 3],
)

#grid(
  columns: (1fr, 1fr),
  column-gutter: 14pt,
  [
    #eric-math-diagram-panel(
      [几何图形区],
      [
        #eric-math-triangle-diagram(a: [A], b: [B], c: [C], d: [D], aux: [$A D$])
      ],
      note: [学生先在图上标角，再填写右侧表格。复杂真题图必须使用原题裁切、GeoGebra 导出图或经验证的矢量图。],
    )
  ],
  [
    #eric-math-known-target-table(
      (
        [已知], [$angle B A D = angle A C B$],
        [所求], [$triangle A B D ~ triangle C A B$],
        [可用理由], [公共角、两角对应相等],
        [辅助线], [$A D$],
      )
    )
  ],
)

#eric-math-solution-block(
  [几何证明链],
  [
    #eric-math-proof-table(
      (
        [步], [结论], [理由], [得到],
        [1], [$angle B A D = angle A C B$], [已知], [一组对应角相等],
        [2], [$angle A B D = angle C A B$], [公共结构/图形关系], [第二组对应角相等],
        [3], [$triangle A B D ~ triangle C A B$], [两角对应相等], [相似结论],
      )
    )
  ],
  version: version,
  student: [
    #eric-math-proof-table(
      (
        [步], [结论], [理由], [得到],
        [1], [], [], [],
        [2], [], [], [],
        [3], [], [], [],
      )
    )
  ],
)

#pagebreak()
= 变式训练与答题结构

#eric-action-strip([12 分钟 · 4 题], [同一方法连续做：读条件、选工具、写过程、回题。])

#hermes-table(
  (0.45fr, 2.6fr, 1fr, 1fr),
  (
    [题], [题目], [题型], [完成],
    [1], [$y=x^3-3x$ 在 $[-2,2]$ 上的最值。], [导数大题], [#checkbox],
    [2], [$y=x^4-4x^2$ 的单调区间。], [函数压轴], [#checkbox],
    [3], [$y=x^3-a x$ 的极值点个数随 $a$ 的变化。], [分类讨论], [#checkbox],
    [4], [在几何图中补一条辅助线并证明两三角形相似。], [几何证明], [#checkbox],
  )
)

#eric-math-answer-grid(kind: "mixed", count: 4)

#eric-math-workspace(lines: 11, mode: "blank", label: [整页演算区：每题之间自己留出分隔线，最终答案写入上方答案格。])

#pagebreak()
= 学习复盘页

#eric-note-box(
  [复盘任务],
  [回看本专题中最容易跳步的位置：定义域、导函数因式分解、端点代入、几何理由、结论回题。把自己的错题补到下面的错因表。]
)

#eric-math-error-log(rows: 5)

#eric-math-solution-block(
  [教师复盘讲评],
  [
    #eric-note-box(
      [讲评提醒],
      [优先追问“为什么这一步成立”，再追问“答案是否回到题目问题”。不要只核对最终数值。]
    )
  ],
  version: version,
)
]
