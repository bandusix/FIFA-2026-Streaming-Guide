import subprocess
import os
import sys

def main():
    # Change to project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    crawlers_dir = os.path.join(project_root, "streaming_crawlers")

    print("Running live streaming aggregator crawler...")
    try:
        subprocess.run(['python3', 'live_streaming_crawler.py'], cwd=crawlers_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running live_streaming_crawler.py: {e}")
        sys.exit(1)

    # Optionally run official crawler here if needed, but let's just stick to the live aggregator for now 
    # as per the cron task definition, or run both. Let's run run_all.sh which does both.
    # Actually, the user's previous cron specifically ran live_streaming_crawler.py.
    # Let's run official crawler too, since it updates official_streams.json.
    print("Running official streaming crawler...")
    try:
        subprocess.run(['python3', 'official_streaming_crawler.py'], cwd=crawlers_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running official_streaming_crawler.py: {e}")
        # Not exiting here so we can still commit streams.json if official fails

    # Check for changes in both streams.json and official_streams.json
    files_to_check = ['streams.json', 'official_streams.json']
    changed_files = []

    for file in files_to_check:
        diff = subprocess.run(['git', 'diff', file], capture_output=True, text=True).stdout
        if diff.strip():
            changed_files.append(file)

    if not changed_files:
        print("No changes in streaming URLs. Exiting.")
        sys.exit(0)

    print(f"Changes detected in {', '.join(changed_files)}. Committing to git...")
    
    try:
        subprocess.run(['git', 'add'] + changed_files, check=True)
        subprocess.run(['git', 'commit', '-m', 'chore: auto update streaming URLs'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Successfully updated and pushed streaming URLs.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
