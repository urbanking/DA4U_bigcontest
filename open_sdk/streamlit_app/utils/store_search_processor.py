"""
매장 검색 프로세서 - MCP Google Maps를 이용한 매장 정보 수집
"""

import os
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Google Maps Agent import (절대 경로 사용)
from agents_new.google_map_mcp import GoogleMapsAgent


class StoreSearchProcessor:
    """
    특정 매장 코드에 대한 정보를 MCP로 검색하고 
    결과를 txt 파일로 저장하는 프로세서
    """
    
    def __init__(self, csv_path: str, output_dir: str = None):
        """
        Args:
            csv_path: matched_store_results.csv 파일 경로
            output_dir: 출력 디렉토리 (기본값: open_sdk/output/store_mcp_searches)
        """
        self.csv_path = Path(csv_path)
        
        if output_dir is None:
            # 기본 출력 디렉토리 설정
            self.output_dir = Path(__file__).parent.parent.parent / "output" / "store_mcp_searches"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Google Maps Agent는 필요할 때 초기화 (lazy loading)
        self._agent = None
    
    @property
    def agent(self):
        """Google Maps Agent lazy loading"""
        if self._agent is None:
            try:
                self._agent = GoogleMapsAgent()
                print("✅ Google Maps Agent 초기화 완료")
            except Exception as e:
                print(f"❌ Google Maps Agent 초기화 실패: {e}")
                self._agent = None
        return self._agent
    
    def get_store_by_code(self, store_code: str) -> Dict[str, str]:
        """
        CSV 파일에서 특정 매장 코드의 정보 조회
        
        Args:
            store_code: 조회할 매장 코드
            
        Returns:
            매장 정보 딕셔너리 (없으면 None)
        """
        try:
            print(f"📂 CSV 파일 경로: {self.csv_path}")
            print(f"🔍 검색할 매장 코드: '{store_code}' (길이: {len(store_code)})")
            
            # UTF-8 BOM 처리
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # 첫 번째 행 확인 (디버깅)
                first_row = None
                row_count = 0
                
                for row in reader:
                    row_count += 1
                    if first_row is None:
                        first_row = row
                        print(f"📋 CSV 첫 번째 행 코드: '{row.get('코드', 'N/A')}' (길이: {len(row.get('코드', ''))})")
                        print(f"📋 CSV 컬럼: {list(row.keys())[:5]}")
                    
                    csv_code = row.get("코드", "").strip()
                    if csv_code == store_code.strip():
                        print(f"✅ 매칭 성공! 행 번호: {row_count}")
                        # 매칭_상호명 (실제 마스킹 해제된 이름) 사용
                        actual_name = row.get("매칭_상호명", "").strip()
                        masked_name = row.get("입력_가맹점명", "").strip()
                        print(f"📍 실제 상호명: '{actual_name}' (마스킹: '{masked_name}')")
                        return {
                            "코드": row.get("코드", ""),
                            "주소": row.get("입력_주소", ""),
                            "매장명": actual_name,  # 매칭_상호명 사용 (마스킹 해제된 실제 이름)
                            "매칭_상호명": actual_name,
                            "매칭_주소": row.get("매칭_주소", ""),
                            "lat": row.get("lat", ""),
                            "lng": row.get("lng", ""),
                        }
            
            print(f"⚠️ 매장 코드 {store_code}를 찾을 수 없습니다 (전체 {row_count}행 검색)")
            return None
            
        except Exception as e:
            print(f"❌ CSV 로딩 실패: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def search_store(self, store_info: Dict[str, str]) -> Dict[str, Any]:
        """
        단일 매장 검색
        
        Args:
            store_info: 매장 정보 딕셔너리
            
        Returns:
            검색 결과 딕셔너리
        """
        if not self.agent:
            return {
                "success": False,
                "error": "Google Maps Agent가 초기화되지 않았습니다"
            }
        
        try:
            # 검색 쿼리 생성
            # 1차: 매칭된 상호명과 주소로 검색
            if store_info.get("매칭_상호명") and store_info.get("매칭_주소"):
                query = f"{store_info['매칭_상호명']} {store_info['매칭_주소']}"
            # 2차: 입력 매장명과 주소로 검색
            elif store_info.get("매장명") and store_info.get("주소"):
                query = f"{store_info['매장명']} {store_info['주소']}"
            # 3차: 주소만으로 검색
            elif store_info.get("주소"):
                query = store_info["주소"]
            else:
                return {
                    "success": False,
                    "error": "검색 가능한 정보가 없습니다"
                }
            
            # Google Maps 검색 실행
            print(f"🔍 검색 중: {query}")
            result = self.agent.search_place(query)
            
            return {
                "success": True,
                "query": query,
                "result": result,
                "store_code": store_info.get("코드", ""),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "store_code": store_info.get("코드", "")
            }
    
    def save_search_result(self, result: Dict[str, Any], store_code: str) -> str:
        """
        검색 결과를 txt 파일로 저장
        
        Args:
            result: 검색 결과
            store_code: 매장 코드
            
        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{store_code}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"매장 코드: {result.get('store_code', 'N/A')}\n")
                f.write(f"검색 쿼리: {result.get('query', 'N/A')}\n")
                f.write(f"검색 시간: {result.get('timestamp', 'N/A')}\n")
                f.write("=" * 80 + "\n\n")
                
                if result.get("success"):
                    f.write("✅ 검색 성공\n\n")
                    f.write("검색 결과:\n")
                    f.write("-" * 80 + "\n")
                    f.write(result.get("result", "결과 없음"))
                    f.write("\n" + "-" * 80 + "\n")
                else:
                    f.write("❌ 검색 실패\n\n")
                    f.write(f"오류: {result.get('error', '알 수 없는 오류')}\n")
            
            print(f"✅ 저장 완료: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return ""
    
    def search_and_save_store(self, store_code: str) -> Dict[str, Any]:
        """
        특정 매장 코드에 대해 검색하고 결과 저장
        
        Args:
            store_code: 검색할 매장 코드
            
        Returns:
            검색 결과 딕셔너리
        """
        print(f"\n{'=' * 80}")
        print(f"🔍 매장 검색 시작: {store_code}")
        print(f"{'=' * 80}")
        
        # CSV에서 매장 정보 조회
        store_info = self.get_store_by_code(store_code)
        
        if not store_info:
            return {
                "success": False,
                "error": f"매장 코드 {store_code}를 CSV에서 찾을 수 없습니다",
                "store_code": store_code
            }
        
        print(f"✅ CSV에서 매장 정보 로드 완료: {store_info.get('매장명', 'N/A')}")
        
        # 매장 검색
        search_result = self.search_store(store_info)
        
        # 결과 저장
        if search_result.get("success"):
            filepath = self.save_search_result(search_result, store_code)
            print(f"✅ 검색 및 저장 완료: {filepath}")
            return {
                "success": True,
                "store_code": store_code,
                "file": filepath,
                "result": search_result.get("result")
            }
        else:
            error_msg = search_result.get("error", "알 수 없는 오류")
            print(f"❌ 검색 실패: {error_msg}")
            return {
                "success": False,
                "store_code": store_code,
                "error": error_msg
            }


def main():
    """
    테스트 실행
    """
    # CSV 파일 경로
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "matched_store_results.csv"
    
    # 프로세서 생성
    processor = StoreSearchProcessor(csv_path=str(csv_path))
    
    # 테스트: 특정 매장 코드 검색
    test_store_code = "000F03E44A"  # 육육면관
    
    result = processor.search_and_save_store(test_store_code)
    
    print("\n✅ 테스트 완료!")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
