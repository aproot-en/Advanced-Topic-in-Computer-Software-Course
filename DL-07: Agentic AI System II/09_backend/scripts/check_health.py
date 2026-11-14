# check_health.py — check that every service is running
# Run:  .venv\Scripts\python.exe 09_backend\scripts\check_health.py

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared"))

import service_client as svc   # noqa: E402

NAMES = {"api": "02 API / Backend", "agent": "03 Travel AI Agent", "eds": "04 External Data Services",
         "di": "05 Data Integration", "rks": "06 Risk & Knowledge", "dle": "07 Decision & LLM",
         "rf": "08 Recommendation & Feedback"}


async def main():
    results = await asyncio.gather(*(svc.is_up(k) for k in NAMES))
    for (key, name), ok in zip(NAMES.items(), results):
        print(f"  {'UP  ' if ok else 'DOWN'}  {name:32s} {svc.SERVICE_URLS[key]}")
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) else 1)
