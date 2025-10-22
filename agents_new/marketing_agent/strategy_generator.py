"""
페르소나 기반 마케팅 전략 자동 생성 엔진
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import random


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
    
    async def generate_persona_based_strategies(
        self,
        persona_type: str,
        risk_codes: List[str],
        store_data: Dict[str, Any],
        seasonal_context: Optional[str] = None
    ) -> List[MarketingStrategy]:
        """페르소나 기반 마케팅 전략 생성"""
        strategies = []
        
        # 기본 전략 템플릿에서 선택
        if persona_type in self.strategy_templates:
            for template in self.strategy_templates[persona_type]:
                # 위험 코드 매칭 확인
                if any(risk_code in risk_codes for risk_code in template["risk_codes"]):
                    strategy = MarketingStrategy(
                        strategy_id=f"STRAT_{len(strategies) + 1}",
                        name=template["name"],
                        description=template["description"],
                        target_persona=persona_type,
                        risk_codes=template["risk_codes"],
                        channel=template["channel"],
                        tactics=template["tactics"],
                        expected_impact=template["expected_impact"],
                        implementation_time=template["implementation_time"],
                        budget_estimate=template["budget_estimate"],
                        success_metrics=template["success_metrics"],
                        priority=template["priority"]
                    )
                    strategies.append(strategy)
        
        # 계절적 요소 적용
        if seasonal_context:
            strategies = self._apply_seasonal_factors(strategies, seasonal_context)
        
        # 우선순위 정렬
        strategies.sort(key=lambda x: x.priority)
        
        return strategies
    
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
        
        # 예상 KPI 계산
        expected_kpis = self._calculate_expected_kpis(strategies)
        
        # 성공 확률 계산
        success_probability = self._calculate_success_probability(strategies)
        
        campaign_plan = CampaignPlan(
            campaign_id=campaign_id,
            name=campaign_name,
            description=f"{len(strategies)}개 전략을 포함한 종합 마케팅 캠페인",
            duration=campaign_duration,
            strategies=strategies,
            budget_allocation=budget_allocation,
            timeline=timeline,
            expected_kpis=expected_kpis,
            success_probability=success_probability
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
    
    def _calculate_expected_kpis(self, strategies: List[MarketingStrategy]) -> Dict[str, Any]:
        """예상 KPI 계산"""
        kpis = {
            "매출_증가율": 0,
            "신규_고객_증가율": 0,
            "재방문율_개선": 0,
            "리뷰_점수_개선": 0,
            "SNS_팔로워_증가율": 0
        }
        
        for strategy in strategies:
            if "매출" in strategy.expected_impact:
                kpis["매출_증가율"] += 10
            if "신규" in strategy.expected_impact:
                kpis["신규_고객_증가율"] += 15
            if "재방문" in strategy.expected_impact:
                kpis["재방문율_개선"] += 5
            if "리뷰" in strategy.expected_impact:
                kpis["리뷰_점수_개선"] += 0.5
            if "SNS" in strategy.expected_impact:
                kpis["SNS_팔로워_증가율"] += 20
        
        return kpis
    
    def _calculate_success_probability(self, strategies: List[MarketingStrategy]) -> float:
        """성공 확률 계산"""
        base_probability = 70.0  # 기본 성공 확률
        
        # 전략 수에 따른 조정
        strategy_bonus = min(len(strategies) * 5, 20)
        
        # 우선순위에 따른 조정
        priority_bonus = 0
        for strategy in strategies:
            if strategy.priority == 1:
                priority_bonus += 5
            elif strategy.priority == 2:
                priority_bonus += 3
        
        total_probability = base_probability + strategy_bonus + priority_bonus
        return min(total_probability, 95.0)  # 최대 95%

