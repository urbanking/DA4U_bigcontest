"""
New Product Agent - 신제품 제안 에이전트
StoreAgent 리포트 → 타깃 선정 → 크롤링 → LLM 생성 → 최종 응답
"""
from typing import Dict, Any, Optional
from .dto.inputs import build_new_product_input
from .dto.outputs import assemble_output
from .planner.selector import (
    should_activate, 
    select_categories,
    choose_gender, 
    choose_ages, 
    to_datalab_age_checks
)
from .utils.parsing import expand_under20, season_from_date
from .crawler.naver_datalab_client import NaverDatalabClient
from .ideation.llm_generator import LLMGenerator
from .ideation.reranker import validate_minimal
from .io.crawler_output_manager import CrawlerOutputManager
from .io.keyword_cache_loader import KeywordCacheLoader


class NewProductAgent:
    """
    신제품 제안 에이전트
    
    파이프라인:
    1. 입력 정규화 (StoreAgent 리포트 → DTO)
    2. 활성화 판정 (업종 화이트리스트 확인)
    3. 타깃 선정 (성별/연령 + 카테고리 매핑)
    4. 네이버 데이터랩 크롤링 (Top10 키워드)
    5. LLM 아이디어 생성 (Gemini 2.5 Flash)
    6. 최종 응답 조립 (insight + proposals)
    """
    
    def __init__(
        self, 
        *, 
        headless: bool = True, 
        save_outputs: bool = False, 
        output_dir: Optional[str] = None,
        use_cache: bool = True,
        cache_json_path: Optional[str] = None
    ):
        """
        Args:
            headless: 크롤러 헤드리스 모드 사용 여부
            save_outputs: 크롤링 결과 및 최종 결과 파일 저장 여부
            output_dir: 출력 디렉토리 경로 (None이면 open_sdk/output 사용)
            use_cache: 캐시 사용 여부 (기본: True, JSON 파일 사용)
            cache_json_path: 캐시 JSON 파일 경로 (기본: keywords_20251026.json)
        """
        self.headless = headless
        self.save_outputs = save_outputs
        self.use_cache = use_cache
        self._llm = None
        self._output_manager = CrawlerOutputManager(output_dir) if output_dir else CrawlerOutputManager() if save_outputs else None
        self._session_timestamp = None  # 세션 타임스탬프 저장
        
        # 크롤러 또는 캐시 로더 초기화
        if use_cache:
            self.crawler = None
            cache_path = cache_json_path or "keywords_20251026.json"
            self._cache_loader = KeywordCacheLoader(cache_path)
        else:
            self.crawler = NaverDatalabClient(headless=headless)
            self._cache_loader = None

    def _get_llm(self) -> LLMGenerator:
        """LLM Generator 싱글톤 패턴"""
        if self._llm is None:
            self._llm = LLMGenerator()
        return self._llm

    async def run(self, store_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        신제품 제안 파이프라인 실행
        
        Args:
            store_report: StoreAgent의 전체 JSON 리포트
            
        Returns:
            {
                "store_code": str,
                "activated": bool,
                "audience_filters": {...},
                "used_categories": [...],
                "keywords_top": [...],
                "insight": {...},
                "proposals": [...]
            }
        """
        print("\n" + "="*60)
        print("[NewProductAgent] 신제품 제안 파이프라인 시작")
        print("="*60)
        
        # 1) 입력 데이터 정규화
        print("\n[Step 1/6] 입력 데이터 정규화...")
        data = build_new_product_input(store_report)
        industry = data["industry"]
        store_code = data["store_code"]
        print(f"  - 매장코드: {store_code}")
        print(f"  - 업종: {industry}")
        print(f"  - 상권: {data['commercial_area']}")
        
        # 2) 활성화 판정
        print("\n[Step 2/6] Agent 활성화 판정...")
        if not should_activate(industry):
            print(f"  ✗ '{industry}' 업종은 화이트리스트에 없음 → Agent 비활성화")
            return assemble_output(
                store_code=store_code, 
                activated=False,
                audience={}, 
                categories=[], 
                keywords=[], 
                insight={}, 
                proposals=[]
            )
        print(f"  ✓ '{industry}' 업종 확인 → Agent 활성화")
        
        # 3) 성별/연령 & 카테고리 선정 (업종 평균 비교)
        print("\n[Step 3/6] 타깃 선정 (성별/연령)...")
        store_gender = data["store_audience"]["gender_ratio"]
        ind_gender   = data["industry_avg"]["gender_ratio"]
        
        gender_sel, _ = choose_gender(
            store_gender["male"], store_gender["female"],
            ind_gender["male"],   ind_gender["female"]
        )
        print(f"  - 선택된 성별: {gender_sel}")
        print(f"    (매장: 남 {store_gender['male']:.1f}%, 여 {store_gender['female']:.1f}% | "
              f"업종평균: 남 {ind_gender['male']:.1f}%, 여 {ind_gender['female']:.1f}%)")
        
        store_age = data["store_audience"]["age_groups"]   # {20↓,30,40,50,60+}
        ind_age   = data["industry_avg"]["age_groups"]
        
        store_age_exp = expand_under20(store_age)          # {"10대":x,"20대":y,...}
        ind_age_exp   = expand_under20(ind_age)
        
        ages_sel      = choose_ages(store_age_exp, ind_age_exp)
        datalab_ages  = to_datalab_age_checks(ages_sel)
        print(f"  - 선택된 연령: {', '.join(datalab_ages)}")
        
        categories    = select_categories(industry)
        print(f"  - 선택된 카테고리: {', '.join(categories)}")
        
        # 4) 크롤링 또는 캐시 로드 (네이버 데이터랩: 식품 하위 Top10 키워드)
        print("\n[Step 4/6] 키워드 수집...")
        print(f"  - 필터: 성별={gender_sel}, 연령={datalab_ages}, 카테고리={categories}")
        
        keywords = []
        
        # 캐시 사용
        if self.use_cache and self._cache_loader:
            print(f"  - 캐시 모드: JSON에서 로드 중...")
            try:
                keywords = self._cache_loader.get_keywords(
                    gender=gender_sel,
                    ages=datalab_ages,
                    categories=categories
                )
                print(f"  ✓ 캐시에서 {len(keywords)}개 키워드 로드 완료")
                if keywords:
                    print(f"    예시: {keywords[0]['keyword']} ({keywords[0]['category']}, rank {keywords[0]['rank']})")
            except Exception as e:
                print(f"  ⚠️ 캐시 로드 실패: {e}")
                keywords = []
        
        # 실시간 크롤링 (캐시 없는 경우)
        if not keywords and self.crawler:
            print(f"  - 크롤링 모드: 네이버 데이터랩 크롤링 중...")
            try:
                keywords = self.crawler.fetch_keywords(categories=categories, gender=gender_sel, ages=datalab_ages)
                print(f"  ✓ 크롤링 완료: {len(keywords)}개 키워드")
                if keywords:
                    print(f"    예시: {keywords[0]['keyword']} ({keywords[0]['category']}, rank {keywords[0]['rank']})")
            except Exception as e:
                print(f"  ⚠️ 크롤링 실패: {e}")
                keywords = []
        
        # 더미 키워드 (캐시도 크롤링도 실패한 경우)
        if not keywords:
            print(f"  ⚠️ 키워드 없음 → 더미 키워드 사용")
            dummy_keywords = {
                "카페": [
                    {"category": "음료", "rank": 1, "keyword": "콜드브루"},
                    {"category": "음료", "rank": 2, "keyword": "라떼"},
                    {"category": "음료", "rank": 3, "keyword": "아메리카노"},
                    {"category": "과자/베이커리", "rank": 1, "keyword": "크로와상"},
                    {"category": "과자/베이커리", "rank": 2, "keyword": "마카롱"},
                    {"category": "과자/베이커리", "rank": 3, "keyword": "케이크"},
                    {"category": "농산물", "rank": 1, "keyword": "바나나"},
                    {"category": "농산물", "rank": 2, "keyword": "딸기"},
                    {"category": "농산물", "rank": 3, "keyword": "블루베리"}
                ],
                "디저트": [
                    {"category": "과자/베이커리", "rank": 1, "keyword": "수제 케이크"},
                    {"category": "과자/베이커리", "rank": 2, "keyword": "마카롱"},
                    {"category": "과자/베이커리", "rank": 3, "keyword": "티라미수"},
                    {"category": "음료", "rank": 1, "keyword": "프라푸치노"},
                    {"category": "음료", "rank": 2, "keyword": "밀크셰이크"},
                    {"category": "농산물", "rank": 1, "keyword": "무화과"},
                    {"category": "농산물", "rank": 2, "keyword": "망고"},
                    {"category": "농산물", "rank": 3, "keyword": "아보카도"}
                ],
                "베이커리": [
                    {"category": "과자/베이커리", "rank": 1, "keyword": "수제 빵"},
                    {"category": "과자/베이커리", "rank": 2, "keyword": "크로와상"},
                    {"category": "과자/베이커리", "rank": 3, "keyword": "도넛"},
                    {"category": "과자/베이커리", "rank": 4, "keyword": "쿠키"},
                    {"category": "농산물", "rank": 1, "keyword": "바나나"},
                    {"category": "농산물", "rank": 2, "keyword": "사과"},
                    {"category": "농산물", "rank": 3, "keyword": "호두"}
                ],
                "카페·디저트": [
                    {"category": "음료", "rank": 1, "keyword": "콜드브루"},
                    {"category": "음료", "rank": 2, "keyword": "라떼"},
                    {"category": "음료", "rank": 3, "keyword": "아메리카노"},
                    {"category": "과자/베이커리", "rank": 1, "keyword": "수제 빵"},
                    {"category": "과자/베이커리", "rank": 2, "keyword": "마카롱"},
                    {"category": "과자/베이커리", "rank": 3, "keyword": "크로와상"},
                    {"category": "과자/베이커리", "rank": 4, "keyword": "케이크"},
                    {"category": "농산물", "rank": 1, "keyword": "바나나"},
                    {"category": "농산물", "rank": 2, "keyword": "딸기"},
                    {"category": "농산물", "rank": 3, "keyword": "무화과"}
                ]
            }
            
            industry = data["industry"]
            if industry in dummy_keywords:
                keywords = dummy_keywords[industry]
                print(f"  ✓ 더미 키워드 {len(keywords)}개 생성 완료")
        
        # 크롤링 결과 저장 (옵션)
        if self.save_outputs and self._output_manager and keywords:
            from datetime import datetime
            self._session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            metadata = {
                "industry": data["industry"],
                "commercial_area": data["commercial_area"],
                "target_gender": gender_sel,
                "target_ages": datalab_ages,
                "categories": categories
            }
            self._output_manager.save_keywords(keywords, store_code, metadata)
        
        # 5) LLM 아이디어 생성 (Gemini 2.5 Flash)
        print("\n[Step 5/6] LLM 아이디어 생성 (Gemini 2.5 Flash)...")
        llm = self._get_llm()
        season = season_from_date(data["analysis_date"])
        
        ind_numbers = {
            "gender": {
                "male": ind_gender["male"], 
                "female": ind_gender["female"]
            },
            "age": ind_age_exp
        }
        
        try:
            result = llm.generate(
                store={
                    "industry": data["industry"], 
                    "area": data["commercial_area"], 
                    "code": data["store_code"]
                },
                audience={
                    "gender": gender_sel, 
                    "ages": datalab_ages,
                    "store_gender": {
                        "male": store_gender["male"], 
                        "female": store_gender["female"]
                    },
                    "store_age": store_age_exp
                },
                insights=keywords,
                ind_numbers=ind_numbers,
                season=season
            )
            print(f"  ✓ LLM 생성 완료")
        except Exception as e:
            print(f"  ✗ LLM 생성 실패: {e}")
            result = {"insight": {}, "proposals": []}
        
        # 6) 검증 및 최종 응답 조립
        print("\n[Step 6/6] 제안 검증 및 최종 응답 조립...")
        proposals = validate_minimal(result.get("proposals", []))
        print(f"  ✓ 검증된 제안: {len(proposals)}개")
        
        final_output = assemble_output(
            store_code=store_code,
            activated=True,
            audience={
                "gender": gender_sel, 
                "ages": datalab_ages, 
                "store_age": store_age_exp
            },
            categories=categories,
            keywords=keywords,
            insight=result.get("insight", {}),
            proposals=proposals
        )
        
        print("\n" + "="*60)
        print("[NewProductAgent] 파이프라인 완료!")
        print("="*60 + "\n")
        
        # 최종 결과 저장 (옵션)
        if self.save_outputs and self._output_manager:
            self._output_manager.save_final_result(
                final_output, 
                store_code, 
                session_timestamp=self._session_timestamp
            )
        
        return final_output
