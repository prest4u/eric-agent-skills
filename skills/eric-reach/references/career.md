# 职场招聘

LinkedIn。

## LinkedIn

```bash
# 获取个人资料
mcporter call 'linkedin-scraper.get_person_profile(linkedin_url: "https://linkedin.com/in/username")'

# 搜索人才
mcporter call 'linkedin-scraper.search_people(keyword: "AI engineer", limit: 10)'

# 获取公司资料
mcporter call 'linkedin-scraper.get_company_profile(linkedin_url: "https://linkedin.com/company/xxx")'

# 搜索职位
mcporter call 'linkedin-scraper.search_jobs(keyword: "software engineer", limit: 10)'
```

Use this route only when doctor reports an already-active read backend; reuse
the current task's unchanged backend result. Fetch only the requested public
fields, and search only when the exact target is unknown. If the
read is blocked by login or setup state, stop and request separate authority;
do not initiate login, credential, browser-profile, or installation changes.

### Fallback 方案

只有目标是真正公开、无凭证参数的页面，且 MCP 缺失或出现非访问控制类故障时，才可用现有网页读者。登录、限流或安全拦截后不得换 Reader 绕过。公开页面的 Jina 示例：

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```
