"""
페르소나 구성요소 및 분류 엔진 - 동적 페르소나 생성 지원
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
try:
    # 패키지로 실행될 때
    from .dynamic_persona_generator import DynamicPersonaGenerator, DynamicPersona
except ImportError:
    # 독립 실행될 때
    from dynamic_persona_generator import DynamicPersonaGenerator, DynamicPersona


class IndustryType(Enum):
    """업종 타입"""
    CAFE = "카페"
    CHINESE = "중식"
    CHICKEN = "치킨"
    KOREAN = "한식"
    DESSERT = "디저트"
    FASTFOOD = "패스트푸드"
    JAPANESE = "일식"
    WESTERN = "양식"


class CommercialZone(Enum):
    """상권 유형"""
    CENTRAL = "중심상권"
    RESIDENTIAL = "주거형"
    OFFICE = "오피스형"
    TRANSPORT = "교통형"
    MARKET = "시장형"


class CustomerType(Enum):
    """고객 유형"""
    RESIDENT = "거주형"
    WORKPLACE = "직장형"
    FLOATING = "유동형"


class StoreAge(Enum):
    """매장 단계"""
    NEW = "신규"
    STABLE = "안정기"
    OLD = "노후"


@dataclass
class PersonaComponents:
    """페르소나 구성요소"""
    industry: IndustryType
    commercial_zone: CommercialZone
    is_franchise: bool
    store_age: StoreAge
    main_customer_gender: str  # "남성", "여성", "혼합"
    main_customer_age: str     # "20대", "30대", "40대", "50대+", "혼합"
    customer_type: CustomerType
    new_customer_trend: str    # "증가", "감소", "정체"
    revisit_trend: str         # "증가", "감소", "정체"
    delivery_ratio: str        # "낮음", "중간", "높음"


class PersonaEngine:
    """페르소나 엔진 - 매장 특성을 기반으로 동적 페르소나 생성"""
    
    def __init__(self, use_dynamic_generation: bool = True):
        self.use_dynamic_generation = use_dynamic_generation
        self.persona_templates = self._load_persona_templates()
        self.marketing_focus_matrix = self._load_marketing_focus_matrix()
        
        # 동적 페르소나 생성기 초기화
        if self.use_dynamic_generation:
            self.dynamic_generator = DynamicPersonaGenerator()
        else:
            self.dynamic_generator = None
    
    def _load_persona_templates(self) -> Dict[str, Dict[str, Any]]:
        """페르소나 템플릿 로드"""
        return {
            "도심형_직장인_중식점": {
                "description": "도심 오피스 중식당 (직장형·배달중간·재방문↓)",
                "components": {
                    "industry": [IndustryType.CHINESE],
                    "commercial_zone": [CommercialZone.CENTRAL, CommercialZone.OFFICE],
                    "customer_type": [CustomerType.WORKPLACE],
                    "delivery_ratio": ["중간", "높음"],
                    "revisit_trend": ["감소", "정체"]
                },
                "risk_codes": ["R2", "R4", "R5"],
                "marketing_tone": "효율성, 속도, 가성비 중심",
                "key_channels": ["배달앱", "오피스 쿠폰", "점심 세트"],
                "strategies": [
                    "점심 피크 타임 회복: 11:30–13:30 전용 세트 메뉴",
                    "오후 재방문 유도: 2PM 할인쿠폰 문자 발송",
                    "배달 경쟁 강화: '빠른 준비시간' 강조 문구, 지도 리뷰 관리"
                ]
            },
            "감성_카페_여성층": {
                "description": "여성 20~30대 중심 카페 (중심상권·유동형·신규유입↓)",
                "components": {
                    "industry": [IndustryType.CAFE],
                    "commercial_zone": [CommercialZone.CENTRAL],
                    "customer_type": [CustomerType.FLOATING],
                    "main_customer_gender": ["여성"],
                    "main_customer_age": ["20대", "30대"],
                    "new_customer_trend": ["감소"]
                },
                "risk_codes": ["R1", "R7"],
                "marketing_tone": "감성, 비주얼, 트렌드 중심",
                "key_channels": ["인스타그램", "틱톡", "네이버지도"],
                "strategies": [
                    "SNS 신제품 노출: 인스타 릴스/틱톡 협찬, 감성 음료 신제품 출시",
                    "리뷰 UGC 이벤트: '해시태그 인증 시 무료샷 추가'",
                    "타깃 맞춤 키워드 광고: '데이트 카페', '포토존 카페'"
                ]
            },
            "프랜차이즈_치킨_배달형": {
                "description": "프랜차이즈 치킨집 (주거형·배달형·취소율↑)",
                "components": {
                    "industry": [IndustryType.CHICKEN],
                    "commercial_zone": [CommercialZone.RESIDENTIAL],
                    "is_franchise": [True],
                    "delivery_ratio": ["높음"],
                    "customer_type": [CustomerType.RESIDENT]
                },
                "risk_codes": ["R6", "R5"],
                "marketing_tone": "신뢰성, 일관성, 야식 중심",
                "key_channels": ["배달앱", "앱 리뷰", "포장할인"],
                "strategies": [
                    "앱리뷰 응대 캠페인: 1시간 내 답변/리뷰관리 시스템 구축",
                    "포장고객 유도: 2천원 포장할인 → 취소율↓",
                    "야식 타겟: 21–23시 광고 집중 (배달 앱 노출 리포지션)"
                ]
            },
            "신규_독립_한식점": {
                "description": "신규 독립 한식점 (주거형·신규유입↑·재방문↓)",
                "components": {
                    "industry": [IndustryType.KOREAN],
                    "commercial_zone": [CommercialZone.RESIDENTIAL],
                    "is_franchise": [False],
                    "store_age": [StoreAge.NEW],
                    "new_customer_trend": ["증가"],
                    "revisit_trend": ["감소"]
                },
                "risk_codes": ["R2", "R8"],
                "marketing_tone": "신뢰성, 지역밀착, 가정식 중심",
                "key_channels": ["네이버밴드", "지역카페", "리뷰이벤트"],
                "strategies": [
                    "단골 구축 페이백: 2회 방문 시 무료음료/쿠폰",
                    "지역 맘카페 공략: 네이버 밴드/카페 체험단 10명 초대",
                    "'가정식 안심' 이미지 강화: 리뷰 포토콘테스트"
                ]
            },
            "노후_중식당_전통형": {
                "description": "노후 중식당 (중심상권·남성 40~50대·매출정체)",
                "components": {
                    "industry": [IndustryType.CHINESE],
                    "commercial_zone": [CommercialZone.CENTRAL],
                    "store_age": [StoreAge.OLD],
                    "main_customer_gender": ["남성"],
                    "main_customer_age": ["40대", "50대+"]
                },
                "risk_codes": ["R3", "R4", "R9"],
                "marketing_tone": "전통성, 신뢰성, 품질 중심",
                "key_channels": ["지역신문", "간판", "상권지원센터"],
                "strategies": [
                    "시그니처 메뉴 리뉴얼: 고정 단골층 유지용 '전통+트렌드 메뉴' 혼합",
                    "현장 리노베이션 홍보: '30년 전통 신메뉴 런칭' 간판 교체",
                    "지자체 연계 홍보: 상권지원센터 프로모션 참여"
                ]
            }
        }
    
    def _load_marketing_focus_matrix(self) -> Dict[str, Dict[str, str]]:
        """마케팅 포인트 매트릭스 로드"""
        return {
            "industry": {
                "카페": "감성·비주얼 중심 SNS",
                "중식": "메뉴·가성비 중심",
                "치킨": "야식·즉시성 중심",
                "한식": "신뢰·품질 중심",
                "패스트푸드": "효율·속도 중심"
            },
            "commercial_zone": {
                "중심상권": "SNS·지도 노출 중심 홍보",
                "주거형": "단골/재방문 유도 (멤버십·쿠폰)",
                "오피스형": "점심 피크 타임/배달 최적화",
                "교통형": "빠른 서비스·간편메뉴 강조",
                "시장형": "가성비·현장 체험 강조"
            },
            "customer_demographics": {
                "여성_2030": "감성·비주얼·트렌드 콘텐츠",
                "남성_3050": "효율·속도·가성비 강조",
                "혼합": "균형잡힌 접근"
            },
            "customer_type": {
                "거주형": "단골 관리, 적립제·멤버십",
                "직장형": "점심 세트, 정기쿠폰, 퇴근시간 할인",
                "유동형": "지도·SNS 노출 강화, 한눈에 들어오는 메뉴판"
            }
        }
    
    async def analyze_store_persona(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        """매장 데이터를 분석하여 페르소나 구성요소 추출"""
        try:
            # 매장 기본 정보 추출
            industry = self._extract_industry(store_data)
            commercial_zone = self._extract_commercial_zone(store_data)
            is_franchise = self._extract_franchise_status(store_data)
            store_age = self._extract_store_age(store_data)
            
            # 고객 정보 추출
            customer_demographics = self._extract_customer_demographics(store_data)
            customer_type = self._extract_customer_type(store_data)
            
            # 트렌드 정보 추출
            trends = self._extract_trends(store_data)
            delivery_ratio = self._extract_delivery_ratio(store_data)
            
            persona_components = PersonaComponents(
                industry=industry,
                commercial_zone=commercial_zone,
                is_franchise=is_franchise,
                store_age=store_age,
                main_customer_gender=customer_demographics["gender"],
                main_customer_age=customer_demographics["age"],
                customer_type=customer_type,
                new_customer_trend=trends["new_customer"],
                revisit_trend=trends["revisit"],
                delivery_ratio=delivery_ratio
            )
            
            return {
                "components": persona_components,
                "raw_data": store_data
            }
            
        except Exception as e:
            return {
                "error": f"페르소나 분석 중 오류 발생: {str(e)}",
                "components": None,
                "raw_data": store_data
            }
    
    def _extract_industry(self, store_data: Dict[str, Any]) -> IndustryType:
        """업종 추출"""
        industry_map = {
            "카페": IndustryType.CAFE,
            "중식": IndustryType.CHINESE,
            "치킨": IndustryType.CHICKEN,
            "한식": IndustryType.KOREAN,
            "디저트": IndustryType.DESSERT,
            "패스트푸드": IndustryType.FASTFOOD,
            "일식": IndustryType.JAPANESE,
            "양식": IndustryType.WESTERN
        }
        
        industry = store_data.get("industry", "").lower()
        for key, value in industry_map.items():
            if key in industry:
                return value
        
        return IndustryType.KOREAN  # 기본값
    
    def _extract_commercial_zone(self, store_data: Dict[str, Any]) -> CommercialZone:
        """상권 유형 추출"""
        zone_map = {
            "중심상권": CommercialZone.CENTRAL,
            "주거형": CommercialZone.RESIDENTIAL,
            "오피스형": CommercialZone.OFFICE,
            "교통형": CommercialZone.TRANSPORT,
            "시장형": CommercialZone.MARKET
        }
        
        zone = store_data.get("commercial_zone", "").lower()
        for key, value in zone_map.items():
            if key in zone:
                return value
        
        return CommercialZone.RESIDENTIAL  # 기본값
    
    def _extract_franchise_status(self, store_data: Dict[str, Any]) -> bool:
        """프랜차이즈 여부 추출"""
        return store_data.get("is_franchise", False)
    
    def _extract_store_age(self, store_data: Dict[str, Any]) -> StoreAge:
        """매장 단계 추출"""
        age_data = store_data.get("store_age", "")
        
        if "신규" in str(age_data) or "1년" in str(age_data):
            return StoreAge.NEW
        elif "3년" in str(age_data) or "노후" in str(age_data):
            return StoreAge.OLD
        else:
            return StoreAge.STABLE
    
    def _extract_customer_demographics(self, store_data: Dict[str, Any]) -> Dict[str, str]:
        """고객 인구통계 추출"""
        demographics = store_data.get("customer_demographics", {})
        
        gender = demographics.get("gender", "혼합")
        age = demographics.get("age_group", "혼합")
        
        return {
            "gender": gender,
            "age": age
        }
    
    def _extract_customer_type(self, store_data: Dict[str, Any]) -> CustomerType:
        """고객 유형 추출"""
        customer_type_map = {
            "거주형": CustomerType.RESIDENT,
            "직장형": CustomerType.WORKPLACE,
            "유동형": CustomerType.FLOATING
        }
        
        customer_type = store_data.get("customer_type", "").lower()
        for key, value in customer_type_map.items():
            if key in customer_type:
                return value
        
        return CustomerType.RESIDENT  # 기본값
    
    def _extract_trends(self, store_data: Dict[str, Any]) -> Dict[str, str]:
        """트렌드 정보 추출"""
        trends = store_data.get("trends", {})
        
        new_customer = trends.get("new_customer", "정체")
        revisit = trends.get("revisit", "정체")
        
        return {
            "new_customer": new_customer,
            "revisit": revisit
        }
    
    def _extract_delivery_ratio(self, store_data: Dict[str, Any]) -> str:
        """배달 비중 추출"""
        delivery_ratio = store_data.get("delivery_ratio", "중간")
        
        if isinstance(delivery_ratio, (int, float)):
            if delivery_ratio >= 60:
                return "높음"
            elif delivery_ratio >= 30:
                return "중간"
            else:
                return "낮음"
        
        return delivery_ratio
    
    async def classify_persona(
        self, 
        persona_components: PersonaComponents, 
        store_data: Dict[str, Any] = None,
        risk_codes: List[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """페르소나 분류 - 동적 생성 또는 템플릿 매칭"""
        
        # 동적 생성 모드인 경우
        if self.use_dynamic_generation and self.dynamic_generator and store_data:
            try:
                dynamic_persona = await self.dynamic_generator.generate_dynamic_persona(
                    store_data=store_data,
                    persona_components=persona_components,
                    risk_codes=risk_codes
                )
                
                # DynamicPersona를 기존 형식으로 변환
                persona_dict = {
                    "description": dynamic_persona.description,
                    "marketing_tone": dynamic_persona.marketing_tone,
                    "key_channels": dynamic_persona.key_channels,
                    "strategies": dynamic_persona.strategies,
                    "risk_codes": dynamic_persona.risk_codes,
                    "characteristics": dynamic_persona.characteristics,
                    "target_demographics": dynamic_persona.target_demographics,
                    "behavioral_patterns": dynamic_persona.behavioral_patterns,
                    "pain_points": dynamic_persona.pain_points,
                    "motivations": dynamic_persona.motivations,
                    "confidence_score": dynamic_persona.confidence_score,
                    "generated_at": dynamic_persona.generated_at,
                    "is_dynamic": True
                }
                
                return dynamic_persona.persona_name, persona_dict
                
            except Exception as e:
                print(f"동적 페르소나 생성 실패, 템플릿 매칭으로 폴백: {e}")
                # 폴백: 기존 템플릿 매칭 방식 사용
        
        # 기존 템플릿 매칭 방식 (폴백 또는 동적 생성 비활성화 시)
        best_match = None
        best_score = 0
        
        for persona_name, template in self.persona_templates.items():
            score = self._calculate_match_score(persona_components, template["components"])
            
            if score > best_score:
                best_score = score
                best_match = persona_name
        
        if best_match:
            template_result = self.persona_templates[best_match].copy()
            template_result["is_dynamic"] = False
            return best_match, template_result
        else:
            # 기본 페르소나 반환
            return "기본_매장", {
                "description": "기본 매장 페르소나",
                "marketing_tone": "균형잡힌 접근",
                "key_channels": ["일반적인 마케팅 채널"],
                "strategies": ["기본적인 마케팅 전략"],
                "is_dynamic": False
            }
    
    def _calculate_match_score(self, components: PersonaComponents, template_components: Dict[str, List]) -> int:
        """매칭 점수 계산"""
        score = 0
        total_checks = 0
        
        # 업종 매칭
        if components.industry in template_components.get("industry", []):
            score += 3
        total_checks += 3
        
        # 상권 매칭
        if components.commercial_zone in template_components.get("commercial_zone", []):
            score += 2
        total_checks += 2
        
        # 프랜차이즈 매칭
        if components.is_franchise in template_components.get("is_franchise", []):
            score += 1
        total_checks += 1
        
        # 고객 유형 매칭
        if components.customer_type in template_components.get("customer_type", []):
            score += 2
        total_checks += 2
        
        # 배달 비중 매칭
        if components.delivery_ratio in template_components.get("delivery_ratio", []):
            score += 1
        total_checks += 1
        
        # 트렌드 매칭
        if components.new_customer_trend in template_components.get("new_customer_trend", []):
            score += 1
        total_checks += 1
        
        if components.revisit_trend in template_components.get("revisit_trend", []):
            score += 1
        total_checks += 1
        
        return (score / total_checks) * 100 if total_checks > 0 else 0
    
    def get_marketing_focus_points(self, persona_type: str, components: PersonaComponents) -> Dict[str, str]:
        """페르소나별 마케팅 포인트 반환"""
        focus_points = {}
        
        # 업종별 포인트
        industry_key = components.industry.value
        if industry_key in self.marketing_focus_matrix["industry"]:
            focus_points["industry_focus"] = self.marketing_focus_matrix["industry"][industry_key]
        
        # 상권별 포인트
        zone_key = components.commercial_zone.value
        if zone_key in self.marketing_focus_matrix["commercial_zone"]:
            focus_points["zone_focus"] = self.marketing_focus_matrix["commercial_zone"][zone_key]
        
        # 고객 인구통계별 포인트
        demo_key = f"{components.main_customer_gender}_{components.main_customer_age}"
        if demo_key in self.marketing_focus_matrix["customer_demographics"]:
            focus_points["demographics_focus"] = self.marketing_focus_matrix["customer_demographics"][demo_key]
        
        # 고객 유형별 포인트
        customer_type_key = components.customer_type.value
        if customer_type_key in self.marketing_focus_matrix["customer_type"]:
            focus_points["customer_type_focus"] = self.marketing_focus_matrix["customer_type"][customer_type_key]
        
        return focus_points
