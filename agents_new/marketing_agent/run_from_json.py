"""
Run Marketing Agent from a JSON input file.
- Loads agents_new/.env for GEMINI_API_KEY
- Accepts a store analysis JSON (Store Agent report or similar)
- Maps fields to expected store_analysis shape
- Calls run_marketing_sync_langchain and writes two JSON outputs
"""

import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env (relative)
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
print(f"[Runner] .env loaded from {ENV_PATH} | GEMINI_API_KEY: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")

# Import runner
try:
    from .marketing_langchain import run_marketing_sync_langchain
except ImportError:
    from marketing_langchain import run_marketing_sync_langchain


def to_store_analysis(data: dict) -> dict:
    """Map various report shapes to the expected store_analysis keys.
    Tolerant: fill what we can; leave others missing.
    """
    # Direct pass-through if already looks like expected format
    if any(k in data for k in ["store_name", "industry"]) and not data.get("store_overview"):
        return data

    store = data.get("store_overview", {})
    customer = data.get("customer_analysis", {})

    # Derive customer_demographics
    gender = "혼합"
    age = "혼합"
    gd = customer.get("gender_distribution", {})
    if gd:
        male = gd.get("male_ratio", 0)
        female = gd.get("female_ratio", 0)
        gender = "남성" if male >= female else "여성"
    ag = customer.get("age_group_distribution", {})
    if ag:
        age = max(ag.items(), key=lambda x: x[1])[0]

    # delivery_ratio (if available)
    delivery_ratio = None
    delivery = data.get("sales_analysis", {}).get("delivery_analysis", {})
    if isinstance(delivery.get("average"), (int, float)):
        delivery_ratio = delivery.get("average")

    return {
        "store_name": store.get("name") or data.get("store_name"),
        "industry": store.get("industry") or data.get("industry"),
        "commercial_zone": store.get("commercial_area") or data.get("commercial_zone"),
        "is_franchise": bool(store.get("brand") and store.get("brand") != "브랜드 없음"),
        "store_age": store.get("store_age") or data.get("store_age"),
        "customer_demographics": {
            "gender": gender,
            "age": age,
        },
        "customer_type": data.get("customer_type", "거주형"),
        "trends": data.get("trends", {}),
        "delivery_ratio": delivery_ratio if delivery_ratio is not None else data.get("delivery_ratio", "중간"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to input JSON file")
    ap.add_argument("--out", required=True, help="Output directory for result JSONs")
    ap.add_argument("--store-code", required=False, help="Store code (optional)")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    store_code = args.store_code
    if not store_code:
        # Try detect from report metadata or overview
        store_code = (
            data.get("report_metadata", {}).get("store_code")
            or data.get("store_overview", {}).get("code")
            or data.get("store_code")
            or "TEST"
        )

    store_analysis = to_store_analysis(data)

    # Run
    result = run_marketing_sync_langchain(store_code, str(out_dir), store_analysis)

    # Print summary
    print("[Runner] Done")
    print(json.dumps({
        "store_code": result.get("store_code"),
        "persona_type": result.get("persona_analysis", {}).get("persona_type"),
        "strategies": len(result.get("marketing_strategies", [])),
        "out_files": [p.name for p in out_dir.glob("marketing_*.json")],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
