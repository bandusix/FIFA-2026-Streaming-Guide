#!/bin/bash
cd "$(dirname "$0")"

echo "Running OFFICIAL streaming crawler (4-hour interval)..."
python3 official_streaming_crawler.py

echo "Done running official tasks."
