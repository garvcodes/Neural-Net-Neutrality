#!/usr/bin/env python3
"""
tools/backup.py

Create timestamped backups of critical data.
Suitable for scheduling via cron or systemd timer.

Usage:
  python -m tools.backup
  python -m tools.backup --backup-dir /backups/neural-net-neutrality
  python -m tools.backup --compress  # Create tar.gz instead of directory
"""

import os
import sys
import argparse
import shutil
import glob
from datetime import datetime
import json

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase_db import get_all_ratings

app = FastAPI()

# Enable CORS so frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ratings")
def fetch_ratings():
    """Return all model ratings as JSON."""
    try:
        ratings = get_all_ratings()
        return {"success": True, "data": ratings}
    except Exception as e:
        return {"success": False, "error": str(e)}



def backup_data(backup_dir='backups', compress=False, retention_days=None):
    """
    Create timestamped backup of critical data.
    
    Args:
        backup_dir: Where to store backups
        compress: If True, create tar.gz; if False, create directory
        retention_days: Auto-remove backups older than this many days
    """
    os.makedirs(backup_dir, exist_ok=True)
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if compress:
        backup_path = os.path.join(backup_dir, f'compass_backup_{ts}')
        os.makedirs(backup_path, exist_ok=True)
    else:
        backup_path = os.path.join(backup_dir, f'compass_backup_{ts}')
        os.makedirs(backup_path, exist_ok=True)
    
    files_backed_up = 0
    
    # Backup aggregates CSV
    src = 'data/summary/aggregates.csv'
    if os.path.exists(src):
        dst = os.path.join(backup_path, 'aggregates.csv')
        shutil.copy2(src, dst)
        print(f"✓ Backed up: {src}")
        files_backed_up += 1
    
    # Backup latest compass image
    src = 'data/plots/compass_latest.png'
    if os.path.exists(src):
        dst = os.path.join(backup_path, 'compass_latest.png')
        shutil.copy2(src, dst)
        print(f"✓ Backed up: {src}")
        files_backed_up += 1
    
    # Backup latest run metadata
    latest_meta = sorted(glob.glob('data/runs/*_meta_common.json'))
    if latest_meta:
        src = latest_meta[-1]
        dst = os.path.join(backup_path, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"✓ Backed up: {src}")
        files_backed_up += 1
    
    # Backup questions.json
    src = 'data/questions.json'
    if os.path.exists(src):
        dst = os.path.join(backup_path, 'questions.json')
        shutil.copy2(src, dst)
        print(f"✓ Backed up: {src}")
        files_backed_up += 1
    
    # Create manifest
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'files_count': files_backed_up,
        'backup_type': 'full'
    }
    with open(os.path.join(backup_path, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Compress if requested
    if compress:
        archive_path = f"{backup_path}.tar.gz"
        shutil.make_archive(backup_path, 'gztar', backup_dir, os.path.basename(backup_path))
        shutil.rmtree(backup_path)  # Remove directory after compression
        backup_path = archive_path
        print(f"✓ Compressed: {archive_path}")
    
    # Cleanup old backups if retention specified
    if retention_days:
        cleanup_old_backups(backup_dir, retention_days)
    
    print(f"\n✓ Backup created: {backup_path}")
    print(f"  Files: {files_backed_up}")
    print(f"  Timestamp: {ts}")
    
    return backup_path


def cleanup_old_backups(backup_dir, retention_days):
    """Remove backups older than retention_days."""
    cutoff = datetime.now().timestamp() - (retention_days * 86400)
    removed_count = 0
    
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.getmtime(item_path) < cutoff:
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"  Removed old backup: {item}")
                removed_count += 1
            except Exception as e:
                print(f"  Error removing {item}: {e}")
    
    if removed_count > 0:
        print(f"✓ Cleaned up {removed_count} old backup(s)")


def list_backups(backup_dir='backups'):
    """List all available backups."""
    if not os.path.exists(backup_dir):
        print("No backups found.")
        return
    
    backups = sorted([
        (f, os.path.getmtime(os.path.join(backup_dir, f)))
        for f in os.listdir(backup_dir)
        if f.startswith('compass_backup_')
    ], key=lambda x: x[1], reverse=True)
    
    if not backups:
        print("No backups found.")
        return
    
    print("Available backups:")
    for filename, mtime in backups:
        size = get_dir_size(os.path.join(backup_dir, filename))
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {filename} ({size}) - {mtime_str}")


def get_dir_size(path):
    """Get human-readable directory size."""
    if os.path.isfile(path):
        size = os.path.getsize(path)
    else:
        size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(path)
            for filename in filenames
        )
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description='Backup critical Neural Net Neutrality data.'
    )
    parser.add_argument('--backup-dir', default='backups',
                        help='Directory to store backups')
    parser.add_argument('--compress', action='store_true',
                        help='Compress backups as tar.gz')
    parser.add_argument('--retention-days', type=int, default=None,
                        help='Auto-remove backups older than this many days')
    parser.add_argument('--list', action='store_true',
                        help='List all available backups')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups(args.backup_dir)
        return 0
    
    backup_data(
        backup_dir=args.backup_dir,
        compress=args.compress,
        retention_days=args.retention_days
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
