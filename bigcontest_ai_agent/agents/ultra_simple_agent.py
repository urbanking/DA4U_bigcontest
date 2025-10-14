"""
Ultra Simple Data Analysis Agent
초간단: 실시간 2개 + 기존 JSON 복사 + Gemini 분석
"""
import asyncio
import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from wrappers.marketplace_wrapper import run_marketplace_analysis
from wrappers.data_loader import get_data_loader
from utils.gemini_client import get_gemini_client


class UltraSimpleAgent:
    """
    초간단 에이전트
    
    1. Marketplace (실시간 분석)
    2. Panorama (실시간 분석)
    3. Mobility, Store, 상권별 JSON → 복사
    4. Gemini 분석
    5. 결과 저장
    """
    
    def __init__(self):
        self.data_loader = get_data_loader()
        self.gemini = get_gemini_client()
        self.output_dir = Path("test_output")
        self.output_dir.mkdir(exist_ok=True)
    
    async def analyze(self, address: str, industry: str = "외식업"):
        """전체 분석"""
        print(f"\n{'='*70}")
        print(f"📊 데이터 분석 시작: {address} ({industry})")
        print(f"{'='*70}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Windows asyncio subprocess 경고 억제
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning)
        
        # Step 1: 실시간 분석 (Marketplace + Panorama)
        print("🔴 [1/4] 실시간 분석 중...")
        realtime_data = await self._realtime_analysis(address, industry)
        
        # Step 2: 기존 JSON 복사
        print("\n📁 [2/4] 기존 데이터 복사 중...")
        copied_files = self._copy_existing_data(address, timestamp)
        
        # Step 3: Gemini 분석
        print("\n🤖 [3/4] AI 분석 중...")
        analysis = await self._analyze_all(address, industry, realtime_data, copied_files)
        
        # Step 4: 결과 저장
        print("\n💾 [4/4] 결과 저장 중...")
        result_files = self._save_results(analysis, timestamp)
        
        # Step 5: 시각화 생성
        print("\n🎨 [5/5] 데이터 시각화 중...")
        viz_files = self._create_visualizations(copied_files, timestamp)
        
        print(f"\n{'='*70}")
        print("✅ 분석 완료!")
        print(f"{'='*70}")
        print(f"\n📂 결과 위치: test_output/")
        for file in result_files:
            print(f"  - {file}")
        if viz_files:
            print(f"\n📊 시각화 폴더:")
            for folder in viz_files:
                print(f"  - {folder}")
        print()
        
        return analysis
    
    async def _realtime_analysis(self, address: str, industry: str) -> Dict[str, Any]:
        """실시간 분석: Marketplace + Panorama"""
        data = {}
        
        # 환경 변수로 Marketplace 스킵 가능
        skip_marketplace = os.getenv("SKIP_MARKETPLACE", "false").lower() == "true"
        
        # 1. Marketplace (Gemini CLI)
        if skip_marketplace:
            print("  🏪 Marketplace 분석 (스킵됨 - SKIP_MARKETPLACE=true)")
            data["marketplace"] = {"status": "skipped"}
        else:
            print("  🏪 Marketplace 분석 중...")
            try:
                result = await run_marketplace_analysis(address, industry, "500M")
                
                # 파일이 실제로 생성되었는지 확인
                if result.get("result", {}).get("pdf_count", 0) == 0:
                    print("     ⚠️  Marketplace 파일 생성 실패 - 기존 데이터 사용")
                    data["marketplace"] = {"status": "no_files_generated"}
                else:
                    data["marketplace"] = result
                    print("     ✓ Marketplace 완료")
            except Exception as e:
                print(f"     ✗ Marketplace 오류: {e}")
                data["marketplace"] = {"error": str(e)}
        
        # 2. Panorama (GPT-4o Vision)
        print("  🏞️  Panorama 분석 중...")
        try:
            from panorama_img_anal.analyze_area_by_address import analyze_area_by_address
            
            # 파노라마 분석 실행 (동기 함수이므로 asyncio.to_thread 사용)
            loop = asyncio.get_event_loop()
            panorama_result = await loop.run_in_executor(
                None,
                lambda: analyze_area_by_address(
                    address=address,
                    buffer_meters=300,
                    max_images=2,  # 비용 절감: 20 → 2
                    output_json_path=str(self.output_dir / f"panorama_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                )
            )
            
            data["panorama"] = panorama_result
            print("     ✓ Panorama 완료")
        except Exception as e:
            print(f"     ✗ Panorama 오류: {e}")
            data["panorama"] = {"error": str(e)}
        
        return data
    
    def _copy_existing_data(self, address: str, timestamp: str) -> Dict[str, str]:
        """기존 JSON 파일 복사"""
        copied = {}
        data_dir = Path("data outputs")
        
        # 1. 상권분석 JSON 복사
        print("  📋 상권분석 데이터...")
        marketplace_data = self.data_loader.find_marketplace_data(address)
        if marketplace_data:
            dest = self.output_dir / f"상권분석_{timestamp}.json"
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(marketplace_data, f, ensure_ascii=False, indent=2)
            copied["상권분석"] = str(dest)
            print(f"     ✓ 복사: {dest.name}")
        
        # 2. Mobility JSON 복사
        print("  🚶 Mobility 데이터...")
        dong = self._extract_dong(address)
        if dong:
            print(f"     → 행정동: {dong}")
            mobility_data = self.data_loader.find_mobility_data(dong)
            if mobility_data:
                dest = self.output_dir / f"mobility_{timestamp}.json"
                with open(dest, 'w', encoding='utf-8') as f:
                    json.dump(mobility_data, f, ensure_ascii=False, indent=2)
                copied["mobility"] = str(dest)
                print(f"     ✓ 복사: {dest.name}")
            else:
                print(f"     ✗ {dong} 데이터 없음")
        else:
            print(f"     ✗ 행정동을 찾을 수 없음")
        
        # 3. Store JSON 복사 (옵션)
        print("  🏬 Store 데이터 (선택)...")
        try:
            store_data = self.data_loader.load_store_data()
            if store_data:
                dest = self.output_dir / f"store_{timestamp}.json"
                with open(dest, 'w', encoding='utf-8') as f:
                    json.dump(store_data, f, ensure_ascii=False, indent=2)
                copied["store"] = str(dest)
                print(f"     ✓ 복사: {dest.name}")
        except Exception as e:
            print(f"     ⚠️  Store 데이터 없음 (선택 항목)")
        
        # 4. Panorama JSON 복사 (스킵 - 실시간만 사용)
        print("  🌆 Panorama 데이터...")
        print(f"     → 실시간 분석만 사용 (기존 데이터 스킵)")
        
        return copied
    
    def _extract_dong(self, address: str) -> str:
        """
        주소에서 동 추출 (지능형 매칭)
        
        1. 직접 동 이름 추출
        2. 주소-동 매핑 딕셔너리 사용
        3. Gemini API로 동 판단 (LLM)
        """
        import re
        
        # 1. 직접 동 이름이 있는 경우
        match = re.search(r'([가-힣]+[0-9]?가?[0-9]?동)', address)
        if match:
            dong_name = match.group(1)
            # "성동" 같은 구 이름은 제외
            if dong_name != "성동":
                return dong_name
        
        # 2. 주소-동 매핑 딕셔너리 (성동구 기준)
        address_dong_map = {
            # 왕십리 지역
            "왕십리역": "왕십리2동",
            "왕십리": "왕십리2동",
            "상왕십리역": "왕십리2동",
            
            # 성수 지역
            "성수역": "성수2가1동",
            "성수": "성수2가1동",
            "뚝섬역": "성수1가1동",
            "서울숲역": "성수1가2동",
            "서울숲": "성수1가2동",
            
            # 금호 지역
            "금호역": "금호1가동",
            "금호도서관": "금호1가동",
            "금호": "금호1가동",
            "신금호역": "금호4가동",
            
            # 옥수 지역
            "옥수역": "옥수동",
            "옥수": "옥수동",
            
            # 행당 지역
            "행당역": "행당1동",
            "행당": "행당1동",
            
            # 마장 지역
            "마장역": "마장동",
            "마장": "마장동",
            
            # 한양대 지역
            "한양대역": "행당1동",
            "한양대": "행당1동",
            
            # 응봉 지역
            "응봉": "응봉동",
            
            # 답십리 지역
            "답십리역": "용답동",
            "답십리": "용답동",
        }
        
        # 매핑 딕셔너리에서 찾기 (부분 매칭)
        for keyword, dong in address_dong_map.items():
            if keyword in address:
                print(f"  💡 주소 매칭: '{address}' → {dong}")
                return dong
        
        # 3. Gemini API로 동 판단 (LLM - 항상 실행)
        print(f"  🤖 LLM으로 동 판단 중: {address}")
        try:
            # 사용 가능한 동 목록
            available_dongs = [
                "금호1가동", "금호2.3가동", "금호4가동",
                "마장동", "사근동",
                "성수1가1동", "성수1가2동", "성수2가1동", "성수2가3동",
                "송정동", "옥수동",
                "왕십리2동", "왕십리도선동",
                "용답동", "응봉동",
                "행당1동", "행당2동"
            ]
            
            prompt = f"""
다음은 서울 성동구의 주소 또는 장소명입니다. 어느 행정동에 속하는지 판단하세요.

입력: {address}

사용 가능한 행정동 (성동구):
{', '.join(available_dongs)}

**중요:**
- 주소나 장소명을 분석하여 가장 가능성 높은 행정동 1개만 정확히 응답하세요
- 동 이름만 답하세요 (예: 금호1가동)
- 확신이 없으면 주변 키워드를 기반으로 추론하세요

응답:"""
            
            response = self.gemini.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="gemini-2.0-flash-exp",
                temperature=0.1
            )
            
            # 응답에서 동 이름 추출
            response_clean = response.strip()
            for dong in available_dongs:
                if dong in response_clean:
                    print(f"  ✓ LLM 판단: '{address}' → {dong}")
                    return dong
            
            print(f"  ⚠️  LLM 응답에서 동 이름 없음: {response_clean[:100]}")
            
        except Exception as e:
            print(f"  ✗ LLM 판단 실패: {e}")
        
        # 매칭 실패
        print(f"  ⚠️  동을 찾을 수 없음: {address}")
        return ""
    
    async def _analyze_all(
        self, 
        address: str, 
        industry: str,
        realtime_data: Dict[str, Any],
        copied_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """Gemini 종합 분석"""
        
        # 데이터 로드
        all_data = {"실시간": realtime_data, "기존데이터": {}}
        
        for key, filepath in copied_files.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    all_data["기존데이터"][key] = json.load(f)
            except:
                pass
        
        prompt = f"""
당신은 데이터 분석 전문가입니다. 다음 데이터를 종합 분석하세요.

**분석 대상**
- 주소: {address}
- 업종: {industry}

**사용 가능한 데이터**
1. 실시간 Marketplace 분석
2. 실시간 Panorama 분석
3. 기존 상권분석 데이터
4. 기존 Mobility 데이터
5. 기존 Store 데이터

**데이터 요약**
{json.dumps(all_data, ensure_ascii=False, indent=2)[:4000]}

**출력 형식 (JSON)**:
{{
  "핵심_인사이트": [
    "인사이트 1 (데이터 근거 포함)",
    "인사이트 2",
    "인사이트 3"
  ],
  "강점": [
    "강점 1",
    "강점 2"
  ],
  "리스크": [
    "리스크 1",
    "리스크 2"
  ],
  "기회_요인": [
    "기회 1",
    "기회 2"
  ],
  "추천사항": [
    "추천 1",
    "추천 2",
    "추천 3"
  ],
  "종합_평가": "2-3문장으로 종합 평가",
  "데이터_신뢰도": "high/medium/low"
}}
"""
        
        try:
            response = self.gemini.chat_completion_json(
                messages=[{"role": "user", "content": prompt}],
                model="gemini-2.0-flash-exp",
                temperature=0.3
            )
            
            # 응답 검증 및 파싱
            if not response or (isinstance(response, str) and response.strip() == ""):
                print(f"     ✗ Gemini 빈 응답 - 기본 분석 사용")
                analysis = self._create_default_analysis(address, industry, all_data)
            elif isinstance(response, str):
                # JSON 파싱 시도
                try:
                    # 마크다운 코드블록 제거
                    cleaned = response.strip()
                    if cleaned.startswith("```"):
                        # ```json ... ``` 제거
                        cleaned = cleaned.split("```")[1]
                        if cleaned.startswith("json"):
                            cleaned = cleaned[4:].strip()
                    
                    analysis = json.loads(cleaned)
                except json.JSONDecodeError as je:
                    print(f"     ✗ JSON 파싱 실패 - 원본 응답 사용")
                    print(f"     응답 미리보기: {response[:200]}...")
                    # JSON 파싱 실패시 기본 분석
                    analysis = self._create_default_analysis(address, industry, all_data)
            else:
                analysis = response
            
            return {
                "status": "success",
                "address": address,
                "industry": industry,
                "분석": analysis,
                "데이터_소스": {
                    "실시간": list(realtime_data.keys()),
                    "기존": list(copied_files.keys())
                }
            }
            
        except Exception as e:
            print(f"     ✗ Gemini 분석 오류: {e}")
            # 에러 발생시에도 기본 분석 제공
            return {
                "status": "partial_success",
                "address": address,
                "industry": industry,
                "분석": self._create_default_analysis(address, industry, all_data),
                "데이터_소스": {
                    "실시간": list(realtime_data.keys()),
                    "기존": list(copied_files.keys())
                },
                "error": str(e)
            }
    
    def _create_default_analysis(
        self, 
        address: str, 
        industry: str, 
        all_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gemini 분석 실패시 기본 분석 생성
        
        Args:
            address: 분석 주소
            industry: 업종
            all_data: 수집된 모든 데이터
            
        Returns:
            기본 분석 결과
        """
        # 사용 가능한 데이터 소스 확인
        available_sources = []
        if all_data.get("실시간"):
            available_sources.extend(all_data["실시간"].keys())
        if all_data.get("기존데이터"):
            available_sources.extend(all_data["기존데이터"].keys())
        
        return {
            "핵심_인사이트": [
                f"{address} 지역에 대한 데이터 수집 완료",
                f"총 {len(available_sources)}개 데이터 소스 분석됨",
                "상세 분석을 위해 AI 분석 재실행 권장"
            ],
            "강점": [
                "다양한 데이터 소스 확보",
                f"{industry} 업종 관련 기초 데이터 수집 완료"
            ],
            "리스크": [
                "AI 분석이 일시적으로 실패하여 기본 분석만 제공됨",
                "상세 인사이트를 위해 분석 재실행 필요"
            ],
            "기회_요인": [
                "수집된 데이터를 기반으로 재분석 가능",
                "추가 데이터 확보 시 더 정확한 분석 가능"
            ],
            "추천사항": [
                "AI 분석을 재실행하여 상세 인사이트 확보",
                "수집된 JSON 파일을 직접 확인하여 데이터 검토",
                "필요시 개별 데이터 소스별 상세 분석 수행"
            ],
            "종합_평가": f"{address} 지역의 {industry} 업종 관련 데이터가 성공적으로 수집되었습니다. AI 분석이 일시적으로 실패하여 기본 분석만 제공되었으며, 재실행을 통해 더 상세한 인사이트를 얻을 수 있습니다.",
            "데이터_신뢰도": "medium",
            "사용된_데이터_소스": available_sources
        }
    
    def _save_results(self, analysis: Dict[str, Any], timestamp: str) -> list:
        """결과 저장"""
        saved_files = []
        
        # 1. JSON 저장
        json_file = self.output_dir / f"final_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        saved_files.append(json_file.name)
        print(f"  ✓ {json_file.name}")
        
        # 2. TXT 리포트 저장
        if analysis.get("status") == "success":
            txt_file = self.output_dir / f"final_report_{timestamp}.txt"
            report = self._generate_report(analysis)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(report)
            saved_files.append(txt_file.name)
            print(f"  ✓ {txt_file.name}")
        
        return saved_files
    
    def _generate_report(self, analysis: Dict[str, Any]) -> str:
        """텍스트 리포트 생성"""
        result = analysis.get("분석", {})
        
        report = f"""
{'='*70}
📊 데이터 분석 리포트
{'='*70}

📍 주소: {analysis.get('address')}
🏢 업종: {analysis.get('industry')}
📅 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 데이터 신뢰도: {result.get('데이터_신뢰도', 'N/A')}

{'='*70}
💡 핵심 인사이트
{'='*70}
"""
        for i, insight in enumerate(result.get("핵심_인사이트", []), 1):
            report += f"{i}. {insight}\n"
        
        report += f"""
{'='*70}
✅ 강점
{'='*70}
"""
        for item in result.get("강점", []):
            report += f"• {item}\n"
        
        report += f"""
{'='*70}
⚠️ 리스크
{'='*70}
"""
        for item in result.get("리스크", []):
            report += f"• {item}\n"
        
        report += f"""
{'='*70}
🎯 기회 요인
{'='*70}
"""
        for item in result.get("기회_요인", []):
            report += f"• {item}\n"
        
        report += f"""
{'='*70}
📋 추천사항
{'='*70}
"""
        for i, item in enumerate(result.get("추천사항", []), 1):
            report += f"{i}. {item}\n"
        
        report += f"""
{'='*70}
📝 종합 평가
{'='*70}
{result.get('종합_평가', 'N/A')}

{'='*70}
"""
        return report
    
    def _create_visualizations(self, copied_files: Dict[str, str], timestamp: str) -> list:
        """데이터 시각화 생성 - test_output 폴더의 최신 JSON 자동 시각화"""
        viz_folders = []
        
        # matplotlib 설치 확인
        try:
            import matplotlib
        except ImportError:
            print("     ⚠️  matplotlib 미설치 - 시각화 건너뜀")
            print("     💡 설치: pip install matplotlib")
            return viz_folders
        
        # 직접 함수 import해서 호출 (subprocess 대신!)
        try:
            from visualize_mobility import visualize_latest_from_folder as viz_mobility
            from visualize_store import visualize_latest_from_folder as viz_store
            
            # 1. Mobility 시각화
            print("  [Mobility] 시각화 중...")
            if viz_mobility(str(self.output_dir)):
                viz_folders.append("mobility_viz_* (7개 그래프)")
                print("     ✓ 완료")
            else:
                print("     → mobility_*.json 없음")
            
            # 2. Store 시각화
            print("  [Store] 시각화 중...")
            if viz_store(str(self.output_dir)):
                viz_folders.append("store_viz_* (8개 그래프)")
                print("     ✓ 완료")
            else:
                print("     → store_*.json 없음")
                
        except Exception as e:
            print(f"     ⚠️  시각화 오류: {e}")
        
        return viz_folders


async def main():
    """실행"""
    import sys
    
    if len(sys.argv) < 2:
        print("\n사용법: python ultra_simple_agent.py <주소> [업종]")
        print("\n예제:")
        print("  python ultra_simple_agent.py '왕십리역' '외식업'")
        print("  python ultra_simple_agent.py '성수역'")
        return
    
    address = sys.argv[1]
    industry = sys.argv[2] if len(sys.argv) > 2 else "외식업"
    
    agent = UltraSimpleAgent()
    await agent.analyze(address, industry)


if __name__ == "__main__":
    import sys
    
    # Windows asyncio 정책 설정
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())

