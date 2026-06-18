#!/bin/bash
cd "$(dirname "$0")"

echo "Running live streaming aggregator crawler (Third-party sources)..."
python3 live_streaming_crawler.py

# We no longer run official_streaming_crawler.py here synchronously
# because we want to decouple their execution frequencies.
# official_streaming_crawler.py will be executed by a separate 4-hour cron job.

echo "Done running frequent tasks."