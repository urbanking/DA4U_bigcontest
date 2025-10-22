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
        # Always use repo-root test_output regardless of current working directory
        self.output_dir = Path(__file__).parent / "test_output"
        self.output_dir.mkdir(exist_ok=True)
        try:
            print(f"[OutputDir] Using: {self.output_dir.resolve()}")
        except Exception:
            pass
    
    async def analyze(self, address: str, industry: str = "외식업"):
        """전체 분석"""
        return await self._run_analysis(address, industry)
    
    async def analyze_with_store_code(self, address: str, store_code: str, industry: str = "외식업"):
        """상점 코드와 함께 분석"""
        print(f"\n{'='*70}")
        print(f"🏪 매장별 분석 시작: {store_code} ({address})")
        print(f"{'='*70}\n")
        
        # 상점 코드 정보를 추가하여 분석 실행
        result = await self._run_analysis(address, industry, store_code)
        
        # 상점 코드 정보를 결과에 추가
        if isinstance(result, dict):
            result["store_code"] = store_code
        
        return result
    
    async def _run_analysis(self, address: str, industry: str, store_code: str = None):
        """분석 실행 공통 로직"""
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
        copied_files = self._copy_existing_data(address, timestamp, store_code)
        
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
        
        # 분석 결과에 복사된 파일들 정보 추가
        if isinstance(analysis, dict):
            analysis["copied_files"] = copied_files
        
        return analysis
    
    async def _realtime_analysis(self, address: str, industry: str) -> Dict[str, Any]:
        """실시간 분석: Marketplace → Panorama (순차 실행)"""
        data = {}
        
        # 환경 변수로 스킵 가능
        skip_marketplace = os.getenv("SKIP_MARKETPLACE", "false").lower() == "true"
        skip_panorama = os.getenv("SKIP_PANORAMA", "false").lower() == "true"
        
        # 1. Marketplace 먼저 실행 (완료될 때까지 대기)
        if skip_marketplace:
            print("  🏪 Marketplace 분석 (스킵됨)")
            data["marketplace"] = {"status": "skipped"}
        else:
            print("  🏪 Marketplace 분석 시작 (5-7분 소요)...")
            print("     ⏰ Chrome 브라우저로 골목상권분석 사이트 자동 조작 중...")
            try:
                marketplace_result = await self._run_marketplace(address, industry)
                data["marketplace"] = marketplace_result
            except Exception as e:
                print(f"     ✗ Marketplace 오류: {e}")
                data["marketplace"] = {"error": str(e)}
        
        # 2. Marketplace 완료 후 Panorama 실행
        if skip_panorama:
            print("  🏞️  Panorama 분석 (스킵됨)")
            data["panorama"] = {"status": "skipped"}
        else:
            print("  🏞️  Panorama 분석 시작 (1-2분 소요)...")
            try:
                panorama_result = await self._run_panorama(address)
                data["panorama"] = panorama_result
            except Exception as e:
                print(f"     ✗ Panorama 오류: {e}")
                data["panorama"] = {"error": str(e)}
        
        return data
    
    async def _run_marketplace(self, address: str, industry: str) -> Dict[str, Any]:
        """Marketplace 분석 실행"""
        try:
            result = await run_marketplace_analysis(address, industry, "500M")
            
            # 파일이 실제로 생성되었는지 확인
            result_data = result.get("result", {})
            pdf_count = result_data.get("pdf_count", 0)
            png_count = result_data.get("png_count", 0)
            
            if pdf_count == 0 and png_count == 0:
                print("     ⚠️  Marketplace 실시간 분석 실패")
                print("     🔍 data outputs에서 기존 PDF 검색 중...")
                
                # Fallback(1): Gemini로 가장 유사한 PDF 선택
                fallback_pdf = self._find_fallback_marketplace_pdf_gemini(address)
                if not fallback_pdf:
                    # Fallback(2): 키워드 기반 단순 매칭
                    fallback_pdf = self._find_fallback_marketplace_pdf(address)
                if fallback_pdf:
                    return {"status": "fallback", "pdf_file": fallback_pdf}
                else:
                    print("     ⚠️  기존 PDF도 없음 - Marketplace 데이터 없이 진행")
                    return {"status": "no_files_generated"}
            else:
                file_info = f"PNG: {png_count}, PDF: {pdf_count}"
                print(f"     ✓ Marketplace 완료 ({file_info})")
                return result
        except Exception as e:
            print(f"     ✗ Marketplace 오류: {e}")
            print("     🔍 data outputs에서 기존 PDF 검색 중...")
            
            # Fallback(1): Gemini로 가장 유사한 PDF 선택
            fallback_pdf = self._find_fallback_marketplace_pdf_gemini(address)
            if not fallback_pdf:
                # Fallback(2): 키워드 기반 단순 매칭
                fallback_pdf = self._find_fallback_marketplace_pdf(address)
            if fallback_pdf:
                return {"status": "fallback", "pdf_file": fallback_pdf}
            else:
                raise
    
    async def _run_panorama(self, address: str) -> Dict[str, Any]:
        """Panorama 분석 실행"""
        try:
            from panorama_img_anal.analyze_area_by_address import analyze_area_by_address
            
            # 파노라마 분석 실행 (동기 함수이므로 asyncio.to_thread 사용)
            loop = asyncio.get_event_loop()
            panorama_result = await loop.run_in_executor(
                None,
                lambda: analyze_area_by_address(
                    address=address,
                    buffer_meters=300,
                    max_images=5,
                    output_json_path=str(self.output_dir / f"panorama_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                )
            )
            
            # 결과를 test_output에 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            panorama_output = self.output_dir / f"panorama_{timestamp}.json"
            with open(panorama_output, 'w', encoding='utf-8') as f:
                json.dump(panorama_result, f, ensure_ascii=False, indent=2)
            
            print(f"     ✓ Panorama 완료 (저장: {panorama_output.name})")
            return {
                **panorama_result,
                "panorama_file": str(panorama_output)
            }
        except Exception as e:
            print(f"     ✗ Panorama 오류: {e}")
            raise
    
    def _copy_existing_data(self, address: str, timestamp: str, store_code: str = None) -> Dict[str, str]:
        """기존 JSON 파일 복사"""
        copied = {}
        data_dir = Path("data outputs")
        
        # 0. Store Agent 리포트 복사 (store_code가 있을 때)
        if store_code:
            print(f"  🏪 Store Agent 리포트 ({store_code})...")
            store_analysis_file = self._find_store_analysis_report(store_code)
            if store_analysis_file:
                dest = self.output_dir / f"store_analysis_{store_code}_{timestamp}.json"
                import shutil
                shutil.copy2(store_analysis_file, dest)
                copied["store_analysis"] = str(dest)
                print(f"     ✓ 복사: {dest.name}")
            else:
                print(f"     ✗ {store_code} Store Agent 리포트 없음")
        
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
    
    def _find_store_analysis_report(self, store_code: str) -> str:
        """상점 코드로 Store Agent 분석 리포트 찾기"""
        try:
            base_dir = Path(__file__).parent
            reports_dir = base_dir / "data outputs" / "store_agent_reports"
            
            if not reports_dir.exists():
                return None
            
            # 상점 코드 패턴으로 파일 찾기
            pattern = f"*{store_code}*.json"
            matching_files = list(reports_dir.glob(pattern))
            
            if matching_files:
                # 최신 파일 선택 (파일명에 날짜가 포함되어 있음)
                latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
                return str(latest_file)
            
            return None
            
        except Exception as e:
            print(f"     ⚠️  Store 리포트 검색 오류: {e}")
            return None
    
    def _find_fallback_marketplace_pdf(self, address: str) -> str:
        """
        Marketplace 실패 시 data outputs에서 비슷한 상권 파일 찾기 (JSON 우선)
        
        Args:
            address: 검색할 주소
            
        Returns:
            복사된 파일 경로 (test_output 폴더) - JSON 우선, PDF/기타 파일 fallback
        """
        from datetime import datetime
        
        # repo-root 기준 경로
        base_dir = Path(__file__).parent
        data_folder = base_dir / "data outputs" / "상권분석서비스_결과"
        
        try:
            print(f"     [DEBUG] 검색 폴더: {data_folder.resolve()}")
        except Exception:
            print(f"     [DEBUG] 검색 폴더: {data_folder}")
        print(f"     [DEBUG] 폴더 존재: {data_folder.exists()}")
        
        if not data_folder.exists():
            print(f"     [DEBUG] 폴더가 없음!")
            return None
        
        # 주소 키워드 추출 (예: "왕십리역" → ["왕십리"])
        keywords = []
        for keyword in ["왕십리", "상왕십리", "성수", "금호", "옥수", "행당", "마장", "답십리", "한양대", "뚝섬", "서울숲"]:
            if keyword in address:
                keywords.append(keyword)
        
        # 키워드가 없으면 전체 주소 사용
        if not keywords:
            keywords = [address.replace(" ", "")]
        
        print(f"     [DEBUG] 검색 키워드: {keywords}")
        
        # 후보 파일 검색 (우선순위: pdf > json > md > png)
        all_candidates = []
        for pattern in ("*.pdf", "*.json", "*.md", "*.png"):
            all_candidates.extend(list(data_folder.glob(pattern)))
        print(f"     [DEBUG] 전체 후보 개수: {len(all_candidates)}")
        
        matched = []
        for f in all_candidates:
            name_wo_ext = f.stem
            for keyword in keywords:
                if keyword in name_wo_ext:
                    matched.append(f)
                    print(f"     [DEBUG] 매칭: {f.name} (키워드: {keyword})")
                    break
        print(f"     [DEBUG] 매칭된 후보: {len(matched)}개")
        
        if not matched:
            print(f"     [DEBUG] 매칭 실패! 첫 3개 PDF 이름:")
            for f in all_candidates[:3]:
                print(f"       - {f.name}")
            return None
        
        # 확장자 우선순위로 정렬 (JSON 우선)
        def ext_priority(path: Path) -> int:
            ext = path.suffix.lower()
            return {".json": 0, ".pdf": 1, ".md": 2, ".png": 3}.get(ext, 9)
        matched.sort(key=lambda p: (ext_priority(p), p.name))
        selected = matched[0]
        file_type = "JSON" if selected.suffix.lower() == ".json" else selected.suffix.upper().replace(".", "")
        print(f"     ✓ 발견: {selected.name} ({file_type})")
        
        # test_output으로 복사
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.output_dir / f"marketplace_report_{timestamp}{selected.suffix.lower()}"
        
        import shutil
        shutil.copy2(selected, dest)
        print(f"     ✓ 복사 완료: {dest.name}")
        
        return str(dest)

    def _find_fallback_marketplace_pdf_gemini(self, address: str) -> str:
        """Gemini를 사용해 가장 유사한 상권 PDF를 선택해 test_output으로 복사

        1) 후보 PDF를 다음 경로에서 수집:
           - data outputs/상권분석서비스_결과
           - marketplcae_anal/상권분석리포트
        2) 주소/행정동/역명 키워드와 파일명 리스트를 Gemini에 전달
        3) JSON으로 best_match 파일명을 받아 복사
        """
        from datetime import datetime

        try:
            # 후보 디렉토리 수집 (repo-root 기준)
            base_dir = Path(__file__).parent
            candidate_dirs = [
                base_dir / "data outputs" / "상권분석서비스_결과",
                base_dir / "marketplcae_anal" / "상권분석리포트",
            ]
            candidates = []
            for d in candidate_dirs:
                if d.exists():
                    # 다중 확장자 허용
                    for pattern in ("*.pdf", "*.json", "*.md", "*.png"):
                        candidates.extend(sorted(d.glob(pattern)))

            if not candidates:
                print("     [GEMINI] 후보 PDF가 없습니다")
                return None

            # 후보 목록 단순화
            cand_names = [p.name for p in candidates]
            dong = self._extract_dong(address) or ""

            # Gemini 프롬프트 구성
            prompt = (
                "아래는 상권분석 PDF 파일명 목록입니다. 주어진 주소/키워드와 가장 관련성이 높은 1개를 고르고, "
                "JSON으로만 답변하세요. 키는 best_match (정확한 파일명), alternatives (관련 순서로 최대 3개 파일명) 입니다.\n\n"
                f"주소: {address}\n"
                f"추정 행정동/키워드: {dong}\n"
                "선호 기준:\n"
                "- 파일명에 주소의 지하철역/동/랜드마크가 포함되면 가산점\n"
                "- 동일한 구/동 키워드를 우선\n"
                "- 유사 발음/철자도 허용 (예: 왕십리/상왕십리/한양대 인접 등)\n\n"
                "파일명 목록:\n" + "\n".join(f"- {name}" for name in cand_names) + "\n\n"
                "응답 예시: {\"best_match\": \"성수역_상권분석레포트.pdf\", \"alternatives\": [\"서울숲역...pdf\"]}"
            )

            gemini = self.gemini  # get_gemini_client()로 초기화된 글로벌 클라이언트
            try:
                content = gemini.chat_completion_json(
                    messages=[{"role": "user", "content": prompt}],
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    temperature=0.1,
                    max_tokens=300,
                )
            except Exception as e:
                print(f"     [GEMINI] API 오류: {e}")
                return None

            # JSON 파싱
            import json as _json
            try:
                data = _json.loads(content)
                best_name = (data.get("best_match") or "").strip()
            except Exception as e:
                print(f"     [GEMINI] JSON 파싱 오류: {e}")
                print(f"     [GEMINI] 원본: {str(content)[:200]}")
                return None

            if not best_name:
                print("     [GEMINI] best_match 없음")
                return None

            # 후보에서 파일 찾기 (정확 일치 → 부분 일치)
            match_path = None
            for p in candidates:
                if p.name == best_name:
                    match_path = p
                    break
            if not match_path:
                # 느슨한 매칭 (파일명 포함)
                lowered = best_name.lower()
                for p in candidates:
                    if lowered in p.name.lower():
                        match_path = p
                        break

            if not match_path:
                print(f"     [GEMINI] 후보에서 파일을 찾지 못함: {best_name}")
                return None

            # test_output으로 복사 (원본 확장자 유지)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = self.output_dir / f"marketplace_report_{timestamp}{match_path.suffix.lower()}"
            shutil.copy2(match_path, dest)
            print(f"     ✓ [GEMINI] 선택: {match_path.name} → {dest.name}")
            return str(dest)

        except Exception as e:
            print(f"     [GEMINI] 예외로 인해 키워드 매칭으로 폴백: {e}")
            return None
    
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
                },
                "실시간": realtime_data,
                "copied_files": copied_files
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
                "실시간": realtime_data,
                "copied_files": copied_files,
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
            if viz_mobility(str(self.output_dir.resolve())):
                viz_folders.append("mobility_viz_* (7개 그래프)")
                print("     ✓ 완료")
                # 존재 확인 (1~7 파일 중 일부 확인)
                mob_viz_dirs = sorted((self.output_dir).glob("mobility_viz_*"))
                if mob_viz_dirs:
                    try:
                        print(f"     [확인] {mob_viz_dirs[-1].resolve()}")
                    except Exception:
                        print(f"     [확인] {mob_viz_dirs[-1]}")
            else:
                print("     → mobility_*.json 없음")
            
            # 2. Store 시각화
            print("  [Store] 시각화 중...")
            if viz_store(str(self.output_dir.resolve())):
                viz_folders.append("store_viz_* (8개 그래프)")
                print("     ✓ 완료")
                store_viz_dirs = sorted((self.output_dir).glob("store_viz_*"))
                if store_viz_dirs:
                    try:
                        print(f"     [확인] {store_viz_dirs[-1].resolve()}")
                    except Exception:
                        print(f"     [확인] {store_viz_dirs[-1]}")
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

