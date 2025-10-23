"""
페르소나 기반 마케팅 전략 자동 생성 엔진
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import random
from pathlib import Path


@dataclass
class MarketingStrategy:
    """마케팅 전략 정의"""
    strategy_id: str
    name: str
    description: str
    target_persona: str
    risk_codes: List[str]
    channel: str
    tactics: List[str]
    expected_impact: str
    implementation_time: str
    budget_estimate: str
    success_metrics: List[str]
    priority: int


@dataclass
class CampaignPlan:
    """캠페인 계획 정의"""
    campaign_id: str
    name: str
    description: str
    duration: str
    strategies: List[MarketingStrategy]
    budget_allocation: Dict[str, float]
    timeline: List[Dict[str, Any]]
    expected_kpis: Dict[str, Any]
    success_probability: float


class StrategyGenerator:
    """페르소나 기반 마케팅 전략 자동 생성기"""
    
    def __init__(self):
        self.strategy_templates = self._load_strategy_templates()
        self.channel_strategies = self._load_channel_strategies()
        self.seasonal_factors = self._load_seasonal_factors()
        self.age_channel_insights = self._load_age_channel_insights()
    
    def _load_strategy_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """전략 템플릿 로드"""
        return {
            "도심형_직장인_중식점": [
                {
                    "name": "점심 피크 타임 회복 전략",
                    "description": "점심 시간대 매출 회복을 위한 전략",
                    "risk_codes": ["R2", "R4"],
                    "channel": "오프라인 + 디지털",
                    "tactics": [
                        "11:30-13:30 전용 세트 메뉴 출시 (7,900원)",
                        "오전 11시~12시 네이버 예약 고객 커피 제공",
                        "카카오채널 친구 대상 쿠폰 발송",
                        "직장인 반경 500m 네이버 지도 광고"
                    ],
                    "expected_impact": "점심 매출 15-20% 증가",
                    "implementation_time": "1-2주",
                    "budget_estimate": "월 50-100만원",
                    "success_metrics": ["점심시간 매출", "신규 예약 고객", "재방문율"],
                    "priority": 1
                },
                {
                    "name": "배달 경쟁력 강화 전략",
                    "description": "배달 채널 경쟁력 향상 전략",
                    "risk_codes": ["R5"],
                    "channel": "배달앱",
                    "tactics": [
                        "배달앱 사진 리뉴얼 및 메뉴명 키워드 최적화",
                        "'30분 이내 배달' 문구 강조",
                        "배달 포장 품질 개선 (리뷰별 만족도 연동)",
                        "배달 리뷰 1시간 내 응답 시스템 구축"
                    ],
                    "expected_impact": "배달 매출 10-15% 증가",
                    "implementation_time": "2-3주",
                    "budget_estimate": "월 30-50만원",
                    "success_metrics": ["배달 매출", "배달 리뷰 점수", "취소율"],
                    "priority": 2
                }
            ],
            "감성_카페_여성층": [
                {
                    "name": "SNS 감성 마케팅 전략",
                    "description": "여성 20-30대 타겟 SNS 마케팅 전략",
                    "risk_codes": ["R1", "R7"],
                    "channel": "인스타그램 + 틱톡",
                    "tactics": [
                        "인스타 릴스 15초 영상 제작 ('오늘은 커피 말고 분위기를 마시는 날')",
                        "고객 후기 리그램 이벤트 (리뷰+태그 시 음료 무료쿠폰)",
                        "포토존 인테리어 강화 및 SNS용 해시태그 노출",
                        "틱톡 챌린지 참여 및 인플루언서 협업"
                    ],
                    "expected_impact": "신규 고객 유입 20-25% 증가",
                    "implementation_time": "3-4주",
                    "budget_estimate": "월 80-120만원",
                    "success_metrics": ["SNS 팔로워", "신규 고객", "포토존 이용률"],
                    "priority": 1
                },
                {
                    "name": "네이버지도 리뷰 확보 전략",
                    "description": "지도 노출 최적화 및 리뷰 확보 전략",
                    "risk_codes": ["R1"],
                    "channel": "네이버지도",
                    "tactics": [
                        "네이버지도 리뷰 20건 확보 캠페인",
                        "'데이트 카페', '포토존 카페' 키워드 광고",
                        "고객 체험단 운영 (10명 초대)",
                        "지도 노출 상위 키워드 등록"
                    ],
                    "expected_impact": "지도 유입 30% 증가",
                    "implementation_time": "2-3주",
                    "budget_estimate": "월 40-60만원",
                    "success_metrics": ["지도 유입", "리뷰 수", "평점"],
                    "priority": 2
                }
            ],
            "프랜차이즈_치킨_배달형": [
                {
                    "name": "배달앱 리뷰 관리 전략",
                    "description": "배달 리뷰 관리 및 고객 서비스 강화",
                    "risk_codes": ["R6", "R5"],
                    "channel": "배달앱",
                    "tactics": [
                        "앱리뷰 응대 캠페인: 1시간 내 답변 시스템 구축",
                        "리뷰별 만족도 연동 포장 품질 개선",
                        "배달 시간 단축을 위한 주방 프로세스 최적화",
                        "야식 타겟 21-23시 광고 집중"
                    ],
                    "expected_impact": "취소율 50% 감소, 배달 매출 12% 증가",
                    "implementation_time": "2-3주",
                    "budget_estimate": "월 60-80만원",
                    "success_metrics": ["취소율", "배달 리뷰 점수", "야식 매출"],
                    "priority": 1
                },
                {
                    "name": "포장 고객 유도 전략",
                    "description": "취소율 감소를 위한 포장 고객 유도",
                    "risk_codes": ["R6"],
                    "channel": "오프라인",
                    "tactics": [
                        "2천원 포장할인 프로모션",
                        "포장 고객 전용 메뉴 개발",
                        "포장 대기시간 단축 시스템",
                        "포장 고객 리뷰 이벤트"
                    ],
                    "expected_impact": "포장 매출 25% 증가, 취소율 30% 감소",
                    "implementation_time": "1-2주",
                    "budget_estimate": "월 20-30만원",
                    "success_metrics": ["포장 매출", "취소율", "포장 고객 수"],
                    "priority": 2
                }
            ]
        }
    
    def _load_channel_strategies(self) -> Dict[str, Dict[str, Any]]:
        """채널별 전략 로드"""
        return {
            "인스타그램": {
                "content_types": ["릴스", "스토리", "포스트", "IGTV"],
                "posting_frequency": "일 2-3회",
                "optimal_times": ["오전 9-11시", "오후 7-9시"],
                "hashtag_strategy": "업종 관련 해시태그 + 지역 해시태그",
                "engagement_tactics": ["리그램 이벤트", "스토리 인터랙션", "라이브 방송"]
            },
            "네이버지도": {
                "optimization_focus": ["키워드", "리뷰", "사진", "정보 정확성"],
                "review_strategy": "고객 체험단 + 리뷰 이벤트",
                "photo_strategy": "메뉴 사진 + 분위기 사진",
                "keyword_strategy": "업종 + 지역 + 특성 키워드"
            },
            "배달앱": {
                "menu_optimization": ["사진", "설명", "가격", "카테고리"],
                "delivery_optimization": ["시간", "포장", "서비스"],
                "review_management": ["응답", "개선", "프로모션"],
                "promotion_strategy": ["할인", "쿠폰", "이벤트"]
            },
            "오프라인": {
                "visual_strategy": ["간판", "메뉴판", "인테리어"],
                "service_strategy": ["고객 서비스", "대기시간", "품질"],
                "promotion_strategy": ["할인", "쿠폰", "이벤트"],
                "location_strategy": ["접근성", "주차", "위치"]
            }
        }
    
    def _load_seasonal_factors(self) -> Dict[str, Dict[str, Any]]:
        """계절별 요인 로드"""
        return {
            "봄": {
                "trending_keywords": ["봄 메뉴", "신제품", "벚꽃", "피크닉"],
                "recommended_strategies": ["신제품 출시", "봄 프로모션", "아웃도어 마케팅"],
                "target_segments": ["커플", "가족", "친구"]
            },
            "여름": {
                "trending_keywords": ["시원한", "냉면", "아이스", "여름 메뉴"],
                "recommended_strategies": ["냉음식 강화", "에어컨 강조", "야외 마케팅"],
                "target_segments": ["직장인", "학생", "가족"]
            },
            "가을": {
                "trending_keywords": ["가을 메뉴", "따뜻한", "추천", "단풍"],
                "recommended_strategies": ["가을 신메뉴", "따뜻한 메뉴 강조", "가족 모임 마케팅"],
                "target_segments": ["가족", "커플", "친구"]
            },
            "겨울": {
                "trending_keywords": ["따뜻한", "겨울 메뉴", "연말", "모임"],
                "recommended_strategies": ["따뜻한 메뉴 강조", "연말 프로모션", "모임 마케팅"],
                "target_segments": ["가족", "친구", "동료"]
            }
        }
    
    def _load_age_channel_insights(self) -> Dict[str, Any]:
        """
        연령대별 SNS 채널 인사이트 로드 (data/segment_sns.json)
        
        Returns:
            연령대별 채널 정보 (top 5 채널, 트렌드, 피해야 할 채널)
        """
        try:
            # data/segment_sns.json 경로 찾기
            json_path = Path(__file__).parent.parent.parent / "data" / "segment_sns.json"
            
            if not json_path.exists():
                print(f"[WARNING] segment_sns.json not found at {json_path}")
                return self._get_default_channel_insights()
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 연령대별로 파싱
            age_top5 = data.get("age_top5_channels", {})
            
            insights = {}
            for age_key, channels in age_top5.items():
                # "연령-20대" → "20대" 변환
                age = age_key.replace("연령-", "")
                
                if not channels:
                    continue
                
                # Top 1 채널 (가장 많이 사용)
                top1 = channels[0]
                primary_channel = top1["channel"]
                usage_rate = top1["usage_percent"]
                
                # Top 2 채널 (상승 추세인 경우에만)
                secondary_channel = None
                if len(channels) >= 2:
                    top2 = channels[1]
                    if top2.get("trend_label") in ["대폭 상승", "소폭 상승"]:
                        secondary_channel = top2["channel"]
                
                # 피해야 할 채널 (하락 추세)
                avoid_channels = [
                    ch["channel"] for ch in channels 
                    if ch.get("trend_label") in ["대폭 하락", "소폭 하락"]
                ]
                
                # 전체 채널 정보 (근거 제시용)
                all_channels = [
                    {
                        "rank": ch["rank"],
                        "channel": ch["channel"],
                        "usage_percent": ch["usage_percent"],
                        "trend_label": ch.get("trend_label", ""),
                        "total_change": ch.get("total_change", 0)
                    }
                    for ch in channels[:5]  # Top 5만
                ]
                
                insights[age] = {
                    "primary_channel": primary_channel,
                    "usage_rate": usage_rate,
                    "secondary_channel": secondary_channel,
                    "avoid_channels": avoid_channels,
                    "all_channels": all_channels  # 근거 제시용
                }
            
            return insights
            
        except Exception as e:
            print(f"[ERROR] Failed to load segment_sns.json: {e}")
            return self._get_default_channel_insights()
    
    def _get_default_channel_insights(self) -> Dict[str, Any]:
        """기본 채널 인사이트 (fallback)"""
        return {
            "20대": {
                "primary_channel": "인스타그램",
                "usage_rate": 87.4,
                "secondary_channel": None,
                "avoid_channels": ["카카오스토리", "페이스북"],
                "all_channels": []
            },
            "30대": {
                "primary_channel": "인스타그램",
                "usage_rate": 72.2,
                "secondary_channel": None,
                "avoid_channels": ["카카오스토리"],
                "all_channels": []
            },
            "40대": {
                "primary_channel": "인스타그램",
                "usage_rate": 60.1,
                "secondary_channel": "페이스북",
                "avoid_channels": ["카카오스토리"],
                "all_channels": []
            },
            "50대": {
                "primary_channel": "네이버밴드",
                "usage_rate": 51.2,
                "secondary_channel": "인스타그램",
                "avoid_channels": ["카카오스토리"],
                "all_channels": []
            },
            "60대": {
                "primary_channel": "네이버밴드",
                "usage_rate": 59.8,
                "secondary_channel": "인스타그램",
                "avoid_channels": ["카카오스토리"],
                "all_channels": []
            }
        }
    
    def _select_optimal_channel(self, age_group: str, delivery_ratio: float = 0.0) -> Dict[str, Any]:
        """
        연령대와 배달율을 고려한 최적 채널 선택 (1-2개로 한정) + 근거 제시
        
        Args:
            age_group: 주요 연령대 (20대, 30대, 40대, 50대, 60대, 70대이상)
            delivery_ratio: 배달 비율 (0-100)
            
        Returns:
            {
                "channels": "선택된 채널 (1-2개)",
                "primary_channel": "주 채널",
                "usage_rate": 사용률,
                "reasoning": "추천 근거",
                "avoid_channels": ["피해야 할 채널"],
                "channel_data": [채널별 상세 데이터]
            }
        """
        # 연령대별 인사이트 가져오기
        insights = self.age_channel_insights.get(age_group, self.age_channel_insights.get("30대", {}))
        
        if not insights:
            return {
                "channels": "인스타그램",
                "primary_channel": "인스타그램",
                "usage_rate": 60.0,
                "reasoning": "기본 추천 채널",
                "avoid_channels": [],
                "channel_data": []
            }
        
        primary = insights.get("primary_channel", "인스타그램")
        secondary = insights.get("secondary_channel")
        usage_rate = insights.get("usage_rate", 0)
        avoid_channels = insights.get("avoid_channels", [])
        all_channels = insights.get("all_channels", [])
        
        # 채널 선택 및 근거 생성
        selected_channels = ""
        reasoning = ""
        
        # 배달율이 50% 이상이면 배달앱 우선
        if delivery_ratio >= 50:
            selected_channels = "배달앱 (배달의민족, 쿠팡이츠, 요기요)"
            reasoning = f"{age_group} 고객의 경우 {primary}({usage_rate}%) 사용률이 가장 높지만, 배달 비율이 {delivery_ratio:.1f}%로 높아 배달앱을 최우선 채널로 추천합니다."
            
        # 배달율이 30-50% 사이면 배달앱 + 주 채널
        elif 30 <= delivery_ratio < 50:
            selected_channels = f"배달앱 + {primary}"
            reasoning = f"{age_group} 고객의 {primary} 사용률이 {usage_rate:.1f}%로 가장 높고, 배달 비율({delivery_ratio:.1f}%)도 높아 두 채널을 병행 추천합니다."
            
        # 일반적인 경우: SNS 채널
        else:
            # Secondary 채널이 있고 오프라인 강조가 필요한 경우
            if secondary and delivery_ratio < 20:
                selected_channels = f"{primary} + 오프라인"
                reasoning = f"{age_group} 고객의 {primary} 사용률이 {usage_rate:.1f}%로 가장 높습니다. 배달 비율({delivery_ratio:.1f}%)이 낮아 오프라인 채널도 병행 추천합니다."
            
            # 주 채널 1개만
            else:
                selected_channels = primary
                reasoning = f"{age_group} 고객의 {primary} 사용률이 {usage_rate:.1f}%로 압도적으로 높습니다."
        
        # 피해야 할 채널에 대한 경고 추가
        if avoid_channels:
            avoid_text = ", ".join(avoid_channels[:3])  # 최대 3개만
            reasoning += f"\n⚠️ 주의: {avoid_text}는 사용률 하락 추세이므로 채널로 사용 시 유의하세요."
        
        # 채널 상세 데이터 (그래프 근거용)
        channel_data_with_reasoning = []
        for ch in all_channels:
            trend_emoji = {
                "대폭 상승": "📈",
                "소폭 상승": "↗️",
                "변화 없음": "➡️",
                "소폭 하락": "↘️",
                "대폭 하락": "📉"
            }.get(ch.get("trend_label", ""), "")
            
            channel_data_with_reasoning.append({
                "rank": ch["rank"],
                "channel": ch["channel"],
                "usage_percent": ch["usage_percent"],
                "trend_label": ch.get("trend_label", ""),
                "trend_emoji": trend_emoji,
                "total_change": ch.get("total_change", 0),
                "recommendation": "추천" if ch["channel"] == primary else "피하기" if ch["channel"] in avoid_channels else "보통"
            })
        
        return {
            "channels": selected_channels,
            "primary_channel": primary,
            "usage_rate": usage_rate,
            "reasoning": reasoning,
            "avoid_channels": avoid_channels,
            "channel_data": channel_data_with_reasoning,
            "source": "2024년 미디어통계포털 - 주로 이용하는 SNS 계정 1,2,3위"
        }
    
    def expand_channel_details(self, channel_string: str) -> Dict[str, Any]:
        """채널 문자열을 구체적인 채널 정보로 확장
        
        Args:
            channel_string: "오프라인 + 디지털", "배달앱", "인스타그램 + 틱톡" 등
            
        Returns:
            확장된 채널 정보 딕셔너리
        """
        channel_strategies = self._load_channel_strategies()
        
        # 채널 문자열 파싱
        channels = []
        if "+" in channel_string:
            channels = [ch.strip() for ch in channel_string.split("+")]
        else:
            channels = [channel_string.strip()]
        
        # 매핑 테이블 (템플릿 채널명 → 구체적 채널명)
        channel_mapping = {
            "오프라인": ["오프라인"],
            "디지털": ["인스타그램", "네이버지도", "네이버플레이스", "카카오맵"],
            "배달앱": ["배달앱"],
            "인스타그램": ["인스타그램"],
            "틱톡": ["인스타그램"],  # 틱톡은 인스타그램과 유사한 전략 사용
            "네이버지도": ["네이버지도"],
        }
        
        # 구체적인 채널 리스트 생성
        expanded_channels = []
        for ch in channels:
            if ch in channel_mapping:
                expanded_channels.extend(channel_mapping[ch])
            else:
                expanded_channels.append(ch)
        
        # 중복 제거
        expanded_channels = list(dict.fromkeys(expanded_channels))
        
        # 각 채널의 상세 정보 수집
        result = {
            "online_channels": [],
            "offline_channels": [],
            "details": {}
        }
        
        for ch in expanded_channels:
            if ch in channel_strategies:
                strategy = channel_strategies[ch]
                result["details"][ch] = strategy
                
                # 온라인/오프라인 분류
                if ch == "오프라인":
                    result["offline_channels"].append(ch)
                else:
                    result["online_channels"].append(ch)
            elif ch in ["네이버플레이스", "카카오맵"]:
                # 네이버지도와 유사한 전략 사용
                if "네이버지도" in channel_strategies:
                    result["details"][ch] = channel_strategies["네이버지도"]
                    result["online_channels"].append(ch)
        
        return result
    
    async def generate_persona_based_strategies(
        self,
        persona_type: str,
        risk_codes: List[str],
        store_data: Dict[str, Any],
        seasonal_context: Optional[str] = None
    ) -> List[MarketingStrategy]:
        """페르소나 기반 마케팅 전략 생성"""
        strategies = []
        
        # 연령별 SNS 채널 정보 추출
        target_age_groups = self._extract_target_age_groups(store_data)
        age_channel_recommendations = self._get_age_channel_recommendations(target_age_groups)
        
        # 기본 전략 템플릿에서 선택
        if persona_type in self.strategy_templates:
            for template in self.strategy_templates[persona_type]:
                # 위험 코드 매칭 확인
                if any(risk_code in risk_codes for risk_code in template["risk_codes"]):
                    # 채널 정보 업데이트 (연령별 SNS 채널 반영)
                    updated_channel = self._update_channel_with_age_insights(
                        template["channel"], 
                        age_channel_recommendations
                    )
                    
                    # 전술 업데이트 (연령별 채널 정보 반영)
                    updated_tactics = self._update_tactics_with_age_channels(
                        template["tactics"], 
                        age_channel_recommendations
                    )
                    
                    strategy = MarketingStrategy(
                        strategy_id=f"STRAT_{len(strategies) + 1}",
                        name=template["name"],
                        description=template["description"],
                        target_persona=persona_type,
                        risk_codes=template["risk_codes"],
                        channel=updated_channel,
                        tactics=updated_tactics,
                        expected_impact=template["expected_impact"],
                        implementation_time=template["implementation_time"],
                        budget_estimate=template["budget_estimate"],
                        success_metrics=template["success_metrics"],
                        priority=template["priority"]
                    )
                    strategies.append(strategy)
        
        # 연령별 SNS 전용 전략 추가
        if age_channel_recommendations:
            sns_strategy = self._create_age_based_sns_strategy(
                persona_type, 
                risk_codes, 
                age_channel_recommendations
            )
            if sns_strategy:
                strategies.append(sns_strategy)
        
        # 계절적 요소 적용
        if seasonal_context:
            strategies = self._apply_seasonal_factors(strategies, seasonal_context)
        
        # 우선순위 정렬
        strategies.sort(key=lambda x: x.priority)
        
        return strategies
    
    def _extract_target_age_groups(self, store_data: Dict[str, Any]) -> List[str]:
        """매장 데이터에서 주요 연령대 추출"""
        age_groups = []
        
        # 고객 분석 데이터에서 연령 분포 확인
        customer_analysis = store_data.get("customer_analysis", {})
        age_distribution = customer_analysis.get("age_distribution", {})
        
        # 상위 3개 연령대 추출 (20% 이상인 경우)
        sorted_ages = sorted(
            age_distribution.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for age_group, percentage in sorted_ages[:3]:
            if percentage >= 20.0:  # 20% 이상인 연령대만
                age_groups.append(age_group)
        
        return age_groups
    
    def _get_age_channel_recommendations(self, age_groups: List[str]) -> Dict[str, Any]:
        """연령대별 SNS 채널 추천 정보 생성"""
        recommendations = {}
        
        for age_group in age_groups:
            if age_group in self.age_channel_insights:
                insights = self.age_channel_insights[age_group]
                recommendations[age_group] = {
                    "primary_channel": insights.get("primary_channel"),
                    "secondary_channel": insights.get("secondary_channel"),
                    "usage_rate": insights.get("usage_rate", 0),
                    "avoid_channels": insights.get("avoid_channels", []),
                    "all_channels": insights.get("all_channels", [])
                }
        
        return recommendations
    
    def _update_channel_with_age_insights(self, original_channel: str, age_recommendations: Dict[str, Any]) -> str:
        """기존 채널 정보를 연령별 인사이트로 업데이트"""
        if not age_recommendations:
            return original_channel
        
        # 주요 연령대의 1순위 채널 추출
        primary_channels = []
        for age_data in age_recommendations.values():
            if age_data.get("primary_channel"):
                primary_channels.append(age_data["primary_channel"])
        
        if primary_channels:
            # 중복 제거하고 상위 2개 채널 선택
            unique_channels = list(dict.fromkeys(primary_channels))[:2]
            return f"{original_channel} + {' + '.join(unique_channels)}"
        
        return original_channel
    
    def _update_tactics_with_age_channels(self, original_tactics: List[str], age_recommendations: Dict[str, Any]) -> List[str]:
        """전술을 연령별 채널 정보로 업데이트"""
        if not age_recommendations:
            return original_tactics
        
        updated_tactics = []
        
        for tactic in original_tactics:
            # SNS 관련 전술인 경우 연령별 채널 정보 추가
            if any(keyword in tactic for keyword in ["SNS", "인스타그램", "페이스북", "카카오", "네이버"]):
                # 주요 연령대의 채널 정보 추가
                channel_info = self._format_channel_info_for_tactic(age_recommendations)
                if channel_info:
                    tactic += f" ({channel_info})"
            
            updated_tactics.append(tactic)
        
        return updated_tactics
    
    def _format_channel_info_for_tactic(self, age_recommendations: Dict[str, Any]) -> str:
        """전술용 채널 정보 포맷팅"""
        channel_info_parts = []
        
        for age_group, data in age_recommendations.items():
            primary = data.get("primary_channel")
            usage_rate = data.get("usage_rate", 0)
            
            if primary and usage_rate > 0:
                channel_info_parts.append(f"{age_group} {primary} {usage_rate:.1f}%")
        
        return ", ".join(channel_info_parts) if channel_info_parts else ""
    
    def _create_age_based_sns_strategy(
        self, 
        persona_type: str, 
        risk_codes: List[str], 
        age_recommendations: Dict[str, Any]
    ) -> Optional[MarketingStrategy]:
        """연령별 SNS 채널 기반 전략 생성"""
        if not age_recommendations:
            return None
        
        # 주요 연령대와 채널 정보 추출
        primary_channels = []
        channel_details = []
        
        for age_group, data in age_recommendations.items():
            primary = data.get("primary_channel")
            usage_rate = data.get("usage_rate", 0)
            
            if primary and usage_rate > 0:
                primary_channels.append(primary)
                channel_details.append(f"{age_group}: {primary} ({usage_rate:.1f}%)")
        
        if not primary_channels:
            return None
        
        # 중복 제거
        unique_channels = list(dict.fromkeys(primary_channels))
        
        # 전술 생성
        tactics = [
            f"{unique_channels[0]} 콘텐츠 제작 및 업로드",
            f"고객 후기 리그램 및 해시태그 캠페인",
            f"매장 포토존 인테리어 강화"
        ]
        
        if len(unique_channels) > 1:
            tactics.append(f"{unique_channels[1]} 크로스 프로모션")
        
        tactics.append(f"연령별 채널 분석: {', '.join(channel_details)}")
        
        return MarketingStrategy(
            strategy_id=f"STRAT_SNS_{len(age_recommendations)}",
            name="연령별 SNS 타겟팅 전략",
            description=f"주요 연령대({', '.join(age_recommendations.keys())})의 선호 채널을 활용한 SNS 마케팅 전략",
            target_persona=persona_type,
            risk_codes=risk_codes,
            channel=f"{' + '.join(unique_channels)}",
            tactics=tactics,
            expected_impact="SNS 팔로워 및 참여도 20-30% 증가",
            implementation_time="2-3주",
            budget_estimate="월 30-50만원",
            success_metrics=["SNS 팔로워 수", "게시물 참여도", "매장 방문 전환율"],
            priority=2
        )
    
    def _apply_seasonal_factors(self, strategies: List[MarketingStrategy], season: str) -> List[MarketingStrategy]:
        """계절적 요소 적용"""
        if season not in self.seasonal_factors:
            return strategies
        
        seasonal_data = self.seasonal_factors[season]
        
        for strategy in strategies:
            # 전술에 계절적 키워드 추가
            for i, tactic in enumerate(strategy.tactics):
                if any(keyword in tactic for keyword in seasonal_data["trending_keywords"]):
                    continue  # 이미 계절적 요소가 포함됨
                
                # 계절적 요소 추가
                if "메뉴" in tactic:
                    strategy.tactics[i] = tactic.replace("메뉴", f"{season} 메뉴")
        
        return strategies
    
    async def generate_tactics(
        self,
        strategy: MarketingStrategy,
        store_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """전략별 구체적 전술 생성"""
        tactics = []
        
        for tactic_description in strategy.tactics:
            tactic = {
                "description": tactic_description,
                "implementation_steps": self._generate_implementation_steps(tactic_description),
                "required_resources": self._estimate_resources(tactic_description),
                "timeline": self._estimate_timeline(tactic_description),
                "success_criteria": self._define_success_criteria(tactic_description),
                "risk_factors": self._identify_risk_factors(tactic_description)
            }
            tactics.append(tactic)
        
        return tactics
    
    def _generate_implementation_steps(self, tactic_description: str) -> List[str]:
        """전술별 구현 단계 생성"""
        steps = []
        
        if "세트 메뉴" in tactic_description:
            steps = [
                "메뉴 기획 및 가격 책정",
                "재료비 및 원가 계산",
                "메뉴판 디자인 및 제작",
                "직원 교육 및 훈련",
                "프로모션 시작 및 모니터링"
            ]
        elif "SNS" in tactic_description:
            steps = [
                "콘텐츠 기획 및 스토리보드 작성",
                "촬영 및 편집",
                "해시태그 및 캡션 작성",
                "업로드 및 스케줄링",
                "반응 모니터링 및 분석"
            ]
        elif "리뷰" in tactic_description:
            steps = [
                "리뷰 관리 시스템 구축",
                "고객 대상 리뷰 이벤트 안내",
                "리뷰 응답 템플릿 작성",
                "리뷰 모니터링 시작",
                "개선사항 도출 및 적용"
            ]
        else:
            steps = [
                "전술 상세 계획 수립",
                "필요 자원 확보",
                "실행 일정 수립",
                "실행 및 모니터링",
                "결과 분석 및 개선"
            ]
        
        return steps
    
    def _estimate_resources(self, tactic_description: str) -> Dict[str, Any]:
        """필요 자원 추정"""
        resources = {
            "human_resources": [],
            "budget": "미정",
            "tools": [],
            "time_required": "미정"
        }
        
        if "세트 메뉴" in tactic_description:
            resources["human_resources"] = ["메뉴 기획자", "주방장", "디자이너"]
            resources["budget"] = "10-20만원"
            resources["tools"] = ["메뉴 기획 도구", "디자인 소프트웨어"]
            resources["time_required"] = "1-2주"
        elif "SNS" in tactic_description:
            resources["human_resources"] = ["콘텐츠 기획자", "촬영 담당자", "편집자"]
            resources["budget"] = "30-50만원"
            resources["tools"] = ["촬영 장비", "편집 소프트웨어"]
            resources["time_required"] = "2-3주"
        elif "리뷰" in tactic_description:
            resources["human_resources"] = ["고객 서비스 담당자"]
            resources["budget"] = "5-10만원"
            resources["tools"] = ["리뷰 관리 시스템"]
            resources["time_required"] = "1주"
        
        return resources
    
    def _estimate_timeline(self, tactic_description: str) -> Dict[str, str]:
        """타임라인 추정"""
        timeline = {
            "planning": "1-2일",
            "preparation": "3-5일",
            "execution": "1-2주",
            "monitoring": "지속적"
        }
        
        if "세트 메뉴" in tactic_description:
            timeline["preparation"] = "1-2주"
            timeline["execution"] = "1개월"
        elif "SNS" in tactic_description:
            timeline["preparation"] = "1주"
            timeline["execution"] = "2-3주"
        
        return timeline
    
    def _define_success_criteria(self, tactic_description: str) -> List[str]:
        """성공 기준 정의"""
        criteria = []
        
        if "세트 메뉴" in tactic_description:
            criteria = [
                "세트 메뉴 주문률 30% 이상",
                "점심시간 매출 15% 증가",
                "고객 만족도 4.5점 이상"
            ]
        elif "SNS" in tactic_description:
            criteria = [
                "팔로워 수 20% 증가",
                "게시물 참여율 5% 이상",
                "웹사이트 트래픽 25% 증가"
            ]
        elif "리뷰" in tactic_description:
            criteria = [
                "리뷰 수 50% 증가",
                "평균 평점 0.5점 향상",
                "리뷰 응답률 90% 이상"
            ]
        
        return criteria
    
    def _identify_risk_factors(self, tactic_description: str) -> List[str]:
        """위험 요소 식별"""
        risks = []
        
        if "세트 메뉴" in tactic_description:
            risks = [
                "재료비 상승으로 인한 수익성 악화",
                "메뉴 복잡도 증가로 인한 서비스 품질 하락",
                "고객 반응 부족"
            ]
        elif "SNS" in tactic_description:
            risks = [
                "콘텐츠 품질 부족으로 인한 브랜드 이미지 훼손",
                "SNS 알고리즘 변경으로 인한 노출 감소",
                "부정적 댓글 및 리뷰 증가"
            ]
        elif "리뷰" in tactic_description:
            risks = [
                "부정적 리뷰 증가",
                "리뷰 조작 의혹",
                "고객 서비스 부담 증가"
            ]
        
        return risks
    
    async def generate_campaign_plan(
        self,
        strategies: List[MarketingStrategy],
        store_data: Dict[str, Any],
        campaign_duration: str = "1개월"
    ) -> CampaignPlan:
        """통합 캠페인 계획 생성"""
        campaign_id = f"CAMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        campaign_name = f"{store_data.get('store_name', '매장')} 마케팅 캠페인"
        
        # 예산 배분 계산
        budget_allocation = self._calculate_budget_allocation(strategies)
        
        # 타임라인 생성
        timeline = self._generate_campaign_timeline(strategies, campaign_duration)
        
        campaign_plan = CampaignPlan(
            campaign_id=campaign_id,
            name=campaign_name,
            description=f"{len(strategies)}개 전략을 포함한 종합 마케팅 캠페인",
            duration=campaign_duration,
            strategies=strategies,
            budget_allocation=budget_allocation,
            timeline=timeline,
            expected_kpis={},
            success_probability=0.0
        )
        
        return campaign_plan
    
    def _calculate_budget_allocation(self, strategies: List[MarketingStrategy]) -> Dict[str, float]:
        """예산 배분 계산"""
        total_budget = 0
        channel_budget = {}
        
        for strategy in strategies:
            # 예산 추정 (간단한 추정)
            budget_text = strategy.budget_estimate
            budget_amount = self._extract_budget_amount(budget_text)
            total_budget += budget_amount
            
            channel = strategy.channel
            if channel not in channel_budget:
                channel_budget[channel] = 0
            channel_budget[channel] += budget_amount
        
        # 비율로 변환
        if total_budget > 0:
            for channel in channel_budget:
                channel_budget[channel] = (channel_budget[channel] / total_budget) * 100
        
        return channel_budget
    
    def _extract_budget_amount(self, budget_text: str) -> float:
        """예산 텍스트에서 금액 추출"""
        # 간단한 추정 (실제로는 더 정교한 파싱 필요)
        if "50-100만원" in budget_text:
            return 75
        elif "30-50만원" in budget_text:
            return 40
        elif "80-120만원" in budget_text:
            return 100
        elif "40-60만원" in budget_text:
            return 50
        elif "60-80만원" in budget_text:
            return 70
        elif "20-30만원" in budget_text:
            return 25
        elif "5-10만원" in budget_text:
            return 7.5
        else:
            return 50  # 기본값
    
    def _generate_campaign_timeline(self, strategies: List[MarketingStrategy], duration: str) -> List[Dict[str, Any]]:
        """캠페인 타임라인 생성"""
        timeline = []
        current_date = datetime.now()
        
        for i, strategy in enumerate(strategies):
            timeline.append({
                "week": i + 1,
                "strategy_name": strategy.name,
                "activities": strategy.tactics[:2],  # 상위 2개 전술만
                "milestones": [
                    f"{strategy.name} 기획 완료",
                    f"{strategy.name} 실행 시작",
                    f"{strategy.name} 중간 점검"
                ],
                "expected_deliverables": [
                    f"{strategy.name} 결과 보고서",
                    f"{strategy.name} 개선 방안"
                ]
            })
        
        return timeline

