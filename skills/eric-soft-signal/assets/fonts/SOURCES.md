# Font Sources

These bundled fonts are used for premium Chinese cover titles and section anchors. Body text should still use system PingFang/Hiragino.

| Font | Files | Source | License |
|---|---|---|---|
| Zhuque Fangsong | `ZhuqueFangsong-Regular.ttf` | https://github.com/TrionesType/zhuque | SIL Open Font License 1.1 |
| Noto Serif SC | `NotoSerifSC-Regular.otf`, `NotoSerifSC-Medium.otf`, `NotoSerifSC-SemiBold.otf` | https://github.com/notofonts/noto-cjk | SIL Open Font License 1.1 |

Compile PDFs with:

```bash
typst compile --font-path fonts source.typ output.pdf
```
