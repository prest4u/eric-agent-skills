// Eric Slate White PDF｜雾蓝白
// Eight-page editorial role gallery and editable starter.
// Keep geometry shared with Eric Moss Ivory PDF; change theme tokens only.

#let document-title = __DOCUMENT_TITLE_JSON__
#let document-subtitle = __DOCUMENT_SUBTITLE_JSON__

#let paper = rgb("#F4F5F3")
#let ink = rgb("#24282A")
#let muted = rgb("#747B7E")
#let micro = rgb("#626B6F")
#let hair = rgb("#CCD2D3")
#let primary = rgb("#5D6C75")
#let secondary = rgb("#7D8990")

#let serif = ("Songti SC", "STSong")
#let sans = ("PingFang SC", "Hiragino Sans GB")
#let quote-face = ("STFangsong", "Songti SC")
#let latin = ("Avenir Next", "Helvetica Neue")

#set document(
  title: document-title,
  author: "",
  keywords: ("Eric Slate White PDF", "雾蓝白", "editorial"),
)

#set page(
  paper: "a4",
  margin: (top: 24mm, bottom: 22mm, left: 25mm, right: 25mm),
  fill: paper,
)
#set text(
  font: serif,
  size: 10.2pt,
  weight: "regular",
  fill: ink,
  lang: "zh",
  tracking: 0.012em,
)
#set par(justify: true, leading: 0.96em, spacing: 0.74em)
#set heading(numbering: none)

#let footer() = context [
  #set text(font: latin, size: 7pt, fill: micro, tracking: 0.03em)
  #grid(
    columns: (1fr, auto),
    [ERIC SLATE WHITE PDF],
    [#counter(page).display("01")],
  )
]

#let eyebrow(body, tone: secondary) = text(
  font: latin,
  size: 7.2pt,
  weight: "semibold",
  fill: tone,
  tracking: 0.16em,
  body,
)

#let display(body, size: 25pt) = text(
  font: serif,
  size: size,
  weight: "bold",
  fill: ink,
  tracking: -0.018em,
  body,
)

#let lead(body) = [
  #set text(font: sans, size: 11.5pt, fill: ink, tracking: 0.01em)
  #set par(justify: false, leading: 1.02em, spacing: 0.6em)
  #body
]

#let label(body, tone: primary) = text(
  font: latin,
  size: 7.6pt,
  weight: "semibold",
  fill: tone,
  tracking: 0.07em,
  body,
)

#let quiet(body) = [
  #set text(font: sans, size: 8.6pt, fill: micro, tracking: 0.006em)
  #set par(justify: false, leading: 0.98em, spacing: 0.4em)
  #body
]

#let pull(body, size: 16.5pt, tone: primary) = [
  #set text(font: quote-face, size: size, fill: tone, tracking: 0.022em)
  #set par(justify: false, leading: 1.08em, spacing: 0.3em)
  #body
]

#let split-rule() = grid(
  columns: (2.35fr, 1fr),
  gutter: 0mm,
  line(length: 100%, stroke: 0.7pt + primary),
  line(length: 100%, stroke: 0.7pt + secondary),
)

#let rail-head(number, kicker, title, premise: none) = grid(
  columns: (16mm, 1fr),
  gutter: 10mm,
  [
    #text(font: latin, size: 9.6pt, weight: "semibold", fill: primary)[#number]
    #v(5mm)
    #line(start: (50%, 0%), end: (50%, 28mm), stroke: 0.9pt + primary)
    #line(start: (50%, 0%), end: (50%, 10mm), stroke: 0.9pt + secondary)
  ],
  [
    #eyebrow(kicker)
    #v(5.5mm)
    #display(title)
    #if premise != none [
      #v(6mm)
      #lead(premise)
    ]
  ],
)

#let side-note(title, body, tone: secondary) = block(
  width: 100%,
  inset: (left: 4mm, top: 1.5mm, bottom: 1.5mm),
  stroke: (left: 0.8pt + tone),
)[
  #label(title, tone: tone)
  #v(2.5mm)
  #quiet(body)
]

#let evidence-row(tag, body, tone: primary) = [
  #grid(
    columns: (25mm, 1fr),
    gutter: 6mm,
    [#label(tag, tone: tone)],
    [#body],
  )
  #v(4.5mm)
  #line(length: 100%, stroke: 0.5pt + hair)
  #v(4.5mm)
]

// 01 · COVER
#set page(footer: none)
#v(15mm)
#eyebrow([ERIC SLATE WHITE PDF · EDITORIAL SYSTEM])
#v(22mm)
#grid(
  columns: (16mm, 1fr),
  gutter: 10mm,
  [
    #text(font: latin, size: 9pt, weight: "semibold", fill: primary)[SW]
    #v(6mm)
    #line(start: (50%, 0%), end: (50%, 62mm), stroke: 0.9pt + primary)
    #v(2mm)
    #line(start: (50%, 0%), end: (50%, 14mm), stroke: 0.9pt + secondary)
  ],
  [
    #display(document-title, size: 35pt)
    #v(11mm)
    #text(font: sans, size: 10.8pt, fill: muted)[#document-subtitle]
  ],
)
#v(1fr)
#split-rule()
#v(5mm)
#grid(
  columns: (1fr, 1fr),
  gutter: 18mm,
  [
    #label([SLATE · PRIMARY])
    #v(3mm)
    #quiet([章节骨架、主规则与关键引文。])
  ],
  [
    #label([SLATE LIGHT · SECONDARY], tone: secondary)
    #v(3mm)
    #quiet([英文眉题、分析提示与轻量层级。])
  ],
)

// 02 · SECTION OPENER
#pagebreak()
#set page(footer: footer())
#rail-head(
  [01],
  [THE QUESTION BENEATH THE QUESTION],
  [真正需要理解的，\ 不是“谁强谁弱”],
)
#v(16mm)
#pad(left: 26mm)[
  #pull([差距本身并不会自动生成敌意。\ 真正令人不适的，是差距冲击了一个人\ 关于自己的解释。], size: 18pt)
  #v(16mm)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 8mm,
    [
      #label([01 · COMPARISON])
      #v(3mm)
      #quiet([能力、资源、影响力或稳定感，在某个具体维度上出现明显差距。])
    ],
    [
      #label([02 · NARRATIVE], tone: secondary)
      #v(3mm)
      #quiet([“我是谁”的旧叙事受到现实挑战，心理开始寻找解释。])
    ],
    [
      #label([03 · DEFENCE])
      #v(3mm)
      #quiet([承认差距需要行动；否定对方可以迅速缓解压力。])
    ],
  )
]

// 03 · CONTINUOUS ESSAY
#pagebreak()
#rail-head(
  [02],
  [SELF-NARRATIVE & DEFENCE],
  [贬低往往在保护什么],
  premise: [每个人心里都有一套关于自己的叙事。现实一旦让它失去说服力，人会在承认、修正与防御之间做出选择。],
)
#v(9mm)
#grid(
  columns: (1fr, 42mm),
  gutter: 11mm,
  [
    当另一个人表现出更强的行动力、更稳定的判断或更高的认可度时，比较会带来一种直接的不适：过去那些解释自己的理由，忽然不再完整。

    承认差距意味着重新评估自己，也意味着付出时间、承担失败和开始行动。否认差距则更轻松。只要把对方的成果解释成运气、包装或关系，就能暂时恢复原有的心理平衡。

    因此，许多贬低并不是为了准确评价一个人，而是为了修复评价者自己的自我感。它像一剂短效止痛药：无法改变现实，却能延迟面对现实。

    理解这层机制，不等于把每个攻击者都定义成坏人。它只是提醒我们，评价的声音有时包含事实，有时也包含说话者尚未处理的痛感。
  ],
  [
    #side-note(
      [READER NOTE],
      [先区分“对方在描述什么”与“这段描述替他说话者解决了什么”。两者可能同时存在。],
    )
    #v(9mm)
    #side-note(
      [LANGUAGE],
      [避免把一个人整体定义为弱或强。更准确的单位，是具体维度、具体关系与具体情境。],
      tone: primary,
    )
  ],
)

// 04 · ARGUMENT / CONTRAST
#pagebreak()
#rail-head(
  [03],
  [COMPARISON & RESPONSE],
  [比较带来的不适，\ 会走向不同方向],
  premise: [同一种不安，可以被转化为学习，也可以被转化为敌意。关键并不在于是否比较，而在于一个人如何处理比较。],
)
#v(10mm)
#pad(left: 26mm)[
  #grid(
    columns: (1fr, 1fr),
    gutter: 9mm,
    [
      #label([转化为学习])
      #v(4mm)
      承认对方在某个维度上做得更好，把不适转化为信息，并将注意力移向可以学习、练习或重新选择的部分。
    ],
    [
      #label([转化为敌意], tone: secondary)
      #v(4mm)
      当暂时无法追赶，也无法接受差距时，通过否认、猜测动机或降低信誉，让自己重新获得心理上的位置。
    ],
  )
  #v(12mm)
  #block(
    width: 90%,
    inset: (left: 5mm),
    stroke: (left: 1.1pt + primary),
  )[
    #pull([当一个人被当作参照物，\ 他的存在可能同时激发学习与防御。])
  ]
  #v(12mm)
  #split-rule()
  #v(4mm)
  #quiet([
    相似者的成功尤其容易产生压力，因为它削弱了“绝对不可能”的解释；但背景、资源、关系和代价仍然不同，不能因此简化他人的处境。
  ])
]

// 05 · TRANSITION / QUOTATION
#pagebreak()
#v(23mm)
#eyebrow([A DELIBERATE PAUSE])
#v(32mm)
#grid(
  columns: (18mm, 1fr),
  gutter: 12mm,
  [
    #line(start: (50%, 0%), end: (50%, 75mm), stroke: 0.9pt + primary)
    #line(start: (50%, 0%), end: (50%, 22mm), stroke: 0.9pt + secondary)
  ],
  [
    #pull([
      有些人攻击的，\ 并不只是一个具体的人，\ 而是那个人所代表的可能性。
    ], size: 21pt)
    #v(18mm)
    #quiet([
      当一个人的存在让旧借口失效，群体会重新解释他：把积累说成投机，把边界说成傲慢，把确定性说成表演。此时需要保护的不是每个人心中的版本，而是事实与长期信誉。
    ])
  ],
)
#v(1fr)
#split-rule()

// 06 · EVIDENCE / JUDGEMENT
#pagebreak()
#rail-head(
  [04],
  [EVIDENCE BEFORE JUDGEMENT],
  [不是所有批评\ 都来自嫉妒],
  premise: [成熟的判断，不是先猜对方的心理，而是先看事实、推断、表达方式与真实影响。],
)
#v(9mm)
#pad(left: 26mm)[
  #grid(
    columns: (1fr, 0.6pt, 1fr),
    gutter: 7mm,
    [
      #label([有价值的批评])
      #v(4mm)
      提供可核实的事实\
      区分事实与推断\
      针对具体行为\
      允许回应与修正
    ],
    [#line(start: (50%, 0%), end: (50%, 56mm), stroke: 0.6pt + hair)],
    [
      #label([需要警惕的贬损], tone: secondary)
      #v(4mm)
      猜测并固化动机\
      夸大并人格化\
      标准随听众变化\
      拒绝核查与回应
    ],
  )
  #v(11mm)
  #evidence-row([FACT], [“你上次在会议里打断了三个人。”])
  #evidence-row([INFERENCE], [“他这个人一直都很虚伪。”], tone: secondary)
  #evidence-row([CHECK], [是否可核实？是否允许回应？是否与实际影响相称？])
  #v(2mm)
  #quiet([渠道只是辅助信号。私下表达可能源于权力差异；公开表达也不天然等于真实。证据仍然是判断基础。])
]

// 07 · NUMBERED PROCESS
#pagebreak()
#rail-head(
  [05],
  [A CALMER RESPONSE],
  [面对议论时，\ 先处理真正重要的部分],
  premise: [回应不是为了赢得每一个人，而是为了保护事实、边界与长期合作条件。],
)
#v(10mm)
#pad(left: 26mm)[
  #grid(
    columns: (14mm, 1fr),
    row-gutter: 7mm,
    [
      #text(font: latin, size: 15pt, weight: "medium", fill: primary)[1]
    ],
    [
      #label([检查事实])
      #v(2mm)
      先确认是否存在真实问题。把行为、影响和证据从对人格与动机的推断中分开。
    ],
    [
      #text(font: latin, size: 15pt, weight: "medium", fill: secondary)[2]
    ],
    [
      #label([判断影响], tone: secondary)
      #v(2mm)
      零散情绪通常不值得扩大；已经影响合作、信任或声誉时，再进入澄清与记录。
    ],
    [
      #text(font: latin, size: 15pt, weight: "medium", fill: primary)[3]
    ],
    [
      #label([选择渠道])
      #v(2mm)
      面向真正相关的人，提供必要事实。避免在不愿理解的人群中反复解释自己。
    ],
    [
      #text(font: latin, size: 15pt, weight: "medium", fill: secondary)[4]
    ],
    [
      #label([维护边界], tone: secondary)
      #v(2mm)
      不接受别人对你动机和人格的任意定义，也不靠贬低对方确认自己的价值。
    ],
  )
]

// 08 · CONCLUSION
#pagebreak()
#v(14mm)
#eyebrow([CONCLUSION · FACTS, BOUNDARIES, REPUTATION])
#v(14mm)
#display([真正需要维护的，\ 不是每个人脑海中的版本], size: 29pt)
#v(12mm)
#lead([
  理解攻击背后的防御机制，可以帮助我们减少无效纠缠；保留对批评的辨别能力，则避免我们把“嫉妒”变成逃避反思的新借口。
])
#v(16mm)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 8mm,
  [
    #label([FACTS])
    #v(4mm)
    #quiet([具体、可核实、可讨论。它决定你是否需要修正自己或澄清现实。])
  ],
  [
    #label([BOUNDARIES], tone: secondary)
    #v(4mm)
    #quiet([不让模糊的人格定义替代真实行为，也不把自己拖入无休止的动机审判。])
  ],
  [
    #label([REPUTATION])
    #v(4mm)
    #quiet([长期、稳定、由持续行动构成。它不依赖一次解释，也不取决于所有人。])
  ],
)
#v(18mm)
#split-rule()
#v(9mm)
#pull([
  真正强大，不是永远不被误解；\ 而是在被误解时，仍不依赖贬低别人\ 来确认自己的价值。
], size: 18pt)
