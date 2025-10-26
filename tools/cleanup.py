#!/usr/bin/env python3
"""
tools/cleanup.py

Cleanup old run data and maintain retention policy.
Runs as part of post-run cleanup or separate cron job.

Usage:
  python -m tools.cleanup --keep-days 90
  python -m tools.cleanup --keep-days 30 --runs-dir /path/to/runs
"""

import os
import sys
import argparse
import glob
from datetime import datetime, timedelta
import json


def cleanup_old_runs(runs_dir='data/runs', keep_days=90):
    """Remove runs older than keep_days."""
    if not os.path.exists(runs_dir):
        print(f"Runs directory not found: {runs_dir}")
        return 0
    
    cutoff = datetime.now() - timedelta(days=keep_days)
    removed_count = 0
    
    # Find all run files
    for run_file in sorted(glob.glob(f"{runs_dir}/run_*.csv")):
        try:
            # Extract timestamp from filename: run_20251025T234436Z_...
            filename = os.path.basename(run_file)
            ts_str = filename.split('__')[0].split('_')[1]
            run_date = datetime.strptime(ts_str, "%Y%m%dT%H%M%SZ")
            
            if run_date < cutoff:
                print(f"[REMOVE] {run_file} (age: {(datetime.now() - run_date).days} days)")
                os.remove(run_file)
                removed_count += 1
                
                # Also remove associated meta files
                base = run_file.rsplit('.', 1)[0]
                for suffix in ['_meta.json', '.json']:
                    meta_file = base + suffix
                    if os.path.exists(meta_file):
                        print(f"[REMOVE] {meta_file}")
                        os.remove(meta_file)
                        removed_count += 1
        except Exception as e:
            print(f"[ERROR] Processing {run_file}: {e}")
    
    print(f"\nCleanup complete: removed {removed_count} files")
    print(f"Retention policy: keep {keep_days} days (cutoff: {cutoff.isoformat()})")
    return removed_count


def cleanup_old_plots(plots_dir='data/plots', keep_days=90):
    """Remove old plot files."""
    if not os.path.exists(plots_dir):
        print(f"Plots directory not found: {plots_dir}")
        return 0
    
    cutoff = datetime.now() - timedelta(days=keep_days)
    removed_count = 0
    
    for plot_file in glob.glob(f"{plots_dir}/*.png"):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(plot_file))
            if mtime < cutoff:
                print(f"[REMOVE] {plot_file}")
                os.remove(plot_file)
                removed_count += 1
        except Exception as e:
            print(f"[ERROR] Processing {plot_file}: {e}")
    
    return removed_count


def get_storage_usage(base_dir='data'):
    """Calculate total storage used."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass
    
    # Format as human-readable
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total_size < 1024:
            return f"{total_size:.2f} {unit}"
        total_size /= 1024
    return f"{total_size:.2f} TB"


def main():
    parser = argparse.ArgumentParser(
        description='Cleanup old run and plot data based on retention policy.'
    )
    parser.add_argument('--keep-days', type=int, default=90,
                        help='Number of days to retain (default: 90)')
    parser.add_argument('--runs-dir', default='data/runs',
                        help='Directory containing run files')
    parser.add_argument('--plots-dir', default='data/plots',
                        help='Directory containing plot files')
    parser.add_argument('--storage-report', action='store_true',
                        help='Show storage usage report before cleanup')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deleted without deleting')
    
    args = parser.parse_args()
    
    if args.storage_report:
        print(f"Storage usage: {get_storage_usage()}\n")
    
    if args.dry_run:
        print("[DRY RUN - No files will be deleted]\n")
    
    # Cleanup runs
    print(f"Cleaning up runs older than {args.keep_days} days...")
    removed = cleanup_old_runs(args.runs_dir, args.keep_days)
    
    # Cleanup plots
    print(f"\nCleaning up plots older than {args.keep_days} days...")
    removed += cleanup_old_plots(args.plots_dir, args.keep_days)
    
    if args.storage_report:
        print(f"\nNew storage usage: {get_storage_usage()}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
