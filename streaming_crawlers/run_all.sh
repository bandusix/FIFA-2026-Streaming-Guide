#!/bin/bash
cd "$(dirname "$0")"

echo "Running live streaming aggregator crawler..."
python3 live_streaming_crawler.py

echo "Running official streaming crawler..."
python3 official_streaming_crawler.py

echo "Done."