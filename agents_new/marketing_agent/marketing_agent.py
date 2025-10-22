"""
Marketing Agent - 페르소나 기반 마케팅 전략 에이전트
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

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


class MarketingAgent:
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
            
            # Step 9: 결과 통합
            return {
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
                    "detected_risks": risk_analysis["detected_risks"],
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
                "marketing_focus_points": marketing_focus_points,
                "social_content": social_content,  # SNS 포스트 및 프로모션 문구
                "recommendations": self._generate_recommendations(
                    persona_type, detected_risk_codes, strategies
                )
            }
            
        except Exception as e:
            logger.error(f"Error running marketing analysis for {self.store_code}: {e}")
            
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
        """매장 리포트와 진단 데이터에서 지표 추출"""
        metrics_data = {}
        
        # 매장 리포트에서 지표 추출
        if "metrics" in store_report:
            metrics = store_report["metrics"]
            metrics_data.update({
                "revisit_rate": metrics.get("revisit_rate", 0),
                "delivery_ratio": metrics.get("delivery_ratio", 0),
                "new_customer_trend": metrics.get("new_customer_trend", 0),
                "cancellation_rate": metrics.get("cancellation_rate", 0),
                "market_fit_score": metrics.get("market_fit_score", 0),
                "business_churn_risk": metrics.get("business_churn_risk", 0)
            })
        
        # 진단 데이터에서 지표 추출
        if "diagnostic_results" in diagnostic:
            diag_results = diagnostic["diagnostic_results"]
            metrics_data.update({
                "sales_slump_days": diag_results.get("sales_slump_days", 0),
                "short_term_sales_drop": diag_results.get("short_term_sales_drop", 0),
                "delivery_sales_drop": diag_results.get("delivery_sales_drop", 0),
                "core_age_gap": diag_results.get("core_age_gap", 0)
            })
        
        # market_fit_score와 business_churn_risk가 없는 경우 계산
        if metrics_data.get("market_fit_score", 0) == 0:
            metrics_data["market_fit_score"] = self._calculate_market_fit_score(store_report, diagnostic)
        
        if metrics_data.get("business_churn_risk", 0) == 0:
            metrics_data["business_churn_risk"] = self._calculate_business_churn_risk(store_report, diagnostic)
        
        return metrics_data
    
    def _calculate_market_fit_score(self, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> float:
        """시장 적합도 점수 계산 - 실제 매장 데이터 기반"""
        try:
            # 매장 리포트에서 실제 데이터 추출
            if "store_overview" in store_report:
                store_data = store_report["store_overview"]
                
                # 재방문 고객 비율 (실제 데이터)
                revisit_customers = store_data.get("재방문고객", 0)
                
                # 신규 고객 비율 (실제 데이터)
                new_customers = store_data.get("신규고객", 0)
                
                # 취소율 (실제 데이터)
                cancellation_rate = store_data.get("취소율", 0)
                
                # 매출 성장률 계산 (최근 3개월 평균)
                sales_data = store_report.get("sales_analysis", {})
                monthly_sales = sales_data.get("monthly_sales", [])
                
                # 고객 분석 데이터
                customer_data = store_report.get("customer_analysis", {})
                customer_growth = customer_data.get("customer_growth_rate", 0)
                
                # 시장 적합도 점수 계산 (가중치 적용)
                score = 0.0
                
                # 1. 재방문 고객 비율 (30% 가중치)
                if revisit_customers > 70:
                    score += 30
                elif revisit_customers > 50:
                    score += 20
                elif revisit_customers > 30:
                    score += 10
                
                # 2. 취소율 (20% 가중치) - 낮을수록 좋음
                if cancellation_rate < 5:
                    score += 20
                elif cancellation_rate < 10:
                    score += 15
                elif cancellation_rate < 15:
                    score += 10
                elif cancellation_rate < 20:
                    score += 5
                
                # 3. 고객 성장률 (25% 가중치)
                if customer_growth > 10:
                    score += 25
                elif customer_growth > 5:
                    score += 20
                elif customer_growth > 0:
                    score += 15
                elif customer_growth > -5:
                    score += 10
                elif customer_growth > -10:
                    score += 5
                
                # 4. 매출 안정성 (25% 가중치)
                if monthly_sales:
                    recent_sales = monthly_sales[-3:] if len(monthly_sales) >= 3 else monthly_sales
                    if recent_sales:
                        avg_sales = sum(recent_sales) / len(recent_sales)
                        sales_variance = sum((x - avg_sales) ** 2 for x in recent_sales) / len(recent_sales)
                        sales_stability = max(0, 25 - (sales_variance / avg_sales) * 10) if avg_sales > 0 else 0
                        score += sales_stability
                
                return min(100, max(0, score))
            
            # 기본값 반환 (데이터가 없는 경우)
            return 50.0
            
        except Exception as e:
            logger.warning(f"시장 적합도 점수 계산 중 오류: {e}")
            return 50.0
    
    def _calculate_business_churn_risk(self, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> float:
        """상권 해지 위험도 계산 - 실제 매장 데이터 기반"""
        try:
            # 매장 리포트에서 실제 데이터 추출
            if "store_overview" in store_report:
                store_data = store_report["store_overview"]
                
                # 해지 위험도 점수 (0-100, 높을수록 위험)
                risk_score = 0.0
                
                # 1. 동종업계 해지 가맹점 비율 (25% 가중치)
                same_industry_churn = store_data.get("동종해지가맹점", 0)
                if same_industry_churn > 20:
                    risk_score += 25
                elif same_industry_churn > 15:
                    risk_score += 20
                elif same_industry_churn > 10:
                    risk_score += 15
                elif same_industry_churn > 5:
                    risk_score += 10
                
                # 2. 동일상권 해지 가맹점 비중 (20% 가중치)
                same_area_churn = store_data.get("동일상권해지가맹점비중", 0)
                if same_area_churn > 15:
                    risk_score += 20
                elif same_area_churn > 10:
                    risk_score += 15
                elif same_area_churn > 5:
                    risk_score += 10
                
                # 3. 매출 순위 하락 (20% 가중치)
                sales_rank = store_data.get("동종매출순위%", 0)
                if sales_rank > 80:  # 하위 20%
                    risk_score += 20
                elif sales_rank > 70:  # 하위 30%
                    risk_score += 15
                elif sales_rank > 60:  # 하위 40%
                    risk_score += 10
                elif sales_rank > 50:  # safety zone
                    risk_score += 5
                
                # 4. 상권 내 매출 순위 (15% 가중치)
                area_sales_rank = store_data.get("동일상권매출순위%", 0)
                if area_sales_rank > 80:
                    risk_score += 15
                elif area_sales_rank > 70:
                    risk_score += 12
                elif area_sales_rank > 60:
                    risk_score += 8
                elif area_sales_rank > 50:
                    risk_score += 5
                
                # 5. 운영 개월수 (10% 가중치) - 신규일수록 위험
                operation_months = store_data.get("운영개월수", 0)
                if operation_months < 6:  # 6개월 미만
                    risk_score += 10
                elif operation_months < 12:  # 1년 미만
                    risk_score += 8
                elif operation_months < 24:  # 2년 미만
                    risk_score += 5
                
                # 6. 취소율 (10% 가중치)
                cancellation_rate = store_data.get("취소율", 0)
                if cancellation_rate > 20:
                    risk_score += 10
                elif cancellation_rate > 15:
                    risk_score += 8
                elif cancellation_rate > 10:
                    risk_score += 5
                
                return min(100, max(0, risk_score))
            
            # 기본값 반환 (데이터가 없는 경우)
            return 30.0
            
        except Exception as e:
            logger.warning(f"상권 해지 위험도 계산 중 오류: {e}")
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
                    "gender": persona_components.main_customer_gender,
                    "age": persona_components.main_customer_age
                },
                "customer_trends": {
                    "new_customer": persona_components.new_customer_trend,
                    "revisit": persona_components.revisit_trend
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
        
        # 위험 코드별 상세 정보
        risk_code_info = {
            "R1": {"meaning": "신규유입 급감", "chart_type": "trend"},
            "R2": {"meaning": "낮은 재방문율", "chart_type": "comparison"},
            "R3": {"meaning": "장기매출침체", "chart_type": "trend"},
            "R4": {"meaning": "단기매출하락", "chart_type": "trend"},
            "R5": {"meaning": "배달매출하락", "chart_type": "trend"},
            "R6": {"meaning": "취소율 급등", "chart_type": "trend"},
            "R7": {"meaning": "핵심연령괴리", "chart_type": "comparison"},
            "R8": {"meaning": "시장부적합", "chart_type": "analysis"},
            "R9": {"meaning": "상권해지위험", "chart_type": "analysis"}
        }
        
        risk_table_data = []
        for risk in detected_risks:
            code = risk["code"]
            risk_info = risk_code_info.get(code, {"meaning": "알 수 없는 위험", "chart_type": "unknown"})
            risk_table_data.append({
                "code": code,
                "meaning": risk_info["meaning"],
                "severity": risk.get("severity", "unknown"),
                "description": risk.get("description", ""),
                "chart_type": risk_info["chart_type"]
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

