"""
LLM Generator - Gemini 2.5 Flash를 활용한 신제품 아이디어 생성
OpenAI SDK + Gemini API Key 방식 사용
"""
from typing import List, Dict, Any
import json
import os
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, USER_PROMPT
import matplotlib.pyplot as plt
import platform

# 한글 폰트 설정
def set_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == "Windows":
        font_name = "Malgun Gothic"
    elif system == "Darwin":  # macOS
        font_name = "AppleGothic"
    else:  # Linux
        font_name = "DejaVu Sans"
    
    # matplotlib 폰트 설정
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False
    
    return font_name

# 폰트 설정 실행
KOREAN_FONT = set_korean_font()


class LLMGenerator:
    """
    Gemini 2.5 Flash를 사용한 신제품 아이디어 생성기
    OpenAI SDK를 사용하되 Gemini endpoint와 API key 사용
    """
    
    def __init__(self):
        """OpenAI SDK + Gemini API Key로 초기화"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            # OpenAI SDK with Gemini endpoint
            self.client = OpenAI(
                api_key=gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self.available = True
            print("[OK] LLMGenerator initialized with Gemini 2.5 Flash (OpenAI SDK)")
        except Exception as e:
            print(f"[WARN] Gemini client not available: {e}")
            self.client = None
            self.available = False

    def _format_insights(self, insights: List[Dict[str, Any]]) -> str:
        """
        키워드 리스트를 카테고리별로 그룹화하여 문자열로 포맷
        
        Args:
            insights: [{"category":"음료", "rank":1, "keyword":"피스타치오"}, ...]
            
        Returns:
            포맷된 문자열 (예: "- [음료] 피스타치오 (rank 1), ...")
        """
        by_cat: Dict[str, List[str]] = {}
        for r in insights:
            by_cat.setdefault(r["category"], []).append(
                f"{r['keyword']} (rank {r['rank']})"
            )
        lines = [f"- [{k}] " + ", ".join(v) for k, v in by_cat.items()]
        return "\n".join(lines) if lines else "- (no insights)"

    def _generate_menu_name(self, keyword: str, category: str) -> str:
        """
        키워드와 카테고리를 기반으로 완성된 메뉴명 생성
        
        Args:
            keyword: 식재료 키워드 (예: "무화과", "바나나")
            category: 카테고리 (예: "농산물", "음료", "과자/베이커리")
            
        Returns:
            완성된 메뉴명 (예: "무화과 스무디", "바나나 쿠키")
        """
        # 카테고리별 메뉴명 템플릿 (쌀 20kg 제거)
        menu_templates = {
            "농산물": {
                "무화과": ["무화과 스무디", "무화과 타르트", "허니 무화과 라떼", "무화과 파르페"],
                "바나나": ["바나나 스무디", "바나나 브레드", "바나나 마카롱", "바나나 푸딩"],
                "딸기": ["딸기 스무디", "딸기 타르트", "딸기 라떼", "딸기 파르페"],
                "블루베리": ["블루베리 스무디", "블루베리 마핀", "블루베리 라떼", "블루베리 케이크"],
                "망고": ["망고 스무디", "망고 타르트", "망고 라떼", "망고 파르페"],
                "아보카도": ["아보카도 스무디", "아보카도 토스트", "아보카도 라떼", "아보카도 브레드"],
                "사과": ["사과 스무디", "사과 타르트", "사과 라떼", "사과 케이크"],
                "호두": ["호두 브레드", "호두 쿠키", "호두 라떼", "호두 케이크"],
                "기본": ["{keyword} 스무디", "{keyword} 쿠키", "{keyword} 타르트", "{keyword} 라떼"]
            },
            "음료": {
                "콜드브루": ["콜드브루", "바닐라 콜드브루", "헤이즐넛 콜드브루", "시나몬 콜드브루"],
                "라떼": ["바닐라 라떼", "헤이즐넛 라떼", "카라멜 라떼", "시나몬 라떼"],
                "아메리카노": ["아메리카노", "아이스 아메리카노", "롱 블랙", "에스프레소"],
                "프라푸치노": ["바닐라 프라푸치노", "모카 프라푸치노", "카라멜 프라푸치노", "헤이즐넛 프라푸치노"],
                "밀크셰이크": ["바닐라 밀크셰이크", "초콜릿 밀크셰이크", "딸기 밀크셰이크", "바나나 밀크셰이크"],
                "기본": ["{keyword} 라떼", "{keyword} 스무디", "{keyword} 주스", "{keyword} 티"]
            },
            "과자/베이커리": {
                "크로와상": ["버터 크로와상", "초콜릿 크로와상", "아몬드 크로와상", "바닐라 크로와상"],
                "마카롱": ["바닐라 마카롱", "초콜릿 마카롱", "딸기 마카롱", "라벤더 마카롱"],
                "케이크": ["초콜릿 케이크", "딸기 케이크", "티라미수", "치즈케이크"],
                "수제 빵": ["소프트 빵", "크림 빵", "단팥 빵", "야채 빵"],
                "도넛": ["글레이즈드 도넛", "초콜릿 도넛", "바닐라 도넛", "딸기 도넛"],
                "쿠키": ["초콜릿 쿠키", "오트밀 쿠키", "버터 쿠키", "견과류 쿠키"],
                "기본": ["{keyword} 쿠키", "{keyword} 브레드", "{keyword} 마카롱", "{keyword} 케이크"]
            }
        }
        
        # 카테고리별 템플릿 선택
        category_templates = menu_templates.get(category, menu_templates["농산물"])
        
        # 키워드별 특정 템플릿이 있으면 사용, 없으면 기본 템플릿 사용
        if keyword in category_templates:
            templates = category_templates[keyword]
        else:
            templates = category_templates.get("기본", ["{keyword} 스무디", "{keyword} 쿠키"])
        
        # 랜덤하게 하나 선택
        import random
        template = random.choice(templates)
        
        # 템플릿에 키워드 삽입
        return template.format(keyword=keyword)
        
    def _generate_multiple_proposals(self, insights: List[Dict], audience: Dict, store_male: float, store_female: float) -> List[Dict]:
        """
        여러 개의 신제품 제안 생성 (2-3개, 카테고리 조합)
        
        Args:
            insights: 크롤링된 키워드 리스트
            audience: 타겟 고객 정보
            store_male: 매장 남성 비율
            store_female: 매장 여성 비율
            
        Returns:
            제안 리스트 (2-3개, 다양한 카테고리 조합)
        """
        proposals = []
        
        # 쌀 관련 키워드 필터링
        filtered_insights = [insight for insight in insights if not any(keyword in insight.get("keyword", "").lower() for keyword in ["쌀", "rice", "20kg", "kg"])]
        
        # 카테고리별로 키워드 분류
        keywords_by_category = {
            "농산물": [],
            "음료": [],
            "과자/베이커리": []
        }
        
        for insight in filtered_insights:
            category = insight.get("category", "")
            if category in keywords_by_category:
                keywords_by_category[category].append(insight)
        
        # ✅ 카테고리 조합별 메뉴 생성
        # 1. 농산물 + 음료 조합 (예: "딸기 라떼", "바나나 스무디")
        if keywords_by_category["농산물"] and keywords_by_category["음료"]:
            agriculture = keywords_by_category["농산물"][0]
            beverage = keywords_by_category["음료"][0]
            proposal = {
                "menu_name": f"{agriculture['keyword']} {beverage['keyword']}",
                "category": "음료",
                "target": {
                    "gender": audience["gender"], 
                    "ages": audience["ages"]
                },
                "evidence": {
                    "category": f"농산물({agriculture['keyword']}) + 음료({beverage['keyword']})", 
                    "keyword": f"{agriculture['keyword']} × {beverage['keyword']}", 
                    "rank": min(agriculture['rank'], beverage['rank']),
                    "data_source": "네이버 데이터랩 쇼핑인사이트",
                    "rationale": f"{agriculture['keyword']}(농산물)와 {beverage['keyword']}(음료)를 조합하여 새로운 메뉴를 제안합니다."
                },
                "data_backing": {
                    "customer_fit": f"{audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭",
                    "trend_score": f"농산물 순위 {agriculture['rank']}위 + 음료 순위 {beverage['rank']}위",
                    "market_gap": f"매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균"
                },
                "template_ko": (
                    f"{audience['gender']}과 {', '.join(audience['ages'])}의 사람들은 "
                    f"네이버 쇼핑에서 '{agriculture['keyword']}'와 '{beverage['keyword']}'를 많이 찾았습니다.\n\n"
                    f"**데이터 근거:**\n"
                    f"- 고객 적합도: {audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭\n"
                    f"- 트렌드 점수: 농산물 순위 {agriculture['rank']}위 + 음료 순위 {beverage['rank']}위\n"
                    f"- 시장 격차: 매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균\n\n"
                    f"따라서 '{agriculture['keyword']} {beverage['keyword']}' 메뉴를 개발해보는 것을 추천드립니다."
                )
            }
            proposals.append(proposal)
        
        # 2. 농산물 + 베이커리 조합 (예: "딸기 타르트", "바나나 케이크")
        if keywords_by_category["농산물"] and keywords_by_category["과자/베이커리"]:
            agriculture = keywords_by_category["농산물"][-1] if len(keywords_by_category["농산물"]) > 1 else keywords_by_category["농산물"][0]
            bakery = keywords_by_category["과자/베이커리"][0]
            proposal = {
                "menu_name": f"{agriculture['keyword']} {bakery['keyword']}",
                "category": "과자/베이커리",
                "target": {
                    "gender": audience["gender"], 
                    "ages": audience["ages"]
                },
                "evidence": {
                    "category": f"농산물({agriculture['keyword']}) + 베이커리({bakery['keyword']})", 
                    "keyword": f"{agriculture['keyword']} × {bakery['keyword']}", 
                    "rank": min(agriculture['rank'], bakery['rank']),
                    "data_source": "네이버 데이터랩 쇼핑인사이트",
                    "rationale": f"{agriculture['keyword']}(농산물)와 {bakery['keyword']}(베이커리)를 조합하여 새로운 메뉴를 제안합니다."
                },
                "data_backing": {
                    "customer_fit": f"{audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭",
                    "trend_score": f"농산물 순위 {agriculture['rank']}위 + 베이커리 순위 {bakery['rank']}위",
                    "market_gap": f"매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균"
                },
                "template_ko": (
                    f"{audience['gender']}과 {', '.join(audience['ages'])}의 사람들은 "
                    f"네이버 쇼핑에서 '{agriculture['keyword']}'와 '{bakery['keyword']}'를 많이 찾았습니다.\n\n"
                    f"**데이터 근거:**\n"
                    f"- 고객 적합도: {audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭\n"
                    f"- 트렌드 점수: 농산물 순위 {agriculture['rank']}위 + 베이커리 순위 {bakery['rank']}위\n"
                    f"- 시장 격차: 매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균\n\n"
                    f"따라서 '{agriculture['keyword']} {bakery['keyword']}' 메뉴를 개발해보는 것을 추천드립니다."
                )
            }
            proposals.append(proposal)
        
        # 최대 3개까지만 반환
        return proposals[:2]
    def generate(
        self, 
        *, 
        store: Dict, 
        audience: Dict, 
        insights: List[Dict], 
        ind_numbers: Dict, 
        season: str | None = None
    ) -> Dict[str, Any]:
        """
        신제품 아이디어 생성 (인사이트 + 템플릿 제안문)
        
        Args:
            store: {"industry": str, "area": str, "code": str}
            audience: {
                "gender": str, 
                "ages": List[str], 
                "store_gender": {"male": float, "female": float},
                "store_age": Dict[str, float]
            }
            insights: 크롤링된 키워드 리스트
            ind_numbers: {
                "gender": {"male": float, "female": float},
                "age": Dict[str, float]
            }
            season: 계절 정보 (선택, 현재 미사용)
            
        Returns:
            {
                "insight": {...},
                "proposals": [...]
            }
        """
        if not self.available:
            return self._dummy_response(store, audience, insights, ind_numbers)
        
        # 프롬프트 구성
        store_male = audience["store_gender"]["male"]
        store_female = audience["store_gender"]["female"]
        ind_male = ind_numbers["gender"]["male"]
        ind_female = ind_numbers["gender"]["female"]

        usr_prompt = USER_PROMPT.format(
            industry=store["industry"],
            area=store["area"],
            store_code=store["code"],
            gender=audience["gender"],
            ages=", ".join(audience["ages"]),
            insights_block=self._format_insights(insights),
            store_male=f"{store_male:.1f}", 
            store_female=f"{store_female:.1f}",
            ind_male=f"{ind_male:.1f}", 
            ind_female=f"{ind_female:.1f}",
            store_age_json=json.dumps(audience["store_age"], ensure_ascii=False),
            ind_age_json=json.dumps(ind_numbers["age"], ensure_ascii=False)
        )

        try:
            # OpenAI SDK로 Gemini 2.5 Flash 호출
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": usr_prompt}
                ],
                temperature=0.4,
                max_tokens=4000,  # 토큰 제한 명시
                response_format={"type": "json_object"}  # JSON 응답 강제
            )
            
            # 응답 추출
            content = response.choices[0].message.content
            
            # JSON 파싱
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print(f"[DEBUG] Raw response: {content[:500]}...")
                return self._dummy_response(store, audience, insights, ind_numbers)
                
        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return self._dummy_response(store, audience, insights, ind_numbers)

    def _dummy_response(
        self, 
        store: Dict, 
        audience: Dict, 
        insights: List[Dict], 
        ind_numbers: Dict
    ) -> Dict[str, Any]:
        """
        Gemini 사용 불가 시 더미 응답 생성 (인사이트 제거, 쌀 관련 키워드 필터링)
        """
        # 쌀 관련 키워드 필터링
        filtered_insights = [insight for insight in insights if not any(keyword in insight.get("keyword", "").lower() for keyword in ["쌀", "rice", "20kg", "kg"])]
        
        # 필터링된 키워드가 없으면 더미 키워드 사용
        if not filtered_insights:
            filtered_insights = [
                {"category": "음료", "keyword": "바닐라", "rank": 1},
                {"category": "과자/베이커리", "keyword": "마카롱", "rank": 2}
            ]
        
        store_male = audience["store_gender"]["male"]
        store_female = audience["store_gender"]["female"]
        
        return {
            "proposals": self._generate_multiple_proposals(filtered_insights, audience, store_male, store_female)
        }

