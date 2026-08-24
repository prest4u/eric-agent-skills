# Font Sources

Bundled fonts cover Chinese display titles and section anchors. English-only cover titles use Typst’s shipped **Libertinus Serif** (`soft-latin-title-font`); do not put that face on Chinese covers, `soft-section` titles, or body text. Chinese cover titles and `soft-section` titles stay Zhuque Fangsong. Body text should still use system PingFang/Hiragino.

If a machine cannot resolve Libertinus Serif, add an OFL Libertinus Serif file here and list it in the table below. Typst `--font-path` adds paths and still sees the engine’s default faces.

| Font | Files | Source | License |
|---|---|---|---|
| Zhuque Fangsong | `ZhuqueFangsong-Regular.ttf` | https://github.com/TrionesType/zhuque | SIL Open Font License 1.1 |
| Noto Serif SC | `NotoSerifSC-Regular.otf`, `NotoSerifSC-Medium.otf`, `NotoSerifSC-SemiBold.otf` | https://github.com/notofonts/noto-cjk | SIL Open Font License 1.1 |
| Libertinus Serif | Typst default (not bundled) | https://github.com/alerque/libertinus | SIL Open Font License 1.1 |

Compile PDFs with:

```bash
typst compile --font-path fonts source.typ output.pdf
```
