#!/usr/bin/env python3
import csv
import os

# CSV 파일 읽기 테스트
csv_path = 'agents_new/google_map_mcp/matched_store_results.csv'
print(f"CSV 파일 경로: {csv_path}")
print(f"파일 존재: {os.path.exists(csv_path)}")

if os.path.exists(csv_path):
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            print("첫 번째 행:")
            for key, value in first_row.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"CSV 읽기 오류: {e}")
else:
    print("CSV 파일을 찾을 수 없습니다.")
