# FIFA 2026 Live Streaming Crawler

## 简介
这是一个针对多个第三方聚合直播源（如 Footybite, Buffstreams 等）的自动化爬虫程序。它会自动结合项目中的 `matches.js` 赛程时间表，仅提取 **今天（过去24小时及未来24小时内）** 的比赛，然后在各大聚合直播网站中进行页面分析，直接抓取带有真实网页播放器的比赛播放页 URL。

## 功能特性
1. **时间智能过滤**：自动读取 `matches.js` 并对比系统时间，自动跳过未来 >24 小时或过去 >24 小时的比赛。
2. **防爬虫绕过**：使用 `playwright` 的真实 Chromium 浏览器内核渲染，有效绕过 Cloudflare 5秒盾和 Nuxt.js 等单页应用 (SPA) 的动态加载限制。
3. **模糊匹配算法**：自动将 FIFA 的 ISO 3166 国家代码转换为对应的英文国名，并对获取到的页面所有 A 标签执行主客队交叉模糊匹配，精准定位赛事的专用播放页面。
4. **一键直达**：抓取到的 URL 是最终带有网页直播视频播放器的播放页，直接下发，可以直接被前端或其他系统调用。

## 支持爬取的聚合源
- `https://footybite.ac/fifa-world-cup`
- `https://olympicweb.me/live/2026-worldcup-stream`
- `https://buffstreams.plus/soccer-live-streams`
- `https://boxinginfo.info/#soccer`
- `https://mmafighter.info/`
- `https://www.vipboxtv.sk/live-now-stream` (备用源，需注意其可能存在的深层反爬跳转)
- `https://ppv.to/#34` (备用源，重度反爬)

## 依赖安装
由于聚合直播站多带有反爬机制，本项目采用 `playwright` 驱动真实浏览器渲染抓取：

```bash
# 安装 Python 依赖
pip install playwright

# 安装 Playwright 的 Chromium 浏览器内核
playwright install chromium
```

## 运行方式
```bash
python3 live_streaming_crawler.py
```

## 输出示例
程序会在终端实时打印抓取过程，并在结束时输出汇总的 JSON 或列表格式。例如：

```text
=== FINAL AGGREGATED LINKS ===

Match 13 | Saudi vs Uruguay
  [Source: https://footybite.ac/fifa-world-cup] https://footybite.ac/event/saudi-arabia-vs-uruguay
  [Source: https://olympicweb.me/live/2026-worldcup-stream] https://olympicweb.me/live-saudi-arabia-vs-uruguay-stream
  ...

Match 16 | Belgium vs Egypt
  [Source: https://footybite.ac/fifa-world-cup] https://footybite.ac/event/belgium-vs-egypt
  [Source: https://buffstreams.plus/soccer-live-streams] https://buffstreams.plus/world-championship-gr-g/egypt-belgium/1244797
  ...
```
