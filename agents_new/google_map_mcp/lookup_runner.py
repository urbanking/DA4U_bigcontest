"""
Lookup runner for Google Maps MCP using LangChain.

Given a store code (코드) from matched_store_results.csv, this runner:
- Finds the matching row (입력_주소, 입력_가맹점명, 매칭_상호명, place_id, ...)
- Builds a robust search query (매칭_상호명 + 입력_주소)
- Invokes GoogleMapsAgent (LangChain + MCP) to perform the search
- Saves a structured JSON output without creating temporary files

Assumptions:
- CSV header columns: 코드, 입력_주소, 입력_가맹점명, 매칭_상호명, place_id, ...
- Encoding is UTF-8 (BOM-safe); adjusts if needed.

Outputs:
- JSON file named `gm_search_result_{code}.json` under the specified output directory
  containing: code, input fields, search_query, agent_output (text), and metadata.

No absolute paths are used; defaults are relative to this file.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from .google_maps_agent import GoogleMapsAgent


DEFAULT_CSV_RELATIVE = os.path.join(os.path.dirname(__file__), "matched_store_results.csv")


@dataclass
class CsvMatch:
    code: str
    input_address: str
    input_store_name: str
    matched_store_name: str
    place_id: str
    row: Dict[str, Any]


def _read_csv_row_by_code(csv_path: str, code: str) -> Optional[CsvMatch]:
    """Return the CSV row for the given code, normalized to a CsvMatch, or None if not found."""
    # Try UTF-8 with BOM first, then fallback to cp949 for Windows-origin files
    encodings = ["utf-8-sig", "utf-8", "cp949"]
    last_err: Optional[Exception] = None
    for enc in encodings:
        try:
            with open(csv_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if str(row.get("코드", "")).strip() == str(code).strip():
                        return CsvMatch(
                            code=row.get("코드", "").strip(),
                            input_address=(row.get("입력_주소") or "").strip(),
                            input_store_name=(row.get("입력_가맹점명") or "").strip(),
                            matched_store_name=(row.get("매칭_상호명") or "").strip(),
                            place_id=(row.get("place_id") or "").strip(),
                            row=row,
                        )
            return None
        except Exception as e:  # keep fallback behavior
            last_err = e
            continue
    # If we exhausted encodings, raise last error for visibility
    if last_err:
        raise last_err
    return None


def _build_search_query(match: CsvMatch) -> str:
    name = match.matched_store_name or match.input_store_name
    addr = match.input_address
    parts = [p for p in [name, addr] if p]
    if not parts:
        return match.code
    return " ".join(parts)


def run_lookup_from_code(
    code: str,
    csv_path: Optional[str] = None,
    out_dir: Optional[str] = None,
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Run Google Maps MCP search for a given code.

    Args:
        code: 상권 코드 (CSV의 '코드' 컬럼 값)
        csv_path: CSV 경로 (기본값: matched_store_results.csv in this package)
        out_dir: 출력 디렉토리 (기본값: current working directory)
        force: 동일 파일이 있어도 덮어쓰기 여부
        dry_run: True이면 MCP 호출 없이 CSV 조회만 수행

    Returns:
        result dict with keys: code, input_address, input_store_name, matched_store_name,
        place_id, search_query, agent_output (text or None), csv_row (raw), output_path (if saved)
    """
    # Load environment (to ensure GEMINI_API_KEY and Google_Map_API_KEY are available)
    load_dotenv()

    csv_path = csv_path or DEFAULT_CSV_RELATIVE
    out_dir = out_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    match = _read_csv_row_by_code(csv_path, code)
    if not match:
        raise ValueError(f"코드 '{code}'를 CSV에서 찾을 수 없습니다. csv_path={csv_path}")

    search_query = _build_search_query(match)

    agent_output: Optional[str] = None
    if not dry_run:
        # Initialize agent and run search_place to ensure maps_search_places + maps_place_details flow
        agent = GoogleMapsAgent()
        agent_output = agent.search_place(search_query)

    result: Dict[str, Any] = {
        "code": match.code,
        "input_address": match.input_address,
        "input_store_name": match.input_store_name,
        "matched_store_name": match.matched_store_name,
        "place_id": match.place_id,
        "search_query": search_query,
        "agent_output": agent_output,
        "csv_row": match.row,
    }

    out_path = os.path.join(out_dir, f"gm_search_result_{match.code}.json")
    if force or not os.path.exists(out_path):
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["output_path"] = out_path
    else:
        result["output_path"] = out_path  # indicate existing file

    return result


__all__ = [
    "run_lookup_from_code",
]
