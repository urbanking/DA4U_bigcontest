"""
OpenAI Agents SDK를 사용한 마케팅 에이전트 래퍼
이미지의 User Flow를 구현한 마케팅 에이전트
"""
from typing import Dict, Any, List, Optional
# OpenAI Agents SDK 의존성 제거 (독립 실행을 위해)
# from openai_agents import Agent, Tool, Message

# 대체 클래스 정의
class Agent:
    """대체 Agent 클래스"""
    def __init__(self, tools=None, system_prompt=""):
        self.tools = tools or []
        self.system_prompt = system_prompt

class Tool:
    """대체 Tool 클래스"""
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

class Message:
    """대체 Message 클래스"""
    def __init__(self, role, content):
        self.role = role
        self.content = content
try:
    # 패키지로 실행될 때
    from .marketing_agent import marketingagent
    from .persona_engine import PersonaEngine
    from .risk_analyzer import RiskAnalyzer
    from .strategy_generator import StrategyGenerator
except ImportError:
    # 독립 실행될 때
    from marketing_agent import marketingagent
    from persona_engine import PersonaEngine
    from risk_analyzer import RiskAnalyzer
    from strategy_generator import StrategyGenerator
import json


class MarketingAgentWrapper:
    """OpenAI Agents SDK를 사용한 마케팅 에이전트 래퍼"""
    
    def __init__(self, store_code: str):
        self.store_code = store_code
        self.marketing_agent = marketingagent(store_code)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """OpenAI Agents SDK 에이전트 생성"""
        
        # 도구 정의
        tools = [
            Tool(
                name="analyze_store_persona",
                description="매장 데이터를 분석하여 페르소나 구성요소를 추출합니다",
                function=self._analyze_store_persona
            ),
            Tool(
                name="classify_persona_type",
                description="페르소나 구성요소를 기반으로 매장 페르소나 유형을 분류합니다",
                function=self._classify_persona_type
            ),
            Tool(
                name="analyze_risk_codes",
                description="매장 지표를 분석하여 위험 코드를 감지합니다",
                function=self._analyze_risk_codes
            ),
            Tool(
                name="generate_marketing_strategies",
                description="페르소나와 위험 코드를 기반으로 맞춤 마케팅 전략을 생성합니다",
                function=self._generate_marketing_strategies
            ),
            Tool(
                name="create_campaign_plan",
                description="마케팅 전략들을 통합하여 캠페인 계획을 생성합니다",
                function=self._create_campaign_plan
            ),
            Tool(
                name="generate_query_response",
                description="사용자 쿼리에 대한 맞춤형 응답을 생성합니다",
                function=self._generate_query_response
            )
        ]
        
        # 시스템 프롬프트
        system_prompt = """
당신은 전문 마케팅 컨설턴트 AI입니다. 

주요 역할:
1. 매장 페르소나 분석 - 업종, 상권, 고객 특성 등을 종합 분석
2. 위험 코드 감지 - 매출, 고객, 운영 지표를 분석하여 위험 요소 식별
3. 맞춤 마케팅 전략 제안 - 페르소나와 위험 코드를 기반으로 구체적인 마케팅 전략 생성
4. 캠페인 계획 수립 - 실행 가능한 마케팅 캠페인 계획 제공

분석 프로세스:
1. 매장 데이터 → 페르소나 구성요소 추출
2. 페르소나 구성요소 → 페르소나 유형 분류
3. 매장 지표 → 위험 코드 감지 (R1~R9)
4. 페르소나 + 위험코드 → 맞춤 마케팅 전략 생성
5. 전략들 → 통합 캠페인 계획 수립

사용자에게는 위험 순으로 위험 코드를 제시하고, 페르소나 맞춤 ALERT FIXING 제안과 구체적 마케팅안을 제공하세요.
"""
        
        return Agent(
            description="전문 마케팅 컨설턴트 AI - 페르소나 기반 맞춤 마케팅 전략 제공",
            instructions=system_prompt,
            tools=tools,
            model="gpt-4o"
        )
    
    async def process_query(self, query: str, store_report: Dict[str, Any], diagnostic: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 쿼리 처리 - 이미지의 User Flow 구현"""
        try:
            # 컨텍스트 설정
            context = {
                "store_code": self.store_code,
                "store_report": store_report,
                "diagnostic": diagnostic,
                "query": query
            }
            
            # 에이전트 실행
            response = await self.agent.run(
                messages=[Message(role="user", content=query)],
                context=context
            )
            
            return {
                "query": query,
                "response": response.content,
                "context": context,
                "success": True
            }
            
        except Exception as e:
            return {
                "query": query,
                "response": f"마케팅 분석 중 오류가 발생했습니다: {str(e)}",
                "context": None,
                "success": False
            }
    
    async def _analyze_store_persona(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        """매장 페르소나 분석"""
        try:
            result = await self.marketing_agent.persona_engine.analyze_store_persona(store_data)
            return {
                "success": True,
                "persona_components": result.get("components"),
                "raw_data": result.get("raw_data"),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "persona_components": None
            }
    
    async def _classify_persona_type(self, persona_components: Dict[str, Any]) -> Dict[str, Any]:
        """페르소나 유형 분류"""
        try:
            try:
                from .persona_engine import PersonaComponents
            except ImportError:
                from persona_engine import PersonaComponents
            
            # PersonaComponents 객체 생성 (실제로는 더 정교한 변환 필요)
            components = PersonaComponents(
                industry=persona_components.get("industry"),
                commercial_zone=persona_components.get("commercial_zone"),
                is_franchise=persona_components.get("is_franchise", False),
                store_age=persona_components.get("store_age"),
                main_customer_gender=persona_components.get("main_customer_gender", "혼합"),
                main_customer_age=persona_components.get("main_customer_age", "혼합"),
                customer_type=persona_components.get("customer_type"),
                new_customer_trend=persona_components.get("new_customer_trend", "정체"),
                revisit_trend=persona_components.get("revisit_trend", "정체"),
                delivery_ratio=persona_components.get("delivery_ratio", "중간")
            )
            
            persona_type, persona_template = await self.marketing_agent.persona_engine.classify_persona(components)
            
            return {
                "success": True,
                "persona_type": persona_type,
                "persona_template": persona_template
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "persona_type": None
            }
    
    async def _analyze_risk_codes(self, store_data: Dict[str, Any], metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """위험 코드 분석"""
        try:
            result = await self.marketing_agent.risk_analyzer.analyze_risks(store_data, metrics_data)
            return {
                "success": True,
                "overall_risk_level": result.get("overall_risk_level"),
                "detected_risks": result.get("detected_risks", []),
                "risk_scores": result.get("risk_scores", {}),
                "analysis_summary": result.get("analysis_summary", "")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "detected_risks": []
            }
    
    async def _generate_marketing_strategies(
        self, 
        persona_type: str, 
        risk_codes: List[str], 
        store_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """마케팅 전략 생성"""
        try:
            seasonal_context = self.marketing_agent._get_seasonal_context()
            strategies = await self.marketing_agent.strategy_generator.generate_persona_based_strategies(
                persona_type=persona_type,
                risk_codes=risk_codes,
                store_data=store_data,
                seasonal_context=seasonal_context
            )
            
            return {
                "success": True,
                "strategies": [
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
                        "priority": strategy.priority
                    }
                    for strategy in strategies
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "strategies": []
            }
    
    async def _create_campaign_plan(
        self, 
        strategies: List[Dict[str, Any]], 
        store_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """캠페인 계획 생성"""
        try:
            try:
                from .strategy_generator import MarketingStrategy
            except ImportError:
                from strategy_generator import MarketingStrategy
            
            # MarketingStrategy 객체들 생성
            strategy_objects = []
            for strategy_data in strategies:
                strategy = MarketingStrategy(
                    strategy_id=strategy_data["strategy_id"],
                    name=strategy_data["name"],
                    description=strategy_data["description"],
                    target_persona="",  # 필요시 설정
                    risk_codes=strategy_data["risk_codes"],
                    channel=strategy_data["channel"],
                    tactics=strategy_data["tactics"],
                    expected_impact=strategy_data["expected_impact"],
                    implementation_time=strategy_data["implementation_time"],
                    budget_estimate=strategy_data["budget_estimate"],
                    success_metrics=[],  # 필요시 설정
                    priority=strategy_data["priority"]
                )
                strategy_objects.append(strategy)
            
            campaign_plan = await self.marketing_agent.strategy_generator.generate_campaign_plan(
                strategies=strategy_objects,
                store_data=store_data,
                campaign_duration="1개월"
            )
            
            return {
                "success": True,
                "campaign_plan": {
                    "campaign_id": campaign_plan.campaign_id,
                    "name": campaign_plan.name,
                    "description": campaign_plan.description,
                    "duration": campaign_plan.duration,
                    "budget_allocation": campaign_plan.budget_allocation,
                    "timeline": campaign_plan.timeline,
                    "expected_kpis": campaign_plan.expected_kpis,
                    "success_probability": campaign_plan.success_probability
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "campaign_plan": None
            }
    
    async def _generate_query_response(
        self, 
        query: str, 
        store_report: Dict[str, Any], 
        diagnostic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """쿼리 응답 생성"""
        try:
            result = await self.marketing_agent.generate_query_response(
                query=query,
                store_report=store_report,
                diagnostic=diagnostic
            )
            return {
                "success": True,
                "response": result["response"],
                "analysis_data": result.get("analysis_data")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"응답 생성 중 오류가 발생했습니다: {str(e)}"
            }


class MarketingAgentOrchestrator:
    """마케팅 에이전트 오케스트레이터 - 전체 플로우 관리"""
    
    def __init__(self):
        self.agents = {}
    
    async def create_agent(self, store_code: str) -> MarketingAgentWrapper:
        """매장별 마케팅 에이전트 생성"""
        if store_code not in self.agents:
            self.agents[store_code] = MarketingAgentWrapper(store_code)
        return self.agents[store_code]
    
    async def process_marketing_analysis(
        self, 
        store_code: str, 
        store_report: Dict[str, Any], 
        diagnostic: Dict[str, Any],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """마케팅 분석 전체 플로우 실행"""
        try:
            # 에이전트 생성 또는 가져오기
            agent = await self.create_agent(store_code)
            
            # 기본 쿼리 설정
            if not query:
                query = f"{store_code}의 가장 큰 문제점과 이를 보완할 마케팅 아이디어와 근거는 무엇인가?"
            
            # 마케팅 분석 실행
            result = await agent.process_query(query, store_report, diagnostic)
            
            return {
                "store_code": store_code,
                "success": result["success"],
                "query": query,
                "response": result["response"],
                "timestamp": result.get("timestamp"),
                "context": result.get("context")
            }
            
        except Exception as e:
            return {
                "store_code": store_code,
                "success": False,
                "error": f"마케팅 분석 오케스트레이션 중 오류: {str(e)}",
                "query": query,
                "response": None
            }
