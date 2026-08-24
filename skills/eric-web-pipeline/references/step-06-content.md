# Step 6 · 内容与素材 — Copy, Media & Assets

> 中文速览：把占位内容全部换成真实内容——文案、图片、视频、图标、字体、3D 资源。内容质量直接决定网站的最终质感；再好的设计配上 Lorem ipsum 和裂图也是废品。

## When you're in this step · 判定信号

- 功能已通，但页面上还有占位文案、占位图、"TODO: 换图"；
- 用户发来真实文案/素材包，需要落位。

## Inputs · 进入条件

- MVP 主流程已通（Step 5 产物）；
- Step 2 的素材清单与来源策略。

## Action checklist · 行动清单

1. **文案**：
   - [ ] 逐页面落位真实文案：标题、副标、正文、CTA、表单提示、错误提示、空态文案；
   - [ ] 语气统一（与 brief 的受众一致）；多语言站点确定翻译流程与回退语言；
   - [ ] 法律文案（Path B 必须）：隐私政策、服务条款、Cookie 提示——占位也要有正式页面；
   - [ ] SEO 文案：每页 title、meta description、og:title/description。
2. **图片与视频**：
   - [ ] 按素材清单逐一落位，全部走本地/自己 CDN，**不热链第三方脆弱 URL**；
   - [ ] 尺寸与压缩：展示尺寸 ≤ 实际需要的 2 倍；照片 WebP/AVIF；视频 H.264/HLS，海报帧必备；
   - [ ] 每张图有明确 `width/height` 或 aspect-ratio（防 CLS），首屏以下 `loading="lazy"`；
   - [ ] alt 文本：信息图写描述，装饰图留空 `alt=""`。
3. **图标与字体**：
   - [ ] 图标统一一个风格体系（不混 outline 和 filled 两套）；
   - [ ] 字体子集化（中文务必），`font-display: swap`，系统字体 fallback 栈完整。
4. **Path C 资源**：模型减面/压缩（Draco/KTX2）、纹理图集、加载清单与总大小预算（移动端 < 10MB 级别）。
5. **版权自查**：每个外部素材记录来源与授权；字体授权覆盖使用场景（web/app/印刷）。
6. **fallback 兜底**：任何加载失败的素材都有兜底（占位色块/备用图），不出现裂图框。

## Decision tables · 决策表

| 素材缺口 | 处理 |
| --- | --- |
| 用户迟迟不给文案 | 用高质量的**主题相关草稿**（非 Lorem ipsum），标注待替换 |
| 图片找不到合适的 | 路由素材 skill 或 AI 生成；保持视觉方向一致 |
| 视频太大 | 压缩 + 海报帧 + 点击播放；背景视频 < 5MB 且静音循环 |
| 字体授权不明 | 换 Google Fonts 等价字体，不抱侥幸心理 |

## Exit criteria · 出口质量门

- [ ] 全站无 Lorem ipsum、无占位图、无裂图、无 "TODO 文案"；
- [ ] 所有图片有尺寸声明与 alt 策略；首屏图片非 lazy；
- [ ] 每页 SEO 三件套（title/description/og）已填；
- [ ] 素材来源与授权有记录；fallback 已验证（断网/慢网测试过一次）；
- [ ] 文案通读一遍：无错别字、无 AI 味套话（路由 `eric-teaching-polish` 或 `huashu-proofreading` 做去 AI 味审校）。

## Common pitfalls · 常见坑

- **文案挤爆布局**：真实标题比占位长三倍——内容落位后必须重查桌面与移动布局；
- **首屏性能被素材拖死**：hero 大图 4MB——压缩、正确尺寸、必要时 `fetchpriority="high"`；
- **装饰图乱写 alt**：屏幕阅读器被无意义 alt 轰炸；
- **多语言回退缺失**：翻译缺键时页面显示 `home.hero.title`。

## Route to existing skills · 路由

- `unsplash-asset-images` / `aura-asset-images` — 图片选取与 URL 规范；
- `company-logos` / `solar-duotone-bold` — logo 墙与图标体系；
- `huashu-proofreading` — 中文文案去 AI 味三遍审校；
- `elevenlabs-tts` — 需要配音/旁白时。

## Output artifacts · 产出物

- 全站真实内容落位；
- 素材来源/授权记录（可并入 progress 文件备注）。

## Handoff · 衔接

- 内容齐、布局复查通过 → **Step 7 Polish**；
- 内容落位暴露了结构性问题（如真实文案需要两栏而非一栏）→ 回 Step 5 调整对应组件。
