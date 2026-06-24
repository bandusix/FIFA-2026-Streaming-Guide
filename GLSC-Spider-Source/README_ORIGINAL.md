# FIFA World Cup 2026 Streaming Scraper (fifa2026_multi_v1)

**source_lang**: multi (Global multi-language)
**source_region**: global
**version**: v1

## ⚽️ Project Overview (项目介绍)
This project is a specialized, highly concurrent streaming media crawler architecture designed for the **FIFA World Cup 2026**. It aggregates live broadcasting URLs, match replays, and official streaming sources across various global third-party and official platforms.

Built upon the **GMCA (Global Media Crawler Architect)** standard, it guarantees data consistency, scalability, and anti-ban resilience for collecting multimedia resources.

## 🚀 Core Capabilities (核心能力)
1. **Multi-Source Aggregation (多源聚合)**
   - **Official Streams**: Crawls official broadcasters per country (e.g., FOX, Telemundo, BBC, ITV, CCTV).
   - **PPV & Subscription**: Captures Pay-Per-View channels and subscription-based OTT platforms.
   - **Third-Party & Live Aggregators**: Scrapes real-time m3u8/iframe streaming links from Footreplays, Livsports, and other live sports hubs.
2. **GMCA-Compliant Architecture (遵循 GMCA 架构)**
   - Strict `play_url` validation (HTML pages only, no direct `.m3u8` or `.mp4` file extensions stored as `play_url`).
   - Unified flat-table output (`media_web_detail` & `media_web_episode`) compatible with MongoDB and SQLite.
   - Dual-channel logging: Unicode-rich CLI cards for humans and `.jsonl` for machines.
3. **Resilience & Proxy Rotation (高可用与代理轮询)**
   - Built-in `StealthyFetcher` with automatic proxy parsing and rotation (`--proxy-file`).
   - Adaptive concurrency control: automatically sheds workers if throttling (HTTP 429 / 5xx) is detected.
4. **Incremental Crawling (增量与断点续爬)**
   - Supports `--mode full` and `--mode incremental`.
   - Independent episode-level and detail-level resume logic.

## 📂 Directory Structure (目录结构)
```text
FIFA-World-Cup-2026-scraper/
├── README.md                           # This file
├── SKILL.md                            # GMCA specification & architecture notes
├── config/sites/                       # Site-specific configurations
├── fifa2026_multi/                     # Core Python package (No version suffix in import path)
│   ├── cli.py                          # Command Line Interface entry point
│   ├── spider.py                       # Core crawling logic & dispatcher
│   ├── live_streaming_crawler.py       # Aggregator for general live streams
│   ├── official_streaming_crawler.py   # Official broadcaster crawler
│   ├── footreplays_crawler.py          # Footreplays VOD/Replay crawler
│   ├── livsports_streaming_crawler.py  # Livsports crawler
│   └── ppv_streaming_crawler.py        # Pay-per-view crawler
├── core/                               # Reusable modules (fetcher, proxy, state)
├── utils/                              # Utilities (logger, exporter, validator)
├── proxies/                            # Proxy lists
├── logs/                               # JSONL & Text execution logs
└── output/                             # SQLite DB, Reconciliation reports & CSV/XLSX
```

## 💻 Usage (使用方法)

### 1. Installation (安装依赖)
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Crawler (启动爬虫)
Execute the crawler via the canonical CLI entry point:
```bash
# Full crawl across all configured sources
python3 -m fifa2026_multi.cli crawl --mode full --threads 5

# Incremental crawl (only fetch new/updated matches)
python3 -m fifa2026_multi.cli crawl --mode incremental --threads 3

# Use proxy file
python3 -m fifa2026_multi.cli crawl --mode full --proxy-file proxies/proxies.txt
```

### 3. Export Data (导出数据)
Export the crawled SQLite data into JSON Lines or XLSX format:
```bash
# Export to JSONL (MongoDB ready)
python3 -m fifa2026_multi.exporter jsonl --output-dir ./output

# Export to Excel
python3 -m fifa2026_multi.exporter xlsx --output-dir ./output
```

### 4. Check Status (查看状态)
```bash
python3 -m fifa2026_multi.cli status
```

## 📜 Development & Compliance
This project strictly follows the **v23 GMCA Doctrine**. Any new site adapter or feature must pass the mandatory `## Definition of Done` checks including log emission formatting, unique `play_url` constraint verification, and the superset catalog audit.
