#import "/theme.typ": *
#import "facts.typ": *

#show: booklet-doc.with(
  title: "选科指导报告 · 林同",
  author: studio,
)

#cover-page(
  title: "选科指导报告",
  student: alias,
  meta: province + " · " + year + " · " + batch,
  opener: opener-line,
  colophon: case-id + "  ·  合成示例  ·  非正式官方文件 · 不保证录取  ·  " + doc-date + "  ·  " + version,
)

#page-frame[
  #rtl-cols((
    v-head("怎么读"),
    v-run("本文件把文字分成三类。栏从右起，字从上到下。"),
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.4mm,
        v-run("事实", size: 11pt, fill: muted),
        v-run(how-fact),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.4mm,
        v-run("判断", size: 11pt, fill: muted),
        v-run(how-judge),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.4mm,
        v-run("待核验", size: 11pt, fill: muted),
        v-run(how-unv),
      )
    ],
    v-run(pending, size: 9pt),
    v-head("档案"),
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.2mm,
        v-run("现行", size: 8pt, fill: muted),
        v-run(current-combo),
        v(2.2mm),
        v-run("备选", size: 8pt, fill: muted),
        v-run(alt-combo),
        v(2.2mm),
        v-run("第三路", size: 8pt, fill: muted),
        v-run(third-combo),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.2mm,
        v-run("硬约束", size: 8pt, fill: muted),
        v-run(hard),
        v(2.2mm),
        v-run("软偏好", size: 8pt, fill: muted),
        v-run(soft),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2.2mm,
        v-run("位次", size: 8pt, fill: muted),
        v-run(rank-note, size: 8.5pt),
        v(2.2mm),
        v-run("署名", size: 8pt, fill: muted),
        v-run("青云未来只署名青云未来。"),
      )
    ],
  ), gutter: 5.6mm)
]

#pagebreak()

#page-frame[
  #rtl-cols((
    v-head("科目与专业门"),
    v-run("只谈门是否被关上。合成口径，状态待核验。不开冲稳保，不上色。每种组合一竖栏。", size: 9pt),
    gate-columns(gate-rows),
    v-run(narrative-1, size: 9pt),
    v-run(narrative-2, size: 9pt),
    v-run(narrative-3, size: 9pt),
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run("不放进表", size: 8pt, fill: muted),
        v-run(exclude-rows.at(0).at(0) + exclude-rows.at(0).at(1), size: 8.5pt),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run("不是志愿", size: 8pt, fill: muted),
        v-run("本页没有院校网格。出分后再开志愿版档案。"),
      )
    ],
  ), gutter: 5.2mm)
]

#pagebreak()

#page-frame[
  #rtl-cols((
    v-head("来源与免责"),
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run(sources.at(0).at(0), size: 8pt, fill: muted),
        v-run(sources.at(0).at(1), size: 9pt),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run(sources.at(1).at(0), size: 8pt, fill: muted),
        v-run(sources.at(1).at(1), size: 9pt),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run(sources.at(2).at(0), size: 8pt, fill: muted),
        v-run(sources.at(2).at(1), size: 9pt),
      )
    ],
    v-run(disclaimer-lines.at(0)),
    v-run(disclaimer-lines.at(1)),
    v-run(disclaimer-lines.at(2)),
    v-run(disclaimer-lines.at(3)),
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run("含什么", size: 8pt, fill: muted),
        v-run(svc-in, size: 8.5pt),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run("不含什么", size: 8pt, fill: muted),
        v-run(svc-out, size: 8.5pt),
      )
    ],
    block(breakable: false)[
      #stack(dir: ttb, spacing: 2mm,
        v-run("下一步", size: 8pt, fill: muted),
        v-run("监护人确认硬约束仍是原意。对照当年选科要求。签发前须对照当年文件。家庭作最终决定。机构署名：青云未来。", size: 8.5pt),
      )
    ],
  ), gutter: 5.2mm)
]
