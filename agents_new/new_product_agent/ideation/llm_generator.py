"""
LLM Generator - Gemini 2.5 Flash를 활용한 신제품 아이디어 생성
OpenAI SDK + Gemini API Key 방식 사용
"""
from typing import List, Dict, Any
import json
import os
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, USER_PROMPT


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
        Gemini 사용 불가 시 더미 응답 생성
        """
        best = insights[0] if insights else {
            "category": "음료", 
            "keyword": "시즈널", 
            "rank": 1
        }
        
        store_male = audience["store_gender"]["male"]
        store_female = audience["store_gender"]["female"]
        
        return {
            "insight": {
                "store_code": store["code"],
                "gender_summary": f"남성이 {store_male:.1f}%로 높습니다",
                "age_summary": "10·20대와 50대 비중이 큽니다",
                "reasoning": {
                    "gender_rule": "55% 우세 규칙 적용",
                    "age_rule": "최소 칸(≤3)로 누적 ≥50% 규칙",
                    "numbers": {
                        "store_gender": {
                            "male": store_male, 
                            "female": store_female
                        },
                        "industry_gender": ind_numbers["gender"],
                        "store_age": audience["store_age"],
                        "industry_age": ind_numbers["age"]
                    }
                }
            },
            "proposals": [
                {
                    "menu_name": f"{best['keyword']} 콘셉트",
                    "category": best["category"],
                    "target": {
                        "gender": audience["gender"], 
                        "ages": audience["ages"]
                    },
                    "evidence": {
                        "category": best["category"], 
                        "keyword": best["keyword"], 
                        "rank": best["rank"],
                        "data_source": "네이버 데이터랩 쇼핑인사이트",
                        "rationale": f"{best['keyword']}는 {best['category']} 카테고리에서 {best['rank']}위로 높은 인기를 보이고 있습니다."
                    },
                    "data_backing": {
                        "customer_fit": f"{audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭",
                        "trend_score": f"순위 {best['rank']}위 = 높은 검색 빈도",
                        "market_gap": f"매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균"
                    },
                    "template_ko": (
                        f"{audience['gender']}과 {', '.join(audience['ages'])}의 사람들은 "
                        f"네이버 쇼핑에서 {best['category']} 카테고리에서 "
                        f"'{best['keyword']}' 키워드를 많이 찾았습니다(순위 {best['rank']}).\n\n"
                        f"**데이터 근거:**\n"
                        f"- 고객 적합도: {audience['gender']} {', '.join(audience['ages'])} 타겟과 매칭\n"
                        f"- 트렌드 점수: 순위 {best['rank']}위 = 높은 검색 빈도\n"
                        f"- 시장 격차: 매장 {audience['gender']} {store_male if audience['gender']=='남성' else store_female:.1f}% vs 업종 평균\n\n"
                        f"따라서 이를 결합한 '{best['keyword']} 콘셉트' 메뉴를 "
                        f"개발해보는 것을 추천드립니다."
                    )
                }
            ]
        }
