#!/usr/bin/env python3
"""
tools/run_on_site.py

Playwright-based script to extract statements from a web page and call the local
`/api/take_test` endpoint. Does NOT auto-submit answers to the remote site; it
only extracts and runs the exam locally.

Usage:
  python tools/run_on_site.py <url> <statement_css_selector> [--api-url URL] [--api-key KEY]

Example:
  python tools/run_on_site.py "https://example.com/test" ".question-text" --api-url http://127.0.0.1:8000/api/take_test

Notes:
- Install requirements: pip install -r backend/requirements.txt
- After installing playwright package run: playwright install
- Be sure you have permission to extract from the target site before running.
"""

import sys
import argparse
import json
import requests
from playwright.sync_api import sync_playwright


def extract_statements_from_page(page, selector):
    elems = page.query_selector_all(selector)
    statements = []
    for el in elems:
        text = el.inner_text().strip()
        if text:
            statements.append(text)
    return statements


def run(url, selector, api_url, api_key=None, headless=True, wait_for="networkidle"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        # wait for network to be quiet / page to load
        try:
            page.wait_for_load_state(wait_for, timeout=10000)
        except Exception:
            # continue anyway; some pages don't reach networkidle
            pass

        statements = extract_statements_from_page(page, selector)
        if not statements:
            print("No statements found with selector:", selector)
            browser.close()
            return None

        print(f"Extracted {len(statements)} statements from page")
        for i, s in enumerate(statements[:10], start=1):
            print(f"{i}. {s[:140]}{'...' if len(s)>140 else ''}")

        payload = {
            "statements": statements
        }
        if api_key:
            payload["api_key"] = api_key

        print("Calling API:", api_url)
        resp = requests.post(api_url, json=payload, timeout=120)
        try:
            resp.raise_for_status()
        except Exception as e:
            print("API call failed:", e)
            print(resp.text)
            browser.close()
            return None

        data = resp.json()
        print(json.dumps(data, indent=2))

        browser.close()
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract statements and run the local take_test API")
    parser.add_argument("url", help="URL of the page containing the test")
    parser.add_argument("selector", help="CSS selector that matches statement text elements")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/take_test", help="Local API URL")
    parser.add_argument("--api-key", default=None, help="OpenAI API key to pass through to backend (optional)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (default true)")
    args = parser.parse_args()

    # default headless True unless --headless flag is provided (keeps compatibility with boolean flag)
    headless = True
    if args.headless is False:
        headless = False

    run(args.url, args.selector, args.api_url, api_key=args.api_key, headless=headless)
