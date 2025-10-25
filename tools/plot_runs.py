#!/usr/bin/env python3
"""
tools/plot_runs.py

Create time-series plots per model and a combined political-compass scatter of latest runs.

Outputs PNG files into `data/plots/`.

Usage:
  python tools/plot_runs.py --summary data/summary/aggregates.csv --outdir data/plots
"""

import os
from datetime import datetime
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def parse_run_timestamp(run_id: str) -> datetime:
    # run_id format: run_YYYYmmddTHHMMSSZ_<uuid>
    try:
        core = run_id.split('_', 1)[1]
        ts = core.split('_', 1)[0]
        return datetime.strptime(ts, "%Y%m%dT%H%M%SZ")
    except Exception:
        return None


def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_timeseries(df: pd.DataFrame, outdir: str):
    ensure_outdir(outdir)
    # expand timestamps
    df['ts'] = df['run_id'].map(parse_run_timestamp)
    df = df.dropna(subset=['ts'])
    # convert numeric
    df['economic'] = pd.to_numeric(df['economic'], errors='coerce')
    df['social'] = pd.to_numeric(df['social'], errors='coerce')

    for model, g in df.groupby('model'):
        g_sorted = g.sort_values('ts')
        if g_sorted.empty:
            continue
        plt.figure(figsize=(10, 5))
        plt.plot(g_sorted['ts'], g_sorted['economic'], marker='o', label='Economic')
        plt.plot(g_sorted['ts'], g_sorted['social'], marker='o', label='Social')
        plt.xlabel('Timestamp')
        plt.ylabel('Normalized score')
        plt.title(f'Time series for {model}')
        plt.legend()
        plt.grid(alpha=0.25)
        fname = os.path.join(outdir, f"timeseries__{model}.png")
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()
        print('Wrote', fname)


def plot_compass_latest(df: pd.DataFrame, outdir: str, size=6):
    ensure_outdir(outdir)
    # pick latest run per model by timestamp
    df['ts'] = df['run_id'].map(parse_run_timestamp)
    df = df.dropna(subset=['ts'])
    df['economic'] = pd.to_numeric(df['economic'], errors='coerce')
    df['social'] = pd.to_numeric(df['social'], errors='coerce')

    latest = df.sort_values('ts').groupby('model').tail(1)
    if latest.empty:
        print('No runs with timestamps found; skipping compass plot')
        return

    plt.figure(figsize=(size, size))
    ax = plt.gca()
    # center cross
    ax.axhline(0, color='#888', linewidth=1)
    ax.axvline(0, color='#888', linewidth=1)
    # scatter points
    xs = latest['economic']
    ys = latest['social']
    labels = latest['model'] + '\n' + latest['run_id']
    sc = ax.scatter(xs, ys, s=100, c='tab:blue', alpha=0.8)
    for i, txt in enumerate(labels):
        ax.annotate(txt, (xs.iloc[i], ys.iloc[i]), xytext=(5, 5), textcoords='offset points', fontsize=8)

    ax.set_xlim(df['economic'].min() - 1, df['economic'].max() + 1)
    ax.set_ylim(df['social'].min() - 1, df['social'].max() + 1)
    ax.set_xlabel('Economic')
    ax.set_ylabel('Social')
    ax.set_title('Latest model positions (economic vs social)')
    plt.grid(alpha=0.2)
    fname = os.path.join(outdir, 'compass_latest.png')
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    print('Wrote', fname)


def main(summary: str, outdir: str):
    if not os.path.exists(summary):
        print('Summary file not found:', summary)
        return
    df = pd.read_csv(summary)
    plot_timeseries(df, outdir)
    plot_compass_latest(df, outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', default='data/summary/aggregates.csv')
    parser.add_argument('--outdir', default='data/plots')
    args = parser.parse_args()
    main(args.summary, args.outdir)
