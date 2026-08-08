"""Small provider-neutral deployment smoke runner."""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def fetch(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"smoke request failed: {url}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-origin", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if "localhost" in args.api_origin or "127.0.0.1" in args.api_origin:
        raise SystemExit("deployed smoke must not use a localhost origin")
    health_status, health = fetch(args.api_origin.rstrip("/") + "/healthz")
    ready_status, ready = fetch(args.api_origin.rstrip("/") + "/readyz")
    if health_status != 200 or health.get("status") != "ok":
        raise SystemExit("healthz contract failed")
    if ready_status != 200 or ready.get("status") != "ready":
        raise SystemExit("readyz contract failed")
    result = {"healthz": health, "readyz": ready, "status": "passed"}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
