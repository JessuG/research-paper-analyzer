#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request


BASE_URL = "https://api.openai.com/v1/organization"


def build_url(path: str, params: dict[str, str]) -> str:
    return f"{BASE_URL}{path}?{urllib.parse.urlencode(params, doseq=True)}"


def get_json(url: str, api_key: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def flatten_usage_buckets(payload: dict) -> list[dict]:
    rows: list[dict] = []
    for bucket in payload.get("data", []):
        start_time = bucket.get("start_time")
        end_time = bucket.get("end_time")
        for result in bucket.get("results", []):
            rows.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "model": result.get("model"),
                    "api_key_id": result.get("api_key_id"),
                    "project_id": result.get("project_id"),
                    "num_model_requests": result.get("num_model_requests", 0),
                    "input_tokens": result.get("input_tokens", 0),
                    "output_tokens": result.get("output_tokens", 0),
                    "input_cached_tokens": result.get("input_cached_tokens", 0),
                }
            )
    return rows


def flatten_cost_buckets(payload: dict) -> list[dict]:
    rows: list[dict] = []
    for bucket in payload.get("data", []):
        start_time = bucket.get("start_time")
        end_time = bucket.get("end_time")
        for result in bucket.get("results", []):
            amount = result.get("amount", {})
            rows.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "project_id": result.get("project_id"),
                    "line_item": result.get("line_item"),
                    "currency": amount.get("currency"),
                    "amount": amount.get("value", 0),
                }
            )
    return rows


def print_usage(rows: list[dict]) -> None:
    print("USAGE")
    print("-" * 80)
    total_requests = 0
    total_input = 0
    total_output = 0
    for row in rows:
        total_requests += row["num_model_requests"]
        total_input += row["input_tokens"]
        total_output += row["output_tokens"]
        print(
            f"{time.strftime('%Y-%m-%d', time.gmtime(row['start_time']))} | "
            f"model={row['model'] or 'unknown'} | "
            f"requests={row['num_model_requests']} | "
            f"input={row['input_tokens']} | "
            f"output={row['output_tokens']} | "
            f"cached={row['input_cached_tokens']}"
        )
    print("-" * 80)
    print(f"Total requests: {total_requests}")
    print(f"Total input tokens: {total_input}")
    print(f"Total output tokens: {total_output}")
    print()


def print_costs(rows: list[dict]) -> None:
    print("COSTS")
    print("-" * 80)
    total_cost = 0.0
    currency = "usd"
    for row in rows:
        total_cost += row["amount"]
        currency = row["currency"] or currency
        print(
            f"{time.strftime('%Y-%m-%d', time.gmtime(row['start_time']))} | "
            f"line_item={row['line_item'] or 'unknown'} | "
            f"amount={row['amount']:.6f} {currency}"
        )
    print("-" * 80)
    print(f"Total cost: {total_cost:.6f} {currency}")


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    end_time = int(time.time())
    start_time = end_time - (days * 24 * 60 * 60)

    usage_url = build_url(
        "/usage/completions",
        {
            "start_time": str(start_time),
            "end_time": str(end_time),
            "bucket_width": "1d",
            "limit": str(days),
            "group_by": ["model", "api_key_id", "project_id"],
        },
    )
    costs_url = build_url(
        "/costs",
        {
            "start_time": str(start_time),
            "end_time": str(end_time),
            "bucket_width": "1d",
            "limit": str(days),
            "group_by": ["line_item", "project_id"],
        },
    )

    try:
        usage_payload = get_json(usage_url, api_key)
        costs_payload = get_json(costs_url, api_key)
    except Exception as exc:
        print(f"Failed to fetch OpenAI usage data: {exc}", file=sys.stderr)
        return 1

    print_usage(flatten_usage_buckets(usage_payload))
    print_costs(flatten_cost_buckets(costs_payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
