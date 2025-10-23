"""
위험 코드 체계 및 트리거 시스템
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math


class RiskLevel(Enum):
    """위험 수준"""
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"
    CRITICAL = "위험"


@dataclass
class RiskCode:
    """위험 코드 정의"""
    code: str
    name: str
    description: str
    trigger_condition: str
    threshold_value: float
    priority: int
    impact_score: float


class RiskAnalyzer:
    """위험 분석기 - 매장 지표를 기반으로 위험 코드 생성"""
    
    def __init__(self):
        self.risk_codes = self._initialize_risk_codes()
        self.industry_averages = self._load_industry_averages()
        self.risk_mitigation_strategies = self._load_mitigation_strategies()
    
    def _initialize_risk_codes(self) -> Dict[str, RiskCode]:
        """위험 코드 초기화"""
        return {
            "R1": RiskCode(
                code="R1",
                name="신규유입 급감",
                description="신규 고객 유입이 급격히 감소하고 있음",
                trigger_condition="new_customer_sink <= -3%",
                threshold_value=-3.0,
                priority=1,
                impact_score=8.5
            ),
            "R2": RiskCode(
                code="R2",
                name="재방문율 저하",
                description="재방문 고객 비율이 감소하고 있음",
                trigger_condition="revisit_rate_drop <= -3%",
                threshold_value=-3.0,
                priority=2,
                impact_score=7.5
            ),
            "R3": RiskCode(
                code="R3",
                name="장기매출침체",
                description="장기간 매출이 정체되거나 감소하고 있음",
                trigger_condition="long_term_slump >= 10 days",
                threshold_value=10.0,
                priority=1,
                impact_score=9.0
            ),
            "R4": RiskCode(
                code="R4",
                name="단기매출하락",
                description="단기간 매출이 급격히 하락하고 있음",
                trigger_condition="short_term_drop >= 15%",
                threshold_value=15.0,
                priority=2,
                impact_score=8.0
            ),
            "R5": RiskCode(
                code="R5",
                name="배달매출하락",
                description="배달 매출이 감소하고 있음",
                trigger_condition="delivery_sales_drop <= -10%",
                threshold_value=-10.0,
                priority=3,
                impact_score=6.5
            ),
            "R6": RiskCode(
                code="R6",
                name="취소율 급등",
                description="주문 취소율이 급격히 증가하고 있음",
                trigger_condition="cancellation_spike >= 0.7%",
                threshold_value=0.7,
                priority=3,
                impact_score=7.0
            ),
            "R7": RiskCode(
                code="R7",
                name="핵심연령괴리",
                description="핵심 고객 연령층과의 괴리가 발생하고 있음",
                trigger_condition="core_age_gap <= -8%",
                threshold_value=-8.0,
                priority=4,
                impact_score=6.0
            ),
            "R8": RiskCode(
                code="R8",
                name="시장부적합",
                description="시장 적합도가 낮아지고 있음",
                trigger_condition="market_fit_score >= 70",
                threshold_value=70.0,
                priority=2,
                impact_score=8.0
            ),
            "R9": RiskCode(
                code="R9",
                name="상권해지위험",
                description="상권 내 경쟁력이 약화되고 있음",
                trigger_condition="business_churn_risk >= industry_avg + 1.5σ",
                threshold_value=1.5,
                priority=1,
                impact_score=9.5
            ),
            "R10": RiskCode(
                code="R10",
                name="재방문율 낮음",
                description="재방문율이 절대적으로 낮음 (30% 이하)",
                trigger_condition="revisit_rate <= 30%",
                threshold_value=30.0,
                priority=2,
                impact_score=7.8
            )
        }
    
    def _load_industry_averages(self) -> Dict[str, Dict[str, float]]:
        """업종별 평균 지표 로드"""
        return {
            "카페": {
                "avg_revisit_rate": 36.2,
                "avg_delivery_ratio": 28.6,
                "avg_cancellation_rate": 2.1,
                "avg_market_fit": 45.0
            },
            "중식": {
                "avg_revisit_rate": 42.1,
                "avg_delivery_ratio": 52.3,
                "avg_cancellation_rate": 1.8,
                "avg_market_fit": 38.0
            },
            "치킨": {
                "avg_revisit_rate": 38.7,
                "avg_delivery_ratio": 67.4,
                "avg_cancellation_rate": 2.5,
                "avg_market_fit": 41.0
            },
            "한식": {
                "avg_revisit_rate": 44.5,
                "avg_delivery_ratio": 35.2,
                "avg_cancellation_rate": 1.5,
                "avg_market_fit": 42.0
            }
        }
    
    def _load_mitigation_strategies(self) -> Dict[str, List[str]]:
        """위험 코드별 완화 전략 로드"""
        return {
            "R1": [
                "SNS 광고 집중 투자",
                "신규 고객 유입 캠페인",
                "지도 노출 최적화",
                "인플루언서 협업"
            ],
            "R2": [
                "로열티 프로그램 도입",
                "재방문 쿠폰 발송",
                "고객 관계 관리 강화",
                "멤버십 혜택 확대"
            ],
            "R3": [
                "메뉴 리뉴얼",
                "브랜드 재포지셔닝",
                "가격 전략 재검토",
                "마케팅 예산 증액"
            ],
            "R4": [
                "즉시 프로모션 실행",
                "단기 할인 캠페인",
                "고객 유지 전략",
                "경쟁 분석 강화"
            ],
            "R5": [
                "배달앱 최적화",
                "배달 메뉴 개선",
                "배달 시간 단축",
                "배달 포장 품질 향상"
            ],
            "R6": [
                "주문 프로세스 개선",
                "고객 서비스 강화",
                "메뉴 명확화",
                "취소 정책 개선"
            ],
            "R7": [
                "타겟 고객 재분석",
                "마케팅 메시지 조정",
                "고객 세그먼트별 접근",
                "연령대별 맞춤 전략"
            ],
            "R8": [
                "시장 조사 강화",
                "고객 니즈 재분석",
                "차별화 전략 수립",
                "경쟁우위 요소 발굴"
            ],
            "R9": [
                "상권 분석 재실시",
                "경쟁사 분석 강화",
                "차별화 포인트 강화",
                "지역 밀착형 마케팅"
            ],
            "R10": [
                "스탬프 적립 프로그램 도입",
                "재방문 고객 전용 할인 쿠폰",
                "회원 멤버십 혜택 확대",
                "단골 고객 감사 이벤트",
                "생일/기념일 특별 혜택"
            ]
        }
    
    async def analyze_risks(self, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """위험 분석 수행"""
        try:
            detected_risks = []
            risk_scores = {}
            
            # 각 위험 코드에 대해 분석
            for risk_code, risk_def in self.risk_codes.items():
                risk_result = await self._check_risk_condition(
                    risk_code, risk_def, store_data, metrics_data
                )
                
                if risk_result["detected"]:
                    detected_risks.append({
                        "code": risk_code,
                        "name": risk_def.name,
                        "description": risk_def.description,
                        "level": risk_result["level"],
                        "score": risk_result["score"],
                        "evidence": risk_result["evidence"],
                        "priority": risk_def.priority,
                        "impact_score": risk_def.impact_score
                    })
                    
                    risk_scores[risk_code] = risk_result["score"]
            
            # 위험 코드 우선순위 정렬
            detected_risks.sort(key=lambda x: (x["priority"], -x["score"]), reverse=False)
            
            # 전체 위험도 계산
            overall_risk_level = self._calculate_overall_risk_level(risk_scores)
            
            # 완화 전략 제안
            mitigation_strategies = self._generate_mitigation_strategies(detected_risks)
            
            return {
                "overall_risk_level": overall_risk_level,
                "detected_risks": detected_risks,
                "risk_scores": risk_scores,
                "mitigation_strategies": mitigation_strategies,
                "analysis_summary": self._generate_analysis_summary(detected_risks, store_data)
            }
            
        except Exception as e:
            return {
                "error": f"위험 분석 중 오류 발생: {str(e)}",
                "overall_risk_level": RiskLevel.MEDIUM,
                "detected_risks": [],
                "risk_scores": {},
                "mitigation_strategies": []
            }
    
    async def _check_risk_condition(
        self, 
        risk_code: str, 
        risk_def: RiskCode, 
        store_data: Dict[str, Any], 
        metrics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개별 위험 조건 체크"""
        try:
            if risk_code == "R1":
                return await self._check_new_customer_sink(risk_def, store_data, metrics_data)
            elif risk_code == "R2":
                return await self._check_revisit_drop(risk_def, store_data, metrics_data)
            elif risk_code == "R3":
                return await self._check_long_term_slump(risk_def, store_data, metrics_data)
            elif risk_code == "R4":
                return await self._check_short_term_drop(risk_def, store_data, metrics_data)
            elif risk_code == "R5":
                return await self._check_delivery_sales_drop(risk_def, store_data, metrics_data)
            elif risk_code == "R6":
                return await self._check_cancellation_spike(risk_def, store_data, metrics_data)
            elif risk_code == "R7":
                return await self._check_core_age_gap(risk_def, store_data, metrics_data)
            elif risk_code == "R8":
                return await self._check_market_fit(risk_def, store_data, metrics_data)
            elif risk_code == "R9":
                return await self._check_business_churn_risk(risk_def, store_data, metrics_data)
            elif risk_code == "R10":
                return await self._check_low_revisit_rate(risk_def, store_data, metrics_data)
            else:
                return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
                
        except Exception as e:
            return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": f"분석 오류: {str(e)}"}
    
    async def _check_new_customer_sink(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """신규 고객 유입 감소 체크"""
        new_customer_trend = metrics_data.get("new_customer_trend", 0)
        
        if new_customer_trend <= risk_def.threshold_value:
            severity = abs(new_customer_trend - risk_def.threshold_value)
            level = self._determine_risk_level(severity)
            score = min(severity * 10, 100)
            
            evidence = f"신규 고객 유입이 {new_customer_trend:.1f}% 감소 (기준: {risk_def.threshold_value}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_revisit_drop(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """재방문율 하락 체크"""
        revisit_rate = metrics_data.get("revisit_rate", 0)
        industry = store_data.get("industry", "한식")
        industry_avg = self.industry_averages.get(industry, {}).get("avg_revisit_rate", 40)
        
        if revisit_rate <= industry_avg + risk_def.threshold_value:
            severity = abs(revisit_rate - (industry_avg + risk_def.threshold_value))
            level = self._determine_risk_level(severity)
            score = min(severity * 5, 100)
            
            evidence = f"재방문율 {revisit_rate:.1f}% (업종평균: {industry_avg:.1f}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_long_term_slump(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """장기 매출 침체 체크"""
        sales_slump_days = metrics_data.get("sales_slump_days", 0)
        
        if sales_slump_days >= risk_def.threshold_value:
            severity = sales_slump_days - risk_def.threshold_value
            level = self._determine_risk_level(severity)
            score = min(severity * 8, 100)
            
            evidence = f"매출 침체 기간 {sales_slump_days}일 (기준: {risk_def.threshold_value}일)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_short_term_drop(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """단기 매출 하락 체크"""
        short_term_drop = metrics_data.get("short_term_sales_drop", 0)
        
        if short_term_drop >= risk_def.threshold_value:
            severity = short_term_drop - risk_def.threshold_value
            level = self._determine_risk_level(severity)
            score = min(severity * 6, 100)
            
            evidence = f"단기 매출 하락 {short_term_drop:.1f}% (기준: {risk_def.threshold_value}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_delivery_sales_drop(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """배달 매출 하락 체크"""
        delivery_drop = metrics_data.get("delivery_sales_drop", 0)
        
        if delivery_drop <= risk_def.threshold_value:
            severity = abs(delivery_drop - risk_def.threshold_value)
            level = self._determine_risk_level(severity)
            score = min(severity * 8, 100)
            
            evidence = f"배달 매출 하락 {delivery_drop:.1f}% (기준: {risk_def.threshold_value}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_cancellation_spike(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """취소율 급등 체크"""
        cancellation_rate = metrics_data.get("cancellation_rate", 0)
        
        if cancellation_rate >= risk_def.threshold_value:
            severity = cancellation_rate - risk_def.threshold_value
            level = self._determine_risk_level(severity)
            score = min(severity * 15, 100)
            
            evidence = f"취소율 {cancellation_rate:.2f}% (기준: {risk_def.threshold_value}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_core_age_gap(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """핵심 연령층 괴리 체크"""
        age_gap = metrics_data.get("core_age_gap", 0)
        
        if age_gap <= risk_def.threshold_value:
            severity = abs(age_gap - risk_def.threshold_value)
            level = self._determine_risk_level(severity)
            score = min(severity * 8, 100)
            
            evidence = f"핵심 연령층 괴리 {age_gap:.1f}% (기준: {risk_def.threshold_value}%)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_market_fit(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """시장 부적합 체크"""
        market_fit_score = metrics_data.get("market_fit_score", 0)
        
        if market_fit_score >= risk_def.threshold_value:
            severity = market_fit_score - risk_def.threshold_value
            level = self._determine_risk_level(severity)
            score = min(severity * 3, 100)
            
            evidence = f"시장 적합도 점수 {market_fit_score:.1f} (기준: {risk_def.threshold_value})"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_business_churn_risk(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """상권 해지 위험 체크"""
        industry = store_data.get("industry", "한식")
        industry_avg = self.industry_averages.get(industry, {}).get("avg_market_fit", 40)
        churn_risk = metrics_data.get("business_churn_risk", 0)
        
        threshold = industry_avg + (risk_def.threshold_value * 10)  # 1.5σ approximation
        
        if churn_risk >= threshold:
            severity = churn_risk - threshold
            level = self._determine_risk_level(severity)
            score = min(severity * 5, 100)
            
            evidence = f"상권 해지 위험도 {churn_risk:.1f} (업종평균+1.5σ: {threshold:.1f})"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    async def _check_low_revisit_rate(self, risk_def: RiskCode, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """재방문율 30% 이하 체크 (R10)"""
        revisit_rate = metrics_data.get("revisit_rate", 0)
        industry = store_data.get("industry", "한식")
        industry_avg = self.industry_averages.get(industry, {}).get("avg_revisit_rate", 40)
        
        # 재방문율이 30% 이하인지 체크
        if revisit_rate <= risk_def.threshold_value:
            # R2 (재방문율 저하)는 트리거되지 않았지만 절대값이 낮은 경우
            severity = risk_def.threshold_value - revisit_rate
            level = self._determine_risk_level(severity)
            score = min(severity * 6, 100)
            
            # R2 위험요소가 없는지 확인 (동종 업종 대비 낮지 않음)
            if revisit_rate > industry_avg - 3:  # R2 조건에 해당하지 않음
                evidence = f"재방문율 {revisit_rate:.1f}% (업종평균: {industry_avg:.1f}% - 동종 업종 대비 낮지는 않으나 절대값 30% 이하)"
            else:
                evidence = f"재방문율 {revisit_rate:.1f}% (기준: 30% 이하)"
            
            return {
                "detected": True,
                "level": level,
                "score": score,
                "evidence": evidence
            }
        
        return {"detected": False, "level": RiskLevel.LOW, "score": 0.0, "evidence": ""}
    
    def _determine_risk_level(self, severity: float) -> RiskLevel:
        """심각도에 따른 위험 수준 결정"""
        if severity >= 20:
            return RiskLevel.CRITICAL
        elif severity >= 10:
            return RiskLevel.HIGH
        elif severity >= 5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_overall_risk_level(self, risk_scores: Dict[str, float]) -> RiskLevel:
        """전체 위험도 계산"""
        if not risk_scores:
            return RiskLevel.LOW
        
        avg_score = sum(risk_scores.values()) / len(risk_scores)
        
        if avg_score >= 80:
            return RiskLevel.CRITICAL
        elif avg_score >= 60:
            return RiskLevel.HIGH
        elif avg_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_mitigation_strategies(self, detected_risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """완화 전략 생성"""
        strategies = []
        
        for risk in detected_risks[:5]:  # 상위 5개 위험만 처리
            risk_code = risk["code"]
            if risk_code in self.risk_mitigation_strategies:
                strategies.append({
                    "risk_code": risk_code,
                    "risk_name": risk["name"],
                    "priority": risk["priority"],
                    "strategies": self.risk_mitigation_strategies[risk_code],
                    "impact_score": risk["impact_score"]
                })
        
        return strategies
    
    def _generate_analysis_summary(self, detected_risks: List[Dict[str, Any]], store_data: Dict[str, Any]) -> str:
        """분석 요약 생성"""
        if not detected_risks:
            return "현재 매장은 안정적인 상태이며 특별한 위험 요소가 감지되지 않았습니다."
        
        high_priority_risks = [r for r in detected_risks if r["priority"] <= 2]
        
        if high_priority_risks:
            risk_names = [r["name"] for r in high_priority_risks[:3]]
            return f"매장에서 {', '.join(risk_names)} 등의 주요 위험 요소가 감지되었습니다. 즉시 대응이 필요합니다."
        else:
            risk_names = [r["name"] for r in detected_risks[:3]]
            return f"매장에서 {', '.join(risk_names)} 등의 위험 요소가 감지되었습니다. 모니터링과 함께 단계적 대응을 권장합니다."
