# Step 9 · 发布上线 — Ship: Review, Deploy & Rollback Readiness

> 中文速览：把验证过的成果安全地推出去——独立 review、部署、域名、监控、回滚预案。发布是**外部不可逆动作**（AGENTS.md 第 11 条）：必须确认授权与恢复路径，发布与签字权分离。

## When you're in this step · 判定信号

- Step 8 全部门通过，有完整 QA 证据；
- 用户说"上线""部署""发出去""push 到 GitHub"。

## Inputs · 进入条件

- QA 证据包（Step 8 产物）；
- 发布目标信息：平台账号、域名、环境变量（生产值）；
- **明确的发布授权**（用户说了要发，才算有）。

## Action checklist · 行动清单

1. **冻结候选**：确定发布对象的确切身份（commit hash / 构建产物目录），发布后不再改动——改了就重验；
2. **独立 review**（按 AGENTS.md 第 8 条，以下情形必须）：
   - [ ] 正式对外交付、涉安全/隐私/认证、破坏性操作、整屏/共享 UI 大改、用户明确要求签字；
   - [ ] 用一个全新的 reviewer 子 agent，只审冻结候选本身；一次review无结论最多换一个新 reviewer 再问一次，不无限循环；
3. **发布前清单**：跑 `templates/launch-checklist.md` 全表；
4. **部署**：
   - [ ] 生产环境变量就位（**绝不**把密钥写进代码或前端 bundle）；
   - [ ] 构建、部署、确认部署产物版本号/commit 与冻结候选一致；
   - [ ] 自定义域名与 HTTPS：DNS 记录、证书自动续期、www/apex 跳转策略；
5. **上线后验证（read-back）**：
   - [ ] 生产 URL 真实访问：主流程、控制台、各断点抽查、Lighthouse 复跑；
   - [ ] og 卡片/分享预览实测；表单/支付在生产模式各跑一次真实闭环（支付用小额真实单或测试模式）；
6. **监控与分析**：
   - [ ] 分析工具（Vercel Analytics / Plausible / GA）已接且事件正确；
   - [ ] 错误监控（Sentry 等，Path B 建议）；uptime 监控（对外服务）；
7. **回滚预案**：明确写出回滚方法（平台一键回滚到上一部署 / git revert + 重新部署），并确认上一稳定版本标识；
8. 更新 progress 文件：Step 9 完成，记录生产 URL、部署版本、回滚方法。

## Decision tables · 决策表

| 项目类型 | 推荐平台 | 备注 |
| --- | --- | --- |
| 静态站（Path A） | GitHub Pages / Cloudflare Pages / Vercel | 路由 `publish-project-to-github` |
| Next.js / 全栈（Path B） | Vercel / 自托管 + Docker | 数据库迁移随发布流程走，先迁后切 |
| 国内访问优先 | 国内对象存储 + CDN / 自有服务器 | ICP 备案是前置条件，Step 1 就该确认 |
| 重资产 Path C | CDN 缓存策略必须配好 | 模型/纹理走 immutable 缓存 |

## Exit criteria · 出口质量门

- [ ] 需要的独立 review 已完成且有结论；
- [ ] 生产环境 read-back 验证通过（有截图/记录）；
- [ ] 回滚方法已写明并确认可用；
- [ ] 监控/分析在线；
- [ ] progress 文件记录生产 URL 与版本。

## Common pitfalls · 常见坑

- **发完才发现环境变量没配**：生产白屏——read-back 是硬步骤，不能省；
- **数据库迁移顺序错**：新代码先上、旧表结构不兼容——先迁移兼容再切流量；
- **DNS 缓存幻觉**：自己电脑能开就宣布上线——用无缓存/手机网络复核；
- **无回滚方案**：出了问题现场想办法——回滚预案必须在发布前写好。

## Route to existing skills · 路由

- `publish-project-to-github` — GitHub 仓库打包 + Pages 发布 + 验证；
- `adaptive-quality-loop`（RELEASE 模式）— 授权/冻结/独立 review 的完整纪律；
- `ship-web-games` — 游戏类项目的打包发布。

## Output artifacts · 产出物

- 生产 URL + 部署版本记录 + 回滚预案（progress 文件 Step 9 勾选）。

## Handoff · 衔接

- 上线成功 → **Step 10 Iterate**；
- 上线后出事故 → 先回滚止血，再回 Step 5/8 定位修复，修完重走 Step 8→9。
