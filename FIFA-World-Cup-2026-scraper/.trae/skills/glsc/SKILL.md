---
name: "glsc"
description: "Defines philosophy, specs, and categorization rules for live sports crawlers. Invoke when designing or writing sports streaming crawlers to ensure standard data association and 3-tier output."
---

# Global Live Sport Crawler (GLSC)

本 Skill 旨在规范体育直播赛事爬虫（Global Live Sport Crawler, 简称 GLSC）的代码逻辑哲学、设计原理与输出规范。它不包含具体的网站抓取代码，而是提供统一的数据关联、播放源分类和结构化导出标准。

## 1. 核心哲学与原理 (Philosophy & Principles)

- **数据驱动而非页面驱动**：爬虫的核心不在于简单提取网页上的链接，而在于将非结构化的播放源与结构化的赛程数据进行深度关联。
- **时间维度绝对化**：所有的比赛时间必须转化为标准的 `UTC` 时间，以此作为状态机（未开赛、直播中、已完赛）的唯一判定基准。
- **播放源状态分离**：必须根据时间线和关键字，将爬取到的播放 URL 严格划分生命周期，避免失效源或未来源对当前观看体验的干扰。

## 2. 关联赛程数据 (Schedule Data Association)

在抓取任何播放源之前，脚本必须首先加载或解析标准的赛程表（例如 `matches.js`），建立 `Match ID` 与实体赛事信息的映射。

**规范要求**：
- **解析映射**：脚本必须能自动解析包含所有赛事（如 104 场完整赛程表）的数据源。
- **球队名称还原**：将单纯的 `Match ID` 映射到具体的主客场球队名称（如 `Mexico` vs `South Africa`），或者后续淘汰赛的对阵组别。
- **时间标准化**：提取原始赛程表中的开赛时间，并强制转换为标准的 UTC 时间，确保全球跨时区比对的绝对准确性。

## 3. 三重维度分类 (Three-Dimensional Categorization)

必须根据每场比赛的 UTC 时间与当前运行时间的对比，以及播放源本身的文本描述（如是否包含 "Replay" 或 "回放" 等字眼），自动将所有播放源进行归类。输出时（如 Excel 导出）需将这些数据分配到三个独立的分类页签（Sheet）中：

1. **时间计划 (Scheduled)**
   - **定义**：收录未开赛的预定赛事直播源或预留位。
   - **判定逻辑**：`当前时间 < 比赛时间` 且非回放源。
2. **实时直播 (Live)**
   - **定义**：收录正在进行中的比赛直播源。
   - **判定逻辑**：`比赛时间 <= 当前时间 <= 比赛时间 + 3小时` 且非回放源。
3. **全场回放 (Replays)**
   - **定义**：收录已完赛赛事的完整比赛录像 URL 和回放源。
   - **判定逻辑**：`当前时间 > 比赛时间 + 3小时`，或播放源描述、源名称中明确包含 "Replay"、"录像"、"回放" 等关键字。

## 4. 输出数据规范 (Output Specification)

无论是输出到 JSON、数据库还是最终的 Excel 报表，每个分类页签下的每一条播放源记录都**必须包含以下完整的 8 个核心字段**：

1. `Match ID`：赛事的唯一标识符。
2. `Home Team`：主队全称或对阵位置。
3. `Away Team`：客队全称或对阵位置。
4. `Match Time (UTC)`：标准的 UTC 格式开赛时间（如 `YYYY-MM-DD HH:MM:SS UTC`）。
5. `Stream Type`：播放源类型（例如 `Official Broadcaster`, `Third-Party/Live/PPV` 等）。
6. `Source`：来源站点的名称或域名。
7. `Player URL`：最终可用于播放视频或加载播放器 iframe 的网页视频播放 URL。
8. `Description`：附加描述，如语言、清晰度或抓取时的源文本信息。
