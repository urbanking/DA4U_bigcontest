"""
StoreAgent → NewProductAgent 통합 파이프라인
open_sdk/output의 StoreAgent 리포트를 자동으로 읽어서
화이트리스트 업종에 해당하면 신제품 제안 Agent 실행
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# New Product Agent는 Streamlit 앱에서만 실행
from agents_new.new_product_agent.planner.rules import ALLOWED_INDUSTRIES


class IntegratedPipeline:
    """StoreAgent 리포트 필터링 (New Product Agent는 Streamlit 앱에서 실행)"""
    
    def __init__(self, output_dir: str = "open_sdk/output"):
        """
        Args:
            output_dir: StoreAgent 출력 디렉토리
        """
        self.output_dir = Path(output_dir)
    
    def find_store_reports(self) -> List[Path]:
        """
        open_sdk/output에서 모든 StoreAgent 리포트 찾기
        
        Returns:
            store_analysis_report.json 파일 경로 리스트
        """
        pattern = "analysis_*/store_analysis_report.json"
        reports = list(self.output_dir.glob(pattern))
        
        # 중복 제거 (같은 매장코드의 최신 것만)
        unique_reports = {}
        for report_path in reports:
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    store_code = data.get('report_metadata', {}).get('store_code')
                    analysis_date = data.get('report_metadata', {}).get('analysis_date')
                    
                    if store_code:
                        # 같은 매장코드면 최신 것만 유지
                        if store_code not in unique_reports or \
                           analysis_date > unique_reports[store_code]['date']:
                            unique_reports[store_code] = {
                                'path': report_path,
                                'date': analysis_date
                            }
            except Exception as e:
                print(f"[WARN] Failed to read {report_path}: {e}")
                continue
        
        return [item['path'] for item in unique_reports.values()]
    
    def check_industry(self, report_path: Path) -> tuple[bool, str, Dict]:
        """
        리포트의 업종이 화이트리스트에 있는지 확인
        
        Args:
            report_path: 리포트 파일 경로
            
        Returns:
            (화이트리스트 포함 여부, 업종명, 리포트 데이터)
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            industry = report.get('store_overview', {}).get('industry', '')
            is_allowed = industry in ALLOWED_INDUSTRIES
            
            return is_allowed, industry, report
        except Exception as e:
            print(f"[ERROR] Failed to check industry for {report_path}: {e}")
            return False, "", {}
    
    async def process_single_report(self, report_path: Path) -> Dict[str, Any]:
        """
        단일 리포트 처리
        
        Args:
            report_path: 리포트 파일 경로
            
        Returns:
            처리 결과 (성공 여부, 매장 코드, 업종, 결과 등)
        """
        store_code = report_path.parent.name.replace('analysis_', '').split('_')[0]
        
        print(f"\n{'='*70}")
        print(f"[Processing] {store_code}")
        print(f"{'='*70}")
        
        # 업종 확인
        is_allowed, industry, report = self.check_industry(report_path)
        
        if not is_allowed:
            print(f"  ✗ 업종 '{industry}' - 화이트리스트에 없음 (SKIP)")
            return {
                "success": False,
                "store_code": store_code,
                "industry": industry,
                "reason": "Not in whitelist",
                "result": None
            }
        
        print(f"  ✓ 업종 '{industry}' - 화이트리스트 확인!")
        
        # New Product Agent는 Streamlit 앱에서만 실행
        print(f"  ℹ️ New Product Agent는 Streamlit 앱에서 실행됩니다.")
        return {
            "success": True,
            "store_code": store_code,
            "industry": industry,
            "activated": True,
            "reason": "Will be executed in Streamlit app",
            "result": None
        }
    
    async def run_all(self) -> Dict[str, Any]:
        """
        모든 StoreAgent 리포트 처리
        
        Returns:
            전체 처리 결과 요약
        """
        print("\n" + "="*70)
        print("StoreAgent 리포트 필터링 (New Product Agent는 Streamlit 앱에서 실행)")
        print("="*70)
        
        # 1) 모든 리포트 찾기
        print("\n[Step 1/3] StoreAgent 리포트 검색...")
        reports = self.find_store_reports()
        print(f"  ✓ 총 {len(reports)}개 리포트 발견")
        
        # 2) 화이트리스트 필터링
        print("\n[Step 2/3] 업종 필터링...")
        filtered = []
        for report_path in reports:
            is_allowed, industry, _ = self.check_industry(report_path)
            store_code = report_path.parent.name.replace('analysis_', '').split('_')[0]
            
            if is_allowed:
                print(f"  ✓ {store_code} - {industry}")
                filtered.append(report_path)
            else:
                print(f"  ✗ {store_code} - {industry} (SKIP)")
        
        print(f"\n  → 처리 대상: {len(filtered)}개 매장")
        
        if not filtered:
            print("\n⚠️  화이트리스트에 해당하는 매장이 없습니다.")
            return {
                "total_reports": len(reports),
                "filtered_count": 0,
                "processed": [],
                "summary": {
                    "success": 0,
                    "failed": 0,
                    "skipped": len(reports)
                }
            }
        
        # 3) 필터링 완료 (New Product Agent는 Streamlit 앱에서 실행)
        print("\n[Step 3/3] 필터링 완료...")
        print(f"  → 처리 대상: {len(filtered)}개 매장")
        print(f"  ℹ️ New Product Agent는 Streamlit 앱에서 실행됩니다.")
        
        # 4) 요약
        print("\n" + "="*70)
        print("처리 완료 - 요약")
        print("="*70)
        
        summary = {
            "filtered": len(filtered),
            "skipped": len(reports) - len(filtered),
            "total_reports": len(reports)
        }
        
        print(f"\n총 리포트: {len(reports)}개")
        print(f"  - 화이트리스트 해당: {len(filtered)}개")
        print(f"  - 스킵됨: {summary['skipped']}개")
        print(f"\nℹ️ New Product Agent는 Streamlit 앱에서 실행됩니다.")
        
        return {
            "total_reports": len(reports),
            "filtered_count": len(filtered),
            "summary": summary
        }
    
    async def run_specific_stores(self, store_codes: List[str]) -> Dict[str, Any]:
        """
        특정 매장 코드만 처리
        
        Args:
            store_codes: 처리할 매장 코드 리스트
            
        Returns:
            처리 결과
        """
        print("\n" + "="*70)
        print(f"특정 매장 처리: {', '.join(store_codes)}")
        print("="*70)
        
        reports = self.find_store_reports()
        filtered = []
        
        for report_path in reports:
            store_code = report_path.parent.name.replace('analysis_', '').split('_')[0]
            if store_code in store_codes:
                is_allowed, industry, _ = self.check_industry(report_path)
                if is_allowed:
                    filtered.append(report_path)
                    print(f"  ✓ {store_code} - {industry}")
                else:
                    print(f"  ✗ {store_code} - {industry} (Not in whitelist)")
        
        if not filtered:
            print("\n⚠️  처리 가능한 매장이 없습니다.")
            return {"processed": [], "summary": {"success": 0, "failed": 0}}
        
        summary = {
            "filtered": len(filtered),
            "skipped": len(reports) - len(filtered),
            "total_reports": len(reports)
        }
        
        return {"processed": filtered, "summary": summary}


async def main():
    """메인 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="StoreAgent → NewProductAgent 통합 파이프라인")
    parser.add_argument('--stores', nargs='+', help='특정 매장 코드만 처리 (예: 002816BA73 614B42817C)')
    parser.add_argument('--dry-run', action='store_true', help='실제 실행 없이 필터링만 확인')
    
    args = parser.parse_args()
    
    pipeline = IntegratedPipeline()
    
    if args.dry_run:
        # Dry-run: 필터링만 확인
        print("\n[DRY-RUN MODE] 실제 실행 없이 필터링 확인만 수행\n")
        reports = pipeline.find_store_reports()
        
        print(f"총 {len(reports)}개 리포트 발견\n")
        print("화이트리스트 필터링 결과:")
        
        for report_path in reports:
            is_allowed, industry, _ = pipeline.check_industry(report_path)
            store_code = report_path.parent.name.replace('analysis_', '').split('_')[0]
            status = "✓ 처리 대상" if is_allowed else "✗ 스킵"
            print(f"  {status} | {store_code} | {industry}")
        
        return
    
    if args.stores:
        # 특정 매장만 처리
        result = await pipeline.run_specific_stores(args.stores)
    else:
        # 전체 처리
        result = await pipeline.run_all()
    
    print("\n" + "="*70)
    print("파이프라인 완료!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
