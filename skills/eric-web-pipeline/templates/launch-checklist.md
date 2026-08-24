# Launch Checklist · 上线前总检查表（Step 9 用）

> 部署前逐项打勾；不适用项标 N/A 并写一句原因。本表是 Step 8 详细 QA 的"最后一遍浓缩版"——Step 8 的证据不能替代本表。

## 冻结与授权

- [ ] 发布候选已冻结（commit/产物确定），发布授权已获用户确认
- [ ] 需要的独立 review 已完成（正式交付/安全相关/大改 UI 时）
- [ ] 回滚方法已写明，上一稳定版本标识已记录

## 功能

- [ ] 主流程在生产构建上端到端走通（本地 preview 或 staging）
- [ ] 三态（loading/empty/error）实测正常
- [ ] 控制台零 error
- [ ] （Path B）认证、鉴权、支付 webhook 生产配置复核（非测试 key！）

## 视觉与兼容

- [ ] 375 / 768 / 1440 / 1920 四断点截图复查无破版
- [ ] hover/focus 状态、暗色模式（如有）抽查
- [ ] 动效有 reduced-motion 回退

## 性能

- [ ] Lighthouse 移动档：Performance ≥ 90；LCP ≤ 2.5s / INP ≤ 200ms / CLS ≤ 0.1
- [ ] 图片压缩与尺寸正确，首屏图非 lazy，其余 lazy
- [ ] 第三方脚本精简，无未使用的大依赖

## SEO 与元信息

- [ ] 每页唯一 title/description，og/twitter 卡片实测预览
- [ ] sitemap.xml、robots.txt、favicon、404 页面
- [ ] canonical 与结构化数据（如适用）

## 安全

- [ ] 无硬编码密钥；`.env` 不在版本库；生产密钥走平台环境变量
- [ ] `npm audit` 无高危
- [ ] （Path B）`security-review` 清单已过；HTTPS 强制跳转

## 部署与监控

- [ ] 生产环境变量就位且未泄漏进前端 bundle
- [ ] 域名、DNS、HTTPS 证书就绪；www/apex 跳转策略明确
- [ ] （Path B）数据库迁移已按"先迁移后切流"执行
- [ ] 分析工具与错误监控已接，事件实测上报
- [ ] 上线后 read-back 计划已排（生产 URL 实测主流程 + 截图）
