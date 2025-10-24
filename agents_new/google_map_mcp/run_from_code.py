"""
CLI to run Google Maps MCP lookup by store code using LangChain.

Usage (Windows cmd):
  python agents_new\google_map_mcp\run_from_code.py --code 1F4203EA83 \
         --csv agents_new\google_map_mcp\matched_store_results.csv \
         --out open_sdk\output\gm_lookup_1F4203EA83

Options:
  --dry-run   Perform only CSV lookup without invoking MCP (useful for quick validation)
  --force     Overwrite existing output JSON
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from .lookup_runner import run_lookup_from_code, DEFAULT_CSV_RELATIVE


def main(argv=None):
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run Google Maps MCP lookup by code")
    parser.add_argument("--code", required=True, help="상권 코드 (CSV의 '코드' 값)")
    parser.add_argument("--csv", default=DEFAULT_CSV_RELATIVE, help="CSV 경로 (기본: 패키지 내 matched_store_results.csv)")
    parser.add_argument("--out", default=os.getcwd(), help="출력 디렉토리 (기본: 현재 디렉토리)")
    parser.add_argument("--dry-run", action="store_true", help="CSV 조회만 수행 (MCP 호출 없음)")
    parser.add_argument("--force", action="store_true", help="동일 파일이 있어도 덮어쓰기")

    args = parser.parse_args(argv)

    result = run_lookup_from_code(
        code=args.code,
        csv_path=args.csv,
        out_dir=args.out,
        force=args.force,
        dry_run=args.dry_run,
    )

    print("\n=== Google Maps MCP Lookup Result ===")
    print(f"code: {result.get('code')}")
    print(f"input_store_name: {result.get('input_store_name')}")
    print(f"matched_store_name: {result.get('matched_store_name')}")
    print(f"place_id: {result.get('place_id')}")
    print(f"search_query: {result.get('search_query')}")
    print(f"output_path: {result.get('output_path')}")
    if args.dry_run:
        print("(dry-run) MCP 호출을 생략했습니다.")


if __name__ == "__main__":
    sys.exit(main())
