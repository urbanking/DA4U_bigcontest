"""
Marketing Agent - 페르소나 기반 마케팅 전략 에이전트
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from enum import Enum
try:
    # 패키지로 실행될 때
    from .persona_engine import PersonaEngine, PersonaComponents
    from .risk_analyzer import RiskAnalyzer
    from .strategy_generator import StrategyGenerator, MarketingStrategy, CampaignPlan
except ImportError:
    # 독립 실행될 때
    from persona_engine import PersonaEngine, PersonaComponents
    from risk_analyzer import RiskAnalyzer
    from strategy_generator import StrategyGenerator, MarketingStrategy, CampaignPlan


def convert_enums_to_json_serializable(obj: Any) -> Any:
    """
    재귀적으로 모든 Enum 객체를 JSON 직렬화 가능한 형태로 변환
    
    Args:
        obj: 변환할 객체 (dict, list, Enum 등)
        
    Returns:
        JSON 직렬화 가능한 객체
    """
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {key: convert_enums_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_enums_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_enums_to_json_serializable(item) for item in obj)
    elif hasattr(obj, '__dict__'):
        # dataclass나 일반 객체의 경우
        return {key: convert_enums_to_json_serializable(value) 
                for key, value in obj.__dict__.items() if not key.startswith('_')}
    else:
        return obj


class marketingagent:
    """페르소나 기반 마케팅 전략 에이전트"""
    
    def __init__(self, store_code: str):
        self.store_code = store_code
        self.persona_engine = PersonaEngine()
        self.risk_analyzer = RiskAnalyzer()
        self.strategy_generator = StrategyGenerator()
    
    async def run_marketing(
        self,
        store_report: Dict[str, Any],
        diagnostic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """마케팅 전략 생성 - 이미지의 User Flow 구현"""
        try:
            # Step 1: 페르소나 분석
            persona_analysis = await self.persona_engine.analyze_store_persona(store_report)
            if persona_analysis.get("error"):
                return {
                    "store_code": self.store_code,
                    "error": persona_analysis["error"],
                    "strategies": [],
                    "target_segments": [],
                    "kpi_estimates": {}
                }
            
            persona_components = persona_analysis["components"]
            
            # Step 2: 위험 분석 (페르소나 생성 전에 먼저 수행)
            metrics_data = self._extract_metrics_data(store_report, diagnostic)
            risk_analysis = await self.risk_analyzer.analyze_risks(store_report, metrics_data)
            detected_risk_codes = [risk["code"] for risk in risk_analysis["detected_risks"]]
            
            # Step 3: 페르소나 분류 (동적 생성, 위험 코드 포함)
            persona_type, persona_template = await self.persona_engine.classify_persona(
                persona_components=persona_components,
                store_data=store_report,
                risk_codes=detected_risk_codes
            )
            
            # Step 4: 마케팅 전략 생성
            # 동적 페르소나에 전략이 있는 경우 우선 사용
            if persona_template.get("is_dynamic", False) and persona_template.get("strategies"):
                strategies = self._convert_dynamic_strategies_to_objects(persona_template["strategies"])
            else:
                strategies = await self.strategy_generator.generate_persona_based_strategies(
                    persona_type=persona_type,
                    risk_codes=detected_risk_codes,
                    store_data=store_report,
                    seasonal_context=self._get_seasonal_context()
                )
            
            # Step 5: 캠페인 계획 생성
            campaign_plan = await self.strategy_generator.generate_campaign_plan(
                strategies=strategies,
                store_data=store_report,
                campaign_duration="1개월"
            )
            
            # Step 6: 마케팅 포인트 추출
            marketing_focus_points = self.persona_engine.get_marketing_focus_points(
                persona_type, persona_components
            )
            
            # Step 7: 핵심 인사이트 데이터 생성
            core_insights = self._generate_core_insights(
                persona_type, persona_template, persona_components, 
                risk_analysis, store_report
            )
            
            # Step 8: SNS 포스트 및 프로모션 문구 생성
            social_content = await self._generate_social_content(
                persona_type, persona_template, strategies, store_report
            )
            
            # Step 8.5: 최적 채널 추천 (데이터 기반)
            main_age = persona_components.main_customer_age  # "20대", "30대" 등
            delivery_ratio_text = persona_components.delivery_ratio  # "높음", "중간", "낮음"
            
            # 배달율을 숫자로 변환
            delivery_ratio_numeric = {
                "높음": 60.0,
                "중간": 40.0,
                "낮음": 15.0
            }.get(delivery_ratio_text, 40.0)
            
            # segment_sns.json 기반 채널 추천
            channel_recommendation = self.strategy_generator._select_optimal_channel(
                age_group=main_age,
                delivery_ratio=delivery_ratio_numeric
            )
            
            # Step 9: 결과 통합
            result = {
                "store_code": self.store_code,
                "analysis_timestamp": datetime.now().isoformat(),
                "persona_analysis": {
                    "persona_type": persona_type,
                    "persona_description": persona_template["description"],
                    "components": {
                        "industry": persona_components.industry.value,
                        "commercial_zone": persona_components.commercial_zone.value,
                        "is_franchise": persona_components.is_franchise,
                        "store_age": persona_components.store_age.value,
                        "customer_demographics": {
                            "gender": persona_components.main_customer_gender,
                            "age": persona_components.main_customer_age
                        },
                        "customer_type": persona_components.customer_type.value,
                        "trends": {
                            "new_customer": persona_components.new_customer_trend,
                            "revisit": persona_components.revisit_trend
                        },
                        "delivery_ratio": persona_components.delivery_ratio
                    },
                    "marketing_tone": persona_template.get("marketing_tone", ""),
                    "key_channels": persona_template.get("key_channels", []),
                    "core_insights": core_insights
                },
                "risk_analysis": {
                    "overall_risk_level": risk_analysis["overall_risk_level"].value if hasattr(risk_analysis["overall_risk_level"], 'value') else str(risk_analysis["overall_risk_level"]),
                    "detected_risks": [
                        {
                            **risk,
                            "level": risk["level"].value if hasattr(risk["level"], 'value') else str(risk["level"])
                        }
                        for risk in risk_analysis["detected_risks"]
                    ],
                    "analysis_summary": risk_analysis["analysis_summary"]
                },
                "marketing_strategies": [
                    {
                        "strategy_id": strategy.strategy_id,
                        "name": strategy.name,
                        "description": strategy.description,
                        "risk_codes": strategy.risk_codes,
                        "channel": strategy.channel,
                        "tactics": strategy.tactics,
                        "expected_impact": strategy.expected_impact,
                        "implementation_time": strategy.implementation_time,
                        "budget_estimate": strategy.budget_estimate,
                        "success_metrics": strategy.success_metrics,
                        "priority": strategy.priority
                    }
                    for strategy in strategies
                ],
                "campaign_plan": {
                    "campaign_id": campaign_plan.campaign_id,
                    "name": campaign_plan.name,
                    "description": campaign_plan.description,
                    "duration": campaign_plan.duration,
                    "budget_allocation": campaign_plan.budget_allocation,
                    "timeline": campaign_plan.timeline,
                    "expected_kpis": campaign_plan.expected_kpis,
                    "success_probability": campaign_plan.success_probability
                },
                "channel_recommendation": channel_recommendation,  # 데이터 기반 채널 추천
                "marketing_focus_points": marketing_focus_points,
                "social_content": social_content,  # SNS 포스트 및 프로모션 문구
                "recommendations": self._generate_recommendations(
                    persona_type, detected_risk_codes, strategies
                )
            }
            
            # 구조화된 출력 텍스트 추가
            result["formatted_output"] = self.format_marketing_output(result)
            
            # 🔥 모든 Enum을 JSON 직렬화 가능한 형태로 변환
            result = convert_enums_to_json_serializable(result)
            
            return result
            
        except Exception as e:
            logging.error(f"Error running marketing analysis for {self.store_code}: {e}")
            
            # API 할당량 초과 등의 오류 시에도 기본 데이터 반환
            return {
                "store_code": self.store_code,
                "analysis_timestamp": datetime.now().isoformat(),
                "persona_analysis": {
                    "persona_type": "기본_매장",
                    "persona_description": "기본 매장 페르소나",
                    "components": {
                        "industry": "외식업",
                        "commercial_zone": "상업지역",
                        "is_franchise": False,
                        "store_age": "신규",
                        "customer_demographics": {
                            "gender": "남성",
                            "age": "30대"
                        },
                        "customer_type": "일반고객",
                        "trends": {
                            "new_customer": "증가",
                            "revisit": "안정"
                        },
                        "delivery_ratio": "50%"
                    },
                    "marketing_tone": "친근한",
                    "key_channels": ["온라인", "오프라인"],
                    "core_insights": {
                        "persona": {
                            "summary": "기본 매장 페르소나입니다.",
                            "table_data": {
                                "업종": "외식업",
                                "상권": "상업지역",
                                "프랜차이즈 여부": "N",
                                "신규·노점 여부": "신규",
                                "주요 고객": "남성 30대",
                                "고객유형": "일반고객",
                                "고객관계": "신규유입증가 / 재방문안정",
                                "배달비중": "50%"
                            }
                        },
                        "risk_diagnosis": {
                            "summary": "현재 파악된 위험 요소는 없습니다.",
                            "table_data": [],
                            "overall_risk_level": "LOW"
                        }
                    }
                },
                "risk_analysis": {
                    "overall_risk_level": "LOW",
                    "detected_risks": [],
                    "analysis_summary": "기본 분석"
                },
                "marketing_strategies": [
                    {
                        "strategy_id": "default_1",
                        "name": "기본 마케팅 전략",
                        "description": "고객 유입 증대를 위한 기본적인 마케팅 전략",
                        "risk_codes": [],
                        "channel": "온라인",
                        "tactics": ["SNS 홍보", "온라인 광고"],
                        "expected_impact": "중간",
                        "implementation_time": "1주",
                        "budget_estimate": "100만원",
                        "success_metrics": ["방문객 증가", "매출 증대"],
                        "priority": "높음"
                    }
                ],
                "campaign_plan": {
                    "campaign_id": "default_campaign",
                    "name": "기본 캠페인",
                    "description": "매장 홍보를 위한 기본 캠페인",
                    "duration": "1개월",
                    "budget_allocation": {"온라인": "70%", "오프라인": "30%"},
                    "timeline": [{"주차": "1주", "활동": "SNS 홍보 시작"}],
                    "expected_kpis": {"방문객": "20% 증가", "매출": "15% 증가"},
                    "success_probability": "중간"
                },
                "marketing_focus_points": ["고객 유입", "브랜드 인지도"],
                "social_content": {
                    "instagram_posts": [
                        {
                            "title": "매장 소개",
                            "content": "안녕하세요! 저희 매장을 소개합니다. 🏪✨ #매장소개 #홍보",
                            "hashtags": ["#매장소개", "#홍보", "#맛집"],
                            "post_type": "feed"
                        }
                    ],
                    "facebook_posts": [
                        {
                            "title": "매장 오픈",
                            "content": "새로운 매장이 오픈했습니다! 많은 관심 부탁드립니다.",
                            "call_to_action": "지금 방문하세요!"
                        }
                    ],
                    "promotion_texts": [
                        {
                            "type": "배너",
                            "title": "특별 할인",
                            "content": "오늘만 특별 할인! 놓치지 마세요!",
                            "discount": "20% 할인"
                        }
                    ]
                },
                "recommendations": ["고객 서비스 개선", "마케팅 활동 강화"]
            }
    
    def _extract_metrics_data(self, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> Dict[str, Any]:
        """매장 리포트와 진단 데이터에서 지표 추출 - 실제 Store Agent 데이터 구조 기반"""
        metrics_data = {}
        
        # Store Agent 데이터 구조에서 실제 지표 추출
        customer_analysis = store_report.get("customer_analysis", {})
        sales_analysis = store_report.get("sales_analysis", {})
        industry_analysis = store_report.get("industry_analysis", {})
        
        # 1. 재방문율 (실제 데이터)
        customer_type_analysis = customer_analysis.get("customer_type_analysis", {})
        returning_customers = customer_type_analysis.get("returning_customers", {})
        revisit_rate = returning_customers.get("ratio", 0)
        
        # 2. 신규 고객 비율 (실제 데이터)
        new_customers = customer_type_analysis.get("new_customers", {})
        new_customer_ratio = new_customers.get("ratio", 0)
        new_customer_trend = new_customers.get("trend", "안정 추세")
        
        # 3. 배달 비율 (업종 평균)
        delivery_analysis = industry_analysis.get("delivery_analysis", {})
        delivery_ratio = delivery_analysis.get("average_delivery_ratio", 0)
        
        # 4. 취소율 (업종 평균 - 실제 매장 취소율은 별도 계산 필요)
        cancellation_rate = 0  # 실제 취소율 데이터가 없으므로 0으로 설정
        
        # 5. 매출 트렌드 분석
        sales_trends = sales_analysis.get("trends", {})
        sales_amount_trend = sales_trends.get("sales_amount", {}).get("trend", "안정 추세")
        sales_count_trend = sales_trends.get("sales_count", {}).get("trend", "안정 추세")
        
        # 6. 고객 성장률 (고유 고객 트렌드)
        unique_customers_trend = sales_trends.get("unique_customers", {}).get("trend", "안정 추세")
        
        # 실제 데이터로 업데이트
        metrics_data.update({
            "revisit_rate": revisit_rate,
            "delivery_ratio": delivery_ratio,
            "new_customer_ratio": new_customer_ratio,
            "new_customer_trend": new_customer_trend,
            "cancellation_rate": cancellation_rate,
            "sales_amount_trend": sales_amount_trend,
            "sales_count_trend": sales_count_trend,
            "unique_customers_trend": unique_customers_trend,
            "market_fit_score": 0,  # 계산 필요
            "business_churn_risk": 0  # 계산 필요
        })
        
        # 진단 데이터에서 지표 추출 (기존 로직 유지)
        if "diagnostic_results" in diagnostic:
            diag_results = diagnostic["diagnostic_results"]
            metrics_data.update({
                "sales_slump_days": diag_results.get("sales_slump_days", 0),
                "short_term_sales_drop": diag_results.get("short_term_sales_drop", 0),
                "delivery_sales_drop": diag_results.get("delivery_sales_drop", 0),
                "core_age_gap": diag_results.get("core_age_gap", 0)
            })
        
        # market_fit_score와 business_churn_risk 계산
        metrics_data["market_fit_score"] = self._calculate_market_fit_score(store_report, diagnostic)
        metrics_data["business_churn_risk"] = self._calculate_business_churn_risk(store_report, diagnostic)
        
        return metrics_data
    
    def _calculate_market_fit_score(self, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> float:
        """시장 적합도 점수 계산 - 실제 Store Agent 데이터 구조 기반"""
        try:
            # 실제 Store Agent 데이터 구조에서 추출
            customer_analysis = store_report.get("customer_analysis", {})
            sales_analysis = store_report.get("sales_analysis", {})
            
            # 재방문 고객 비율 (실제 데이터)
            customer_type_analysis = customer_analysis.get("customer_type_analysis", {})
            returning_customers = customer_type_analysis.get("returning_customers", {})
            revisit_rate = returning_customers.get("ratio", 0)
            
            # 신규 고객 비율 (실제 데이터)
            new_customers = customer_type_analysis.get("new_customers", {})
            new_customer_ratio = new_customers.get("ratio", 0)
            
            # 매출 트렌드 분석
            sales_trends = sales_analysis.get("trends", {})
            sales_amount_trend = sales_trends.get("sales_amount", {}).get("trend", "안정 추세")
            sales_count_trend = sales_trends.get("sales_count", {}).get("trend", "안정 추세")
            unique_customers_trend = sales_trends.get("unique_customers", {}).get("trend", "안정 추세")
            
            # 시장 적합도 점수 계산 (가중치 적용)
            score = 0.0
            
            # 1. 재방문 고객 비율 (40% 가중치) - 실제 데이터 기반
            if revisit_rate > 50:
                score += 40
            elif revisit_rate > 30:
                score += 30
            elif revisit_rate > 20:
                score += 20
            elif revisit_rate > 10:
                score += 10
            else:
                score += 0  # 재방문율이 매우 낮음
            
            # 2. 신규 고객 비율 (20% 가중치) - 적절한 수준이 좋음
            if 10 <= new_customer_ratio <= 30:
                score += 20
            elif 5 <= new_customer_ratio <= 40:
                score += 15
            elif new_customer_ratio > 40:
                score += 10  # 너무 높으면 불안정
            else:
                score += 5   # 너무 낮으면 성장성 부족
            
            # 3. 매출 트렌드 (20% 가중치)
            if sales_amount_trend == "상승 추세":
                score += 20
            elif sales_amount_trend == "안정 추세":
                score += 15
            elif sales_amount_trend == "하락 추세":
                score += 5
            
            # 4. 고객 트렌드 (20% 가중치)
            if unique_customers_trend == "상승 추세":
                score += 20
            elif unique_customers_trend == "안정 추세":
                score += 15
            elif unique_customers_trend == "하락 추세":
                score += 5
            
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"[WARNING] Market fit score calculation failed: {e}")
            # 기본값 반환 (데이터가 없는 경우)
            return 50.0
    
    def _calculate_business_churn_risk(self, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> float:
        """상권 해지 위험도 계산 - 실제 Store Agent 데이터 구조 기반"""
        try:
            # 실제 Store Agent 데이터 구조에서 추출
            commercial_area_analysis = store_report.get("commercial_area_analysis", {})
            industry_analysis = store_report.get("industry_analysis", {})
            sales_analysis = store_report.get("sales_analysis", {})
            
            # 해지 위험도 점수 (0-100, 높을수록 위험)
            risk_score = 0.0
            
            # 1. 상권 해지율 (30% 가중치)
            termination_analysis = commercial_area_analysis.get("termination_analysis", {})
            termination_ratio = termination_analysis.get("termination_ratio", 0)
            if termination_ratio > 15:
                risk_score += 30
            elif termination_ratio > 10:
                risk_score += 25
            elif termination_ratio > 5:
                risk_score += 15
            elif termination_ratio > 3:
                risk_score += 10
            
            # 2. 업종 해지율 (25% 가중치)
            industry_termination = industry_analysis.get("termination_analysis", {})
            industry_termination_ratio = industry_termination.get("termination_ratio", 0)
            if industry_termination_ratio > 20:
                risk_score += 25
            elif industry_termination_ratio > 15:
                risk_score += 20
            elif industry_termination_ratio > 10:
                risk_score += 15
            elif industry_termination_ratio > 5:
                risk_score += 10
            
            # 3. 매출 트렌드 (25% 가중치)
            sales_trends = sales_analysis.get("trends", {})
            sales_amount_trend = sales_trends.get("sales_amount", {}).get("trend", "안정 추세")
            if sales_amount_trend == "하락 추세":
                risk_score += 25
            elif sales_amount_trend == "안정 추세":
                risk_score += 10
            elif sales_amount_trend == "상승 추세":
                risk_score += 0
            
            # 4. 고객 트렌드 (20% 가중치)
            unique_customers_trend = sales_trends.get("unique_customers", {}).get("trend", "안정 추세")
            if unique_customers_trend == "하락 추세":
                risk_score += 20
            elif unique_customers_trend == "안정 추세":
                risk_score += 8
            elif unique_customers_trend == "상승 추세":
                risk_score += 0
            
            return min(100, max(0, risk_score))
            
        except Exception as e:
            print(f"[WARNING] Business churn risk calculation failed: {e}")
            # 기본값 반환 (데이터가 없는 경우)
            return 30.0
    
    def _get_seasonal_context(self) -> str:
        """계절적 컨텍스트 반환"""
        current_month = datetime.now().month
        
        if current_month in [3, 4, 5]:
            return "봄"
        elif current_month in [6, 7, 8]:
            return "여름"
        elif current_month in [9, 10, 11]:
            return "가을"
        else:
            return "겨울"
    
    def _generate_recommendations(
        self, 
        persona_type: str, 
        risk_codes: List[str], 
        strategies: List[MarketingStrategy]
    ) -> Dict[str, Any]:
        """추천사항 생성"""
        recommendations = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_strategy": [],
            "success_factors": []
        }
        
        # 즉시 실행 가능한 액션
        if strategies:
            immediate_strategy = strategies[0]  # 우선순위 1 전략
            recommendations["immediate_actions"] = [
                f"즉시 실행: {immediate_strategy.name}",
                f"예상 효과: {immediate_strategy.expected_impact}",
                f"예산: {immediate_strategy.budget_estimate}",
                f"구현 기간: {immediate_strategy.implementation_time}"
            ]
        
        # 단기 목표
        recommendations["short_term_goals"] = [
            "위험 코드 해결을 위한 단계적 접근",
            "페르소나별 맞춤 마케팅 채널 최적화",
            "고객 만족도 및 리뷰 점수 개선"
        ]
        
        # 장기 전략
        recommendations["long_term_strategy"] = [
            "브랜드 이미지 및 고객 충성도 구축",
            "지속 가능한 성장 모델 수립",
            "시장 경쟁력 강화 및 차별화"
        ]
        
        # 성공 요인
        recommendations["success_factors"] = [
            "페르소나 기반 맞춤형 접근",
            "데이터 기반 의사결정",
            "지속적인 모니터링 및 개선",
            "고객 피드백 반영"
        ]
        
        return recommendations
    
    def _generate_core_insights(
        self,
        persona_type: str,
        persona_template: Dict[str, Any],
        persona_components: PersonaComponents,
        risk_analysis: Dict[str, Any],
        store_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """핵심 인사이트 데이터 생성"""
        
        # 페르소나 섹션
        persona_section = {
            "summary": f"이 가게는 {persona_components.main_customer_gender}이 높고, {persona_components.main_customer_age}가 주를 이루고 있고, 유동인구가 많은 \"{persona_type}\"형 가게입니다",
            "table_data": {
                "업종": persona_components.industry.value,
                "상권": persona_components.commercial_zone.value,
                "프랜차이즈 여부": "Y" if persona_components.is_franchise else "N",
                "신규·노점 여부": persona_components.store_age.value,
                "주요 고객": f"{persona_components.main_customer_gender} {persona_components.main_customer_age}",
                "고객유형": persona_components.customer_type.value,
                "고객관계": f"신규유입{persona_components.new_customer_trend} / 재방문{persona_components.revisit_trend}",
                "배달비중": persona_components.delivery_ratio
            },
            "charts": {
                "customer_demographics": {
                    "type": "gender_age_distribution",
                    "title": "성별 & 연령 분포",
                    "description": "고객 분석 결과에서 가져온 성별 및 연령대별 분포",
                    "source": "store_analysis - customer_analysis",
                    "data": {
                        "gender": persona_components.main_customer_gender,
                        "age": persona_components.main_customer_age
                    }
                },
                "customer_trends": {
                    "type": "new_returning_pie",
                    "title": "신규 유입 & 재방문 파이 차트",
                    "description": "신규 고객과 재방문 고객의 비율",
                    "source": "store_analysis - customer_trends",
                    "data": {
                        "new_customer": persona_components.new_customer_trend,
                        "revisit": persona_components.revisit_trend
                    }
                }
            }
        }
        
        # 위험 진단 섹션
        detected_risks = risk_analysis.get("detected_risks", [])
        risk_count = len(detected_risks)
        
        if risk_count > 0:
            risk_codes = [risk["code"] for risk in detected_risks]
            risk_descriptions = [risk["description"] for risk in detected_risks]
            risk_summary = f"이 가게에서 파악된 위험 요소는 {', '.join(risk_descriptions)}로 {risk_count}개의 요소가 있습니다"
        else:
            risk_summary = "현재 파악된 위험 요소는 없습니다. 페르소나에 기반한 타겟팅 마케팅 전략을 도출합니다."
        
        # 위험 코드별 상세 정보 (그래프 매핑 포함)
        risk_code_info = {
            "R1": {
                "meaning": "신규유입 급감",
                "chart_type": "new_customer_trend",
                "chart_title": "신규 유입 추세 (전 분기 대비)",
                "chart_description": "신규 고객 유입률이 급격히 감소하고 있습니다"
            },
            "R2": {
                "meaning": "업종평균 대비 낮은 재방문율",
                "chart_type": "revisit_comparison",
                "chart_title": "재방문율 비교 (업종 평균 vs 가게)",
                "chart_description": "업종 평균 대비 재방문율이 낮습니다"
            },
            "R3": {
                "meaning": "장기매출침체",
                "chart_type": "sales_trend",
                "chart_title": "장기 매출 추세",
                "chart_description": "장기간 매출이 정체 또는 감소하고 있습니다"
            },
            "R4": {
                "meaning": "단기매출하락",
                "chart_type": "sales_trend",
                "chart_title": "단기 매출 추세",
                "chart_description": "단기간 매출이 급격히 하락하고 있습니다"
            },
            "R5": {
                "meaning": "배달매출하락",
                "chart_type": "delivery_trend",
                "chart_title": "배달 매출 추세",
                "chart_description": "배달 매출이 감소하고 있습니다"
            },
            "R6": {
                "meaning": "취소율 급등",
                "chart_type": "cancellation_trend",
                "chart_title": "취소율 추세",
                "chart_description": "주문 취소율이 급격히 증가하고 있습니다"
            },
            "R7": {
                "meaning": "핵심연령괴리",
                "chart_type": "age_distribution",
                "chart_title": "연령대별 분포",
                "chart_description": "핵심 고객 연령층과 괴리가 발생하고 있습니다"
            },
            "R8": {
                "meaning": "시장부적합",
                "chart_type": "market_fit_analysis",
                "chart_title": "시장 적합도 분석",
                "chart_description": "시장 적합도가 낮아지고 있습니다"
            },
            "R9": {
                "meaning": "상권해지위험",
                "chart_type": "churn_risk_analysis",
                "chart_title": "상권 해지 위험도",
                "chart_description": "상권 내 경쟁력이 약화되고 있습니다"
            },
            "R10": {
                "meaning": "재방문율 낮음 (30% 이하)",
                "chart_type": "revisit_rate_absolute",
                "chart_title": "재방문율 절대값",
                "chart_description": "재방문율이 절대적으로 낮습니다 (30% 이하)"
            }
        }
        
        risk_table_data = []
        for risk in detected_risks:
            code = risk["code"]
            risk_info = risk_code_info.get(code, {
                "meaning": "알 수 없는 위험",
                "chart_type": "unknown",
                "chart_title": "분석 필요",
                "chart_description": "상세 분석이 필요합니다"
            })
            
            risk_table_data.append({
                "code": code,
                "meaning": risk_info["meaning"],
                "level": risk.get("level", "알 수 없음"),
                "score": risk.get("score", 0),
                "description": risk.get("description", ""),
                "evidence": risk.get("evidence", ""),
                "chart_type": risk_info["chart_type"],
                "chart_title": risk_info["chart_title"],
                "chart_description": risk_info["chart_description"],
                "priority": risk.get("priority", 5),
                "impact_score": risk.get("impact_score", 0)
            })
        
        # 전체 위험 수준 처리
        overall_risk_level = risk_analysis.get("overall_risk_level")
        if hasattr(overall_risk_level, 'value'):
            overall_risk_level_value = overall_risk_level.value
        else:
            overall_risk_level_value = str(overall_risk_level) if overall_risk_level else "unknown"
        
        risk_section = {
            "summary": risk_summary,
            "table_data": risk_table_data,
            "overall_risk_level": overall_risk_level_value
        }
        
        return {
            "persona": persona_section,
            "risk_diagnosis": risk_section
        }
    
    async def generate_query_response(
        self,
        query: str,
        store_report: Dict[str, Any],
        diagnostic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사용자 쿼리에 대한 맞춤형 응답 생성"""
        try:
            # 마케팅 분석 수행
            marketing_analysis = await self.run_marketing(store_report, diagnostic)
            
            if marketing_analysis.get("error"):
                return {
                    "query": query,
                    "response": f"분석 중 오류가 발생했습니다: {marketing_analysis['error']}",
                    "analysis_data": None
                }
            
            # 쿼리 타입에 따른 응답 생성
            query_type = self._classify_query(query)
            response = self._generate_targeted_response(
                query_type, query, marketing_analysis
            )
            
            return {
                "query": query,
                "response": response,
                "analysis_data": marketing_analysis
            }
            
        except Exception as e:
            return {
                "query": query,
                "response": f"응답 생성 중 오류가 발생했습니다: {str(e)}",
                "analysis_data": None
            }
    
    def _classify_query(self, query: str) -> str:
        """쿼리 타입 분류"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["문제점", "문제", "위험", "리스크"]):
            return "problem_analysis"
        elif any(keyword in query_lower for keyword in ["마케팅", "전략", "홍보", "캠페인"]):
            return "marketing_strategy"
        elif any(keyword in query_lower for keyword in ["고객", "타겟", "세그먼트"]):
            return "customer_analysis"
        elif any(keyword in query_lower for keyword in ["매출", "수익", "성과"]):
            return "performance_analysis"
        else:
            return "general_analysis"
    
    def _generate_targeted_response(
        self, 
        query_type: str, 
        query: str, 
        marketing_analysis: Dict[str, Any]
    ) -> str:
        """타겟팅된 응답 생성"""
        persona_info = marketing_analysis["persona_analysis"]
        risk_info = marketing_analysis["risk_analysis"]
        strategies = marketing_analysis["marketing_strategies"]
        
        if query_type == "problem_analysis":
            return self._generate_problem_analysis_response(query, risk_info, strategies)
        elif query_type == "marketing_strategy":
            return self._generate_marketing_strategy_response(query, persona_info, strategies)
        elif query_type == "customer_analysis":
            return self._generate_customer_analysis_response(query, persona_info)
        elif query_type == "performance_analysis":
            return self._generate_performance_analysis_response(query, marketing_analysis)
        else:
            return self._generate_general_response(query, marketing_analysis)
    
    def _generate_problem_analysis_response(
        self, 
        query: str, 
        risk_info: Dict[str, Any], 
        strategies: List[Dict[str, Any]]
    ) -> str:
        """문제 분석 응답 생성"""
        detected_risks = risk_info["detected_risks"]
        
        if not detected_risks:
            return "현재 매장은 안정적인 상태입니다. 특별한 문제점이 감지되지 않았습니다."
        
        response = f"매장에서 {len(detected_risks)}개의 주요 문제점이 감지되었습니다:\n\n"
        
        for i, risk in enumerate(detected_risks[:3], 1):
            response += f"{i}. {risk['name']} ({risk['code']})\n"
            response += f"   - {risk['description']}\n"
            response += f"   - 근거: {risk['evidence']}\n"
            response += f"   - 우선순위: {risk['priority']}\n\n"
        
        if strategies:
            response += "추천 해결 방안:\n"
            for strategy in strategies[:2]:
                response += f"- {strategy['name']}: {strategy['expected_impact']}\n"
        
        return response
    
    def _generate_marketing_strategy_response(
        self, 
        query: str, 
        persona_info: Dict[str, Any], 
        strategies: List[Dict[str, Any]]
    ) -> str:
        """마케팅 전략 응답 생성"""
        persona_type = persona_info["persona_type"]
        marketing_tone = persona_info["marketing_tone"]
        key_channels = persona_info["key_channels"]
        
        response = f"매장의 페르소나는 '{persona_type}'입니다.\n\n"
        response += f"마케팅 톤: {marketing_tone}\n"
        response += f"핵심 채널: {', '.join(key_channels)}\n\n"
        
        response += "추천 마케팅 전략:\n"
        for i, strategy in enumerate(strategies[:3], 1):
            response += f"{i}. {strategy['name']}\n"
            response += f"   - 채널: {strategy['channel']}\n"
            response += f"   - 예상 효과: {strategy['expected_impact']}\n"
            response += f"   - 예산: {strategy['budget_estimate']}\n\n"
        
        return response
    
    def _generate_customer_analysis_response(
        self, 
        query: str, 
        persona_info: Dict[str, Any]
    ) -> str:
        """고객 분석 응답 생성"""
        components = persona_info["components"]
        
        response = "매장의 주요 고객 특성:\n\n"
        response += f"업종: {components['industry']}\n"
        response += f"상권: {components['commercial_zone']}\n"
        response += f"고객 유형: {components['customer_type']}\n"
        response += f"주요 고객층: {components['customer_demographics']['gender']} {components['customer_demographics']['age']}\n"
        response += f"배달 비중: {components['delivery_ratio']}\n"
        response += f"신규 고객 트렌드: {components['trends']['new_customer']}\n"
        response += f"재방문 트렌드: {components['trends']['revisit']}\n"
        
        return response
    
    def _generate_performance_analysis_response(
        self, 
        query: str, 
        marketing_analysis: Dict[str, Any]
    ) -> str:
        """성과 분석 응답 생성"""
        campaign_plan = marketing_analysis["campaign_plan"]
        expected_kpis = campaign_plan["expected_kpis"]
        
        response = "예상 마케팅 성과:\n\n"
        response += f"매출 증가율: {expected_kpis.get('매출_증가율', 0)}%\n"
        response += f"신규 고객 증가율: {expected_kpis.get('신규_고객_증가율', 0)}%\n"
        response += f"재방문율 개선: {expected_kpis.get('재방문율_개선', 0)}%\n"
        response += f"SNS 팔로워 증가율: {expected_kpis.get('SNS_팔로워_증가율', 0)}%\n"
        response += f"성공 확률: {campaign_plan['success_probability']:.1f}%\n"
        
        return response
    
    def _generate_general_response(
        self, 
        query: str, 
        marketing_analysis: Dict[str, Any]
    ) -> str:
        """일반 응답 생성"""
        persona_info = marketing_analysis["persona_analysis"]
        risk_info = marketing_analysis["risk_analysis"]
        
        response = f"매장 분석 결과:\n\n"
        response += f"페르소나: {persona_info['persona_type']}\n"
        response += f"위험 수준: {risk_info['overall_risk_level']}\n"
        response += f"감지된 위험: {len(risk_info['detected_risks'])}개\n"
        response += f"추천 전략: {len(marketing_analysis['marketing_strategies'])}개\n\n"
        
        response += risk_info["analysis_summary"]
        
        return response
    
    def _convert_dynamic_strategies_to_objects(self, dynamic_strategies: List[str]) -> List:
        """동적 페르소나의 전략 문자열을 MarketingStrategy 객체로 변환"""
        try:
            from .strategy_generator import MarketingStrategy
        except ImportError:
            from strategy_generator import MarketingStrategy
        
        strategies = []
        for i, strategy_text in enumerate(dynamic_strategies):
            # 전략 텍스트에서 이름과 설명 추출
            if ": " in strategy_text:
                name, description = strategy_text.split(": ", 1)
            else:
                name = f"전략 {i+1}"
                description = strategy_text
            
            strategy = MarketingStrategy(
                strategy_id=f"DYNAMIC_STRAT_{i+1}",
                name=name.strip(),
                description=description.strip(),
                target_persona="dynamic",
                risk_codes=[],
                channel="다양한 채널",
                tactics=[description.strip()],
                expected_impact="매출 증대 및 고객 만족도 향상",
                implementation_time="1-2주",
                budget_estimate="중간",
                success_metrics=["매출 증가", "고객 수 증가", "재방문율 향상"],
                priority=i+1
            )
            strategies.append(strategy)
        
        return strategies
    
    async def _generate_social_content(
        self,
        persona_type: str,
        persona_template: Dict[str, Any],
        strategies: List,
        store_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SNS 포스트 및 프로모션 문구 생성"""
        try:
            try:
                from .dynamic_persona_generator import DynamicPersonaGenerator
            except ImportError:
                from dynamic_persona_generator import DynamicPersonaGenerator
            
            # Gemini 클라이언트 초기화
            gemini_client = DynamicPersonaGenerator().gemini_client
            
            # 매장 정보 추출
            store_name = store_data.get("store_name", "매장")
            industry = store_data.get("industry", "일반")
            address = store_data.get("address", "")
            
            # 페르소나 정보
            marketing_tone = persona_template.get("marketing_tone", "친근한")
            key_channels = persona_template.get("key_channels", [])
            
            # 전략 요약
            strategy_summaries = [f"- {strategy.name}: {strategy.description}" for strategy in strategies[:3]]
            
            # SNS 포스트 생성 프롬프트
            sns_prompt = f"""
            다음 매장 정보를 바탕으로 SNS 포스트 3개를 생성해주세요:
            
            매장 정보:
            - 매장명: {store_name}
            - 업종: {industry}
            - 위치: {address}
            - 페르소나: {persona_type}
            - 마케팅 톤: {marketing_tone}
            - 주요 채널: {', '.join(key_channels)}
            
            마케팅 전략:
            {chr(10).join(strategy_summaries)}
            
            다음 형식으로 JSON 응답해주세요:
            {{
                "instagram_posts": [
                    {{
                        "title": "포스트 제목",
                        "content": "포스트 내용 (이모지 포함, 해시태그 포함)",
                        "hashtags": ["#해시태그1", "#해시태그2"],
                        "post_type": "feed|story|reel"
                    }}
                ],
                "facebook_posts": [
                    {{
                        "title": "포스트 제목", 
                        "content": "포스트 내용",
                        "call_to_action": "행동 유도 문구"
                    }}
                ],
                "promotion_texts": [
                    {{
                        "type": "배너|팝업|SMS|이메일",
                        "title": "제목",
                        "content": "내용",
                        "discount": "할인 정보"
                    }}
                ]
            }}
            """
            
            messages = [{"role": "user", "content": sns_prompt}]
            response = gemini_client.chat_completion(
                messages=messages,
                temperature=0.8,
                model="gemini-2.5-flash"
            )
            
            # JSON 파싱
            if isinstance(response, str):
                try:
                    # 마크다운 코드 블록 제거
                    if "```json" in response:
                        start = response.find("```json") + 7
                        end = response.find("```", start)
                        if end != -1:
                            response = response[start:end].strip()
                    elif "```" in response:
                        start = response.find("```") + 3
                        end = response.find("```", start)
                        if end != -1:
                            response = response[start:end].strip()
                    
                    import json
                    social_content = json.loads(response)
                except json.JSONDecodeError:
                    # 기본 템플릿 반환
                    social_content = self._get_default_social_content(store_name, industry)
            else:
                social_content = response
            
            return social_content
            
        except Exception as e:
            print(f"SNS 콘텐츠 생성 오류: {e}")
            return self._get_default_social_content(
                store_data.get("store_name", "매장"),
                store_data.get("industry", "일반")
            )
    
    def _get_default_social_content(self, store_name: str, industry: str) -> Dict[str, Any]:
        """기본 SNS 콘텐츠 템플릿"""
        return {
            "instagram_posts": [
                {
                    "title": f"{store_name} 특별 이벤트! 🎉",
                    "content": f"안녕하세요! {store_name}입니다! 😊\n\n{industry} 전문점으로서 최고의 서비스를 제공하고 있습니다! 💪\n\n지금 방문하시면 특별한 혜택을 받으실 수 있어요! ✨\n\n#매장 #이벤트 #특가 #방문",
                    "hashtags": ["#매장", "#이벤트", "#특가", "#방문"],
                    "post_type": "feed"
                }
            ],
            "facebook_posts": [
                {
                    "title": f"{store_name}에서 만나요!",
                    "content": f"안녕하세요! {store_name}입니다.\n\n{industry} 전문점으로서 고객님께 최고의 서비스를 제공하겠습니다.\n\n지금 방문하시면 특별한 혜택이 기다립니다!",
                    "call_to_action": "지금 방문하기"
                }
            ],
            "promotion_texts": [
                {
                    "type": "배너",
                    "title": "신규 고객 특가!",
                    "content": f"{store_name}에서 신규 고객님을 위한 특별 할인을 진행합니다!",
                    "discount": "첫 방문 10% 할인"
                }
            ]
        }
    
    def format_marketing_output(self, result: Dict[str, Any]) -> str:
        """마케팅 분석 결과를 상담 에이전트 스타일의 구조화된 텍스트로 변환
        
        Args:
            result: run_marketing()의 반환값
            
        Returns:
            구조화된 마케팅 분석 텍스트 (현황→전략→실행→효과)
        """
        try:
            from strategy_generator import StrategyGenerator
            sg = StrategyGenerator()
        except:
            try:
                from .strategy_generator import StrategyGenerator
                sg = StrategyGenerator()
            except:
                sg = None
        
        # Gemini로 전체 마케팅 보고서 생성
        natural_language_summary = self._generate_natural_language_summary_with_gemini(result)
        
        # Gemini 생성 보고서를 그대로 반환
        if natural_language_summary:
            return natural_language_summary
        
        # Gemini 실패 시에만 기본 템플릿 사용
        print("[WARNING] Gemini 보고서 생성 실패. 기본 템플릿을 사용합니다.")
        
        # 페르소나 정보
        persona_analysis = result.get("persona_analysis", {})
        persona_type = persona_analysis.get("persona_type", "알 수 없음")
        persona_desc = persona_analysis.get("persona_description", "")
        
        # 위험 분석
        risk_analysis = result.get("risk_analysis", {})
        risk_level = risk_analysis.get("overall_risk_level", "알 수 없음")
        detected_risks = risk_analysis.get("detected_risks", [])
        
        # 마케팅 전략
        strategies = result.get("marketing_strategies", [])
        
        # 캠페인 계획
        campaign = result.get("campaign_plan", {})
        
        # 출력 생성
        output = []
        output.append("# 📈 마케팅 전략 분석 보고서\n\n")
        output.append("⚠️ **Gemini 기반 자연어 보고서 생성에 실패했습니다. 기본 템플릿을 사용합니다.**\n\n")
        
        components = persona_analysis.get("components", {})
        
        # 1. 현황 분석
        output.append("## 1️⃣ 현황 분석\n\n")
        output.append(f"### 🎯 페르소나 유형: {persona_type}\n")
        output.append(f"{persona_desc}\n")
        
        # 주요 특징
        components = persona_analysis.get("components", {})
        if components:
            output.append("\n**📊 매장 특성:**\n")
            output.append(f"- **업종:** {components.get('industry', 'N/A')}\n")
            output.append(f"- **상권:** {components.get('commercial_zone', 'N/A')}\n")
            output.append(f"- **매장 연령:** {components.get('store_age', 'N/A')}\n")
            
            customer_demo = components.get('customer_demographics', {})
            output.append(f"- **주요 고객:** {customer_demo.get('gender', 'N/A')} {customer_demo.get('age', 'N/A')}\n")
            output.append(f"- **고객 유형:** {components.get('customer_type', 'N/A')}\n")
            output.append(f"- **배달 비중:** {components.get('delivery_ratio', 'N/A')}\n")
        
        # 위험 요소
        output.append(f"\n### ⚠️ 위험 수준: {risk_level}\n")
        if detected_risks:
            output.append("\n**감지된 위험 요소:**\n")
            for risk in detected_risks[:3]:
                output.append(f"- **{risk.get('name', 'N/A')}** (우선순위: {risk.get('priority', 'N/A')})\n")
                output.append(f"  {risk.get('description', 'N/A')}\n")
        else:
            output.append("\n특별한 위험 요소가 감지되지 않았습니다. ✅\n")
        
        output.append("\n---\n")
        
        # 2. 전략 제시
        output.append("## 2️⃣ 추천 마케팅 전략\n")
        
        if strategies:
            for i, strategy in enumerate(strategies[:5], 1):
                output.append(f"\n### 전략 {i}: {strategy.get('name', 'N/A')}\n")
                output.append(f"\n**📋 설명:** {strategy.get('description', 'N/A')}\n")
                
                # 채널 정보 (구체적으로 확장)
                channel = strategy.get('channel', 'N/A')
                if channel != 'N/A' and sg:
                    try:
                        expanded = sg.expand_channel_details(channel)
                        
                        # 온라인 채널
                        if expanded.get("online_channels"):
                            online_list = []
                            for ch in expanded["online_channels"]:
                                if ch == "인스타그램":
                                    online_list.append("인스타그램 (릴스/피드/스토리)")
                                elif ch == "네이버지도":
                                    online_list.append("네이버 플레이스")
                                elif ch == "네이버플레이스":
                                    online_list.append("네이버 플레이스")
                                elif ch == "카카오맵":
                                    online_list.append("카카오맵")
                                elif ch == "배달앱":
                                    online_list.append("배달앱 (배민/쿠팡이츠)")
                                else:
                                    online_list.append(ch)
                            output.append(f"\n**📱 온라인 채널:** {', '.join(online_list)}\n")
                        
                        # 오프라인 채널
                        if expanded.get("offline_channels"):
                            offline_list = []
                            for ch in expanded["offline_channels"]:
                                details = expanded["details"].get(ch, {})
                                tactics = details.get("promotion_strategy", [])
                                if tactics:
                                    offline_list.append(f"{', '.join(tactics[:3])}")
                                else:
                                    offline_list.append(ch)
                            output.append(f"**🏪 오프라인 채널:** {', '.join(offline_list)}\n")
                    except:
                        output.append(f"\n**📱 마케팅 채널:** {channel}\n")
                else:
                    output.append(f"\n**📱 마케팅 채널:** {channel}\n")
                
                # 전술
                tactics = strategy.get('tactics', [])
                if tactics:
                    output.append("\n**⚡ 주요 전술:**\n")
                    for tactic in tactics:
                        output.append(f"  • {tactic}\n")
                
                output.append(f"\n**🎯 예상 효과:** {strategy.get('expected_impact', 'N/A')}\n")
                output.append(f"**⏱️ 구현 기간:** {strategy.get('implementation_time', 'N/A')}\n")
                output.append(f"**💰 예산:** {strategy.get('budget_estimate', 'N/A')}\n")
                output.append(f"**⭐ 우선순위:** {strategy.get('priority', 'N/A')}\n")
        else:
            output.append("\n마케팅 전략이 생성되지 않았습니다.\n")
        
        output.append("\n---\n")
        
        # 3. 실행 방안
        output.append("## 3️⃣ 실행 방안 (캠페인 계획)\n")
        
        if campaign:
            output.append(f"\n**📌 캠페인명:** {campaign.get('name', 'N/A')}\n")
            output.append(f"**📅 기간:** {campaign.get('duration', 'N/A')}\n")
            output.append(f"**📖 설명:** {campaign.get('description', 'N/A')}\n")
            
            # 예산 배분
            budget_allocation = campaign.get('budget_allocation', {})
            if budget_allocation:
                output.append("\n**💰 예산 배분:**\n")
                for channel, percentage in budget_allocation.items():
                    output.append(f"  • {channel}: {percentage}\n")
            
            # 타임라인
            timeline = campaign.get('timeline', [])
            if timeline:
                output.append("\n**📆 실행 일정:**\n")
                for item in timeline[:5]:
                    if isinstance(item, dict):
                        week = item.get('주차', item.get('week', 'N/A'))
                        activity = item.get('활동', item.get('activity', 'N/A'))
                        output.append(f"  • **{week}:** {activity}\n")
                    else:
                        output.append(f"  • {item}\n")
            
            # KPI
            expected_kpis = campaign.get('expected_kpis', {})
            if expected_kpis:
                output.append("\n**📊 목표 KPI:**\n")
                for kpi, value in expected_kpis.items():
                    output.append(f"  • {kpi}: {value}\n")
            
            output.append(f"\n**✅ 성공 확률:** {campaign.get('success_probability', 'N/A')}\n")
        else:
            output.append("\n캠페인 계획이 생성되지 않았습니다.\n")
        
        output.append("\n---\n")
        
        # 4. 예상 효과
        output.append("## 4️⃣ 예상 효과\n")
        
        if strategies:
            output.append("\n**전략별 예상 효과:**\n")
            for i, strategy in enumerate(strategies[:5], 1):
                output.append(f"\n**전략 {i} - {strategy.get('name', 'N/A')}:**\n")
                output.append(f"  • {strategy.get('expected_impact', 'N/A')}\n")
                
                # 성공 지표
                success_metrics = strategy.get('success_metrics', [])
                if success_metrics:
                    output.append(f"  • 성공 지표: {', '.join(success_metrics)}\n")
        
        if campaign:
            expected_kpis = campaign.get('expected_kpis', {})
            if expected_kpis:
                output.append("\n**캠페인 전체 예상 효과:**\n")
                for kpi, value in expected_kpis.items():
                    output.append(f"  • {kpi}: {value}\n")
        
        output.append("\n---\n")
        output.append("\n*본 분석은 Gemini 2.5 Flash 기반 마케팅 에이전트에 의해 생성되었습니다.*\n")
        
        return "".join(output)
    
    def _generate_natural_language_summary_with_gemini(self, result: Dict[str, Any]) -> str:
        """Gemini를 사용하여 마케팅 분석 결과의 자연어 종합 설명 생성"""
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            
            # 분석 결과 요약
            persona_analysis = result.get("persona_analysis", {})
            risk_analysis = result.get("risk_analysis", {})
            strategies = result.get("marketing_strategies", [])
            
            store_code = result.get("store_code", "매장")
            persona_type = persona_analysis.get("persona_type", "")
            components = persona_analysis.get("components", {})
            detected_risks = risk_analysis.get("detected_risks", [])
            
            # 전체 분석 데이터를 JSON으로 변환
            import json
            
            # 위험 요소 상세 정보
            risk_details = "\n".join([
                f"- {r.get('name', '')}: {r.get('description', '')} (우선순위: {r.get('priority', '')})"
                for r in detected_risks
            ]) if detected_risks else "- 특별한 위험 요소 없음"
            
            # 페르소나의 추천 채널 정보
            key_channels = persona_analysis.get("key_channels", [])
            key_channels_text = "\n".join([f"- {channel}" for channel in key_channels]) if key_channels else "- 채널 정보 없음"
            
            # 전략 요약 (채널 정보 확장하여 포함)
            strategy_details = []
            for i, s in enumerate(strategies[:6]):
                channel_info = s.get('channel', 'N/A')
                
                # 채널 정보 확장
                expanded_channels = []
                if '디지털' in channel_info or '온라인' in channel_info:
                    expanded_channels.extend(['인스타그램', '네이버지도', '네이버플레이스', '카카오맵'])
                if '배달앱' in channel_info:
                    expanded_channels.extend(['배달의민족', '쿠팡이츠'])
                if '오프라인' in channel_info or '매장' in channel_info:
                    expanded_channels.extend(['매장 POP', '전단지', '현수막'])
                if 'SNS' in channel_info:
                    expanded_channels.extend(['인스타그램', '페이스북', '틱톡'])
                
                # 확장된 채널이 없으면 원본 사용
                if not expanded_channels:
                    expanded_channels = [channel_info]
                
                channel_str = ", ".join(expanded_channels)
                
                strategy_details.append(
                    f"{i+1}. **{s.get('name', '')}**\n" +
                    f"   - 설명: {s.get('description', '')[:200]}...\n" +
                    f"   - 채널: {channel_str}\n" +
                    f"   - 주요 전술: {', '.join(s.get('tactics', [])[:2])}\n" +
                    f"   - 예상 효과: {s.get('expected_impact', '')}\n" +
                    f"   - 구현 기간: {s.get('implementation_time', '')}\n" +
                    f"   - 예산: {s.get('budget_estimate', '')}"
                )
            
            strategy_summary = "\n\n".join(strategy_details) if strategy_details else "전략 없음"
            
            # Gemini에게 전달할 프롬프트
            prompt = f"""
당신은 마케팅 전략 분석 전문가입니다. 아래의 **전체 분석 데이터**를 바탕으로 **자연스럽고 전문적인 한국어 종합 설명**을 작성해주세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 전체 분석 데이터:

### 매장 기본 정보:
- 매장 코드: {store_code}
- 페르소나 유형: {persona_type}
- 페르소나 설명: {persona_analysis.get('persona_description', '')}

### 매장 특성:
- 업종: {components.get('industry', 'N/A')}
- 상권: {components.get('commercial_zone', 'N/A')}
- 매장 연령: {components.get('store_age', 'N/A')}
- 프랜차이즈 여부: {'예' if components.get('is_franchise') else '아니오'}
- 주요 고객: {components.get('customer_demographics', {}).get('gender', '')} {components.get('customer_demographics', {}).get('age', '')}
- 고객 유형: {components.get('customer_type', '')}
- 배달 비중: {components.get('delivery_ratio', '')}
- 신규 고객 트렌드: {components.get('trends', {}).get('new_customer', '')}
- 재방문 트렌드: {components.get('trends', {}).get('revisit', '')}

### 추천 마케팅 채널:
{key_channels_text}

### 위험 분석:
- 전체 위험 수준: {risk_analysis.get('overall_risk_level', 'N/A')}
- 감지된 위험 요소:
{risk_details}

### 추천 마케팅 전략 ({len(strategies)}개):

{strategy_summary}

### 캠페인 계획:
- 캠페인명: {result.get('campaign_plan', {}).get('name', 'N/A')}
- 기간: {result.get('campaign_plan', {}).get('duration', 'N/A')}
- 성공 확률: {result.get('campaign_plan', {}).get('success_probability', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📝 작성 가이드:

다음 형식으로 **구체적이고 실행 가능한 분석**을 작성해주세요:

### 📋 종합 결론

**[첫 문단]** {store_code} 매장은 [상권 특성 + 위치 특성]에 위치하며, [주요 고객층 상세 설명]이라는 명확한 핵심 고객층을 보유하고 있습니다. [강점 요소들]의 잠재력을 가지고 있으나, [감지된 위험 요소들]에 대한 대응이 필요한 상황입니다.

**[두 번째 문단]** 성공적인 마케팅을 위해서는 이러한 데이터를 기반으로 한 **'타겟 고객 맞춤형, 접근성 강화, 고객 경쟁력 개선, 특색시장 공략'** 전략이 필수적입니다.

### 📢 홍보 아이디어

**위의 전략 데이터를 바탕으로 6가지 구체적이고 실행 가능한 홍보 아이디어를 작성해주세요:**

1. **[전략 1의 주요 전술]**: [구체적인 실행 방법 설명]
2. **[전략 2의 주요 전술]**: [구체적인 실행 방법 설명]
3. **[전략 3의 주요 전술]**: [구체적인 실행 방법 설명]
4. **[채널 기반 아이디어 1]**: [온라인 채널 활용 방안]
5. **[채널 기반 아이디어 2]**: [오프라인 채널 활용 방안]
6. **[채널 기반 아이디어 3]**: [통합 채널 활용 방안]

### 🎯 타겟 전략

**1. 주 타겟 고객층**
- **성별**: [주요 성별]
- **연령대**: [주요 연령대]
- **특성**: [고객 유형 및 행동 패턴]
- **추천 채널**: [이 타겟에게 가장 효과적인 온라인/오프라인 채널]

**2. 보조 타겟 고객층 및 확장 전략**
- **성별**: [보조 타겟 성별]
- **연령대**: [인접 연령대]
- **확장 전략**: [주 타겟에서 보조 타겟으로 확장하는 방법]
- **추천 채널**: [보조 타겟에게 적합한 채널]

### � 마케팅 채널 전략

**위의 전략 데이터에 포함된 채널 정보를 바탕으로 구체적인 채널 전략을 작성해주세요:**

**온라인 채널:**
- **인스타그램/틱톡**: [릴스/피드/스토리 활용 방안, 게시 빈도, 최적 시간대]
- **네이버 플레이스/지도**: [리뷰 관리, 메뉴 사진 업데이트, 키워드 최적화 방안]
- **카카오맵/카카오톡**: [카카오채널 활용, 쿠폰 발송, 예약 시스템 연동]
- **배달앱 (배민/쿠팡이츠)**: [메뉴 최적화, 리뷰 관리, 프로모션 전략]

**오프라인 채널:**
- **매장 POP/전단지**: [디자인 방향, 배포 전략, 타겟 반경]
- **현수막/간판**: [메시지 전략, 설치 위치]
- **이벤트/프로모션**: [매장 내 이벤트, 고객 참여 유도 방안]

**통합 채널 전략:**
- [온라인과 오프라인을 연계한 O2O 전략]
- [채널 간 시너지 극대화 방안]

### �📊 핵심 인사이트

**매장의 현재 상황을 3가지 핵심 포인트로 요약해주세요:**

1. **핵심 고객층**: [주요 고객의 특성과 행동 패턴 분석]
2. **경쟁 우위**: [매장이 가진 차별화 요소와 강점]
3. **개선 필요 영역**: [위험 요소와 개선이 필요한 부분]

### 🎯 다음 단계 제안:

**위의 분석을 바탕으로 4가지 구체적이고 실행 가능한 제안을 작성해주세요:**

1. [가장 시급한 개선 사항 - 위험 요소 기반]
2. [고객층 확대 방안 - 고객 데이터 기반]
3. [데이터 기반 의사결정 강화 방안]
4. [접근성/서비스 개선 방안]

**[마지막 문단]** 이러한 전략적 접근을 통해 매장은 [구체적인 개선 방향 3가지]를 실현하여 지속 가능한 성장을 이룰 수 있을 것입니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚠️ 중요 지침:

1. **데이터 기반 작성**: 위의 분석 데이터를 최대한 활용하여 구체적으로 작성
2. **자연스러운 한국어**: 전문적이면서도 이해하기 쉽게
3. **실행 가능성**: 모든 제안은 실제로 실행 가능해야 함
4. **구체성**: 추상적인 표현 대신 구체적인 숫자와 사실 사용
5. **맥락 반영**: 매장의 특성(페르소나, 상권, 고객층)을 충분히 반영
6. **긍정적 톤**: 문제점을 지적하되, 해결 방안 중심으로 서술

위 형식을 **정확히 따라** 작성해주세요.
"""
            
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "당신은 마케팅 전략 분석 전문가입니다. 데이터를 바탕으로 자연스럽고 전문적인 한국어 분석 보고서를 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=16000  # 8000 → 16000으로 증가 (토큰 부족 방지)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[WARNING] Gemini 자연어 설명 생성 실패: {e}")
            return ""

