"""
Marketing Module - 통합 마케팅 에이전트
모든 마케팅 관련 로직을 통합하여 marketing_result.json과 marketing_strategy.json을 생성
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# OpenAI SDK import
from openai import OpenAI

# Marketing Module components
try:
    from .marketing_agent import marketingagent
    from .persona_engine import PersonaEngine
    from .risk_analyzer import RiskAnalyzer
    from .strategy_generator import StrategyGenerator
    from .dynamic_persona_generator import DynamicPersonaGenerator
except ImportError:
    # 독립 실행될 때
    from marketing_agent import marketingagent
    from persona_engine import PersonaEngine
    from risk_analyzer import RiskAnalyzer
    from strategy_generator import StrategyGenerator
    from dynamic_persona_generator import DynamicPersonaGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한글 폰트 설정
import matplotlib.pyplot as plt
import platform

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

class MarketingModule:
    """통합 마케팅 모듈"""
    
    def __init__(self, store_code: str, analysis_dir: str):
        self.store_code = store_code
        self.analysis_dir = Path(analysis_dir)
        
        # Gemini API 키 확인 및 클라이언트 초기화
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY or GOOGLE_API_KEY not found. Marketing Module will use basic functionality.")
            self.client = None
        else:
            try:
                # OpenAI SDK로 Gemini 2.5 Flash 사용
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta"
                )
                logger.info("OpenAI client with Gemini 2.5 Flash initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client with Gemini: {str(e)}")
                self.client = None
        
        # Ensure analysis directory exists
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_marketing_analysis(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        마케팅 분석 실행 및 결과 저장
        
        Args:
            store_analysis: 매장 분석 데이터
            
        Returns:
            마케팅 분석 결과
        """
        try:
            logger.info(f"Starting marketing analysis for store: {self.store_code}")
            
            # API 키가 없으면 기본 결과 반환
            if not self.client:
                logger.warning("No OpenAI client available. Returning basic marketing result.")
                basic_result = self._get_basic_marketing_result(store_analysis)
                await self._save_results(basic_result)
                return basic_result
            
            # Marketing Module 실행 (Gemini 2.5 Flash 사용)
            agent = marketingagent(self.store_code, self.client)
            
            # Store analysis를 marketing format으로 변환
            store_report = self._convert_store_to_marketing_format(store_analysis)
            
            # Diagnostic 데이터 생성
            diagnostic = {
                "overall_risk_level": "MEDIUM",
                "detected_risks": [],
                "diagnostic_results": {}
            }
            
            # Marketing Module 실행
            marketing_result = await agent.run_marketing(store_report, diagnostic)
            
            if marketing_result and not marketing_result.get("error"):
                # Enum을 문자열로 변환
                marketing_result = self._convert_enums_to_strings(marketing_result)
                
                # 추가 데이터 생성
                marketing_result["analysis_timestamp"] = datetime.now().isoformat()
                marketing_result["channel_recommendation"] = await self._recommend_channels(store_analysis, marketing_result.get("persona_analysis", {}))
                marketing_result["marketing_focus_points"] = self._get_marketing_focus_points(store_analysis)
                marketing_result["social_content"] = await self._generate_social_content(store_analysis, marketing_result.get("persona_analysis", {}))
                marketing_result["recommendations"] = self._get_recommendations(marketing_result, marketing_result.get("risk_analysis", {}))
                marketing_result["formatted_output"] = self._generate_formatted_output(store_analysis, marketing_result.get("persona_analysis", {}), marketing_result.get("risk_analysis", {}), marketing_result)
                
                # 결과 저장
                await self._save_results(marketing_result)
                
                logger.info("Marketing analysis completed successfully")
                return marketing_result
            else:
                logger.error(f"Marketing module failed: {marketing_result.get('error', 'Unknown error')}")
                return self._get_basic_marketing_result(store_analysis)
            
        except Exception as e:
            logger.error(f"Marketing analysis failed: {str(e)}")
            return self._get_basic_marketing_result(store_analysis)
    
    async def _analyze_persona(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """페르소나 분석"""
        try:
            # Dynamic Persona Generator 사용
            persona_generator = DynamicPersonaGenerator()
            persona_result = await persona_generator.generate_persona(store_analysis)
            return persona_result
        except Exception as e:
            logger.error(f"Persona analysis failed: {str(e)}")
            # Fallback to basic persona
            return self._get_basic_persona(store_analysis)
    
    async def _analyze_risks(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """위험 분석"""
        try:
            # Marketing Module의 RiskAnalyzer 사용
            agent = marketingagent(self.store_code)
            risk_result = await agent.analyze_risks(store_analysis)
            return risk_result
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            return self._get_basic_risk_analysis()
    
    async def _generate_strategies(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any], risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """마케팅 전략 생성"""
        try:
            # Marketing Module의 StrategyGenerator 사용
            agent = marketingagent(self.store_code)
            strategies = await agent.generate_strategies(store_analysis, persona_result, risk_result)
            campaign_plan = await agent.generate_campaign_plan(strategies)
            
            return {
                "strategies": strategies,
                "campaign_plan": campaign_plan
            }
        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            return self._get_basic_strategies()
    
    async def _recommend_channels(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any]) -> Dict[str, Any]:
        """채널 추천"""
        try:
            # SNS 사용률 데이터 로드
            sns_data = self._load_sns_data()
            
            # 페르소나 기반 채널 추천
            persona_type = persona_result.get("persona_type", "")
            customer_demographics = persona_result.get("components", {}).get("customer_demographics", {})
            
            # 기본 채널 추천 로직
            recommended_channels = self._get_recommended_channels(customer_demographics, sns_data)
            
            return recommended_channels
        except Exception as e:
            logger.error(f"Channel recommendation failed: {str(e)}")
            return self._get_basic_channel_recommendation()
    
    async def _generate_social_content(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any]) -> Dict[str, Any]:
        """소셜 콘텐츠 생성"""
        try:
            # Gemini 2.5 Flash를 사용한 소셜 콘텐츠 생성
            content_prompt = self._create_social_content_prompt(store_analysis, persona_result)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 소셜미디어 마케터입니다. 매장의 특성과 페르소나에 맞는 매력적인 소셜 콘텐츠를 생성해주세요."},
                    {"role": "user", "content": content_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                return json.loads(content)
            except:
                # JSON 파싱 실패 시 기본 구조 반환
                return self._parse_social_content(content)
                
        except Exception as e:
            logger.error(f"Social content generation failed: {str(e)}")
            return self._get_basic_social_content()
    
    def _load_sns_data(self) -> Dict[str, Any]:
        """SNS 사용률 데이터 로드"""
        try:
            sns_file = Path("data/segment_sns.json")
            if sns_file.exists():
                with open(sns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load SNS data: {str(e)}")
        
        return {}
    
    def _get_recommended_channels(self, demographics: Dict[str, Any], sns_data: Dict[str, Any]) -> Dict[str, Any]:
        """채널 추천 로직"""
        # 기본 채널 추천
        channels = {
            "channels": "인스타그램 + 배달앱",
            "primary_channel": "인스타그램",
            "usage_rate": 72.2,
            "reasoning": "타겟 고객층의 주요 사용 채널",
            "avoid_channels": ["카카오스토리"],
            "channel_data": [
                {
                    "rank": 1,
                    "channel": "인스타그램",
                    "usage_percent": 72.2,
                    "trend_label": "상승",
                    "trend_emoji": "📈",
                    "total_change": 65.7,
                    "recommendation": "추천"
                }
            ],
            "source": "2024년 미디어통계포털"
        }
        
        return channels
    
    def _get_marketing_focus_points(self, store_analysis: Dict[str, Any]) -> Dict[str, str]:
        """마케팅 포커스 포인트"""
        return {
            "industry_focus": "신뢰·품질 중심",
            "zone_focus": "단골/재방문 유도",
            "customer_type_focus": "단골 관리, 적립제·멤버십"
        }
    
    def _get_recommendations(self, strategy_result: Dict[str, Any], risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """추천사항"""
        return {
            "immediate_actions": [
                "즉시 실행: 첫 번째 전략",
                "예상 효과: 매출 증대 및 고객 만족도 향상",
                "예산: 중간",
                "구현 기간: 1-2주"
            ],
            "short_term_goals": [
                "위험 코드 해결을 위한 단계적 접근",
                "페르소나별 맞춤 마케팅 채널 최적화",
                "고객 만족도 및 리뷰 점수 개선"
            ],
            "long_term_strategy": [
                "브랜드 이미지 및 고객 충성도 구축",
                "지속 가능한 성장 모델 수립",
                "시장 경쟁력 강화 및 차별화"
            ],
            "success_factors": [
                "페르소나 기반 맞춤형 접근",
                "데이터 기반 의사결정",
                "지속적인 모니터링 및 개선",
                "고객 피드백 반영"
            ]
        }
    
    def _generate_formatted_output(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any], 
                                 risk_result: Dict[str, Any], strategy_result: Dict[str, Any]) -> str:
        """포맷된 출력 생성"""
        try:
            # Gemini 2.5 Flash를 사용한 포맷된 보고서 생성
            report_prompt = self._create_report_prompt(store_analysis, persona_result, risk_result, strategy_result)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 마케팅 컨설턴트입니다. 매장 분석 데이터를 바탕으로 상세하고 실용적인 마케팅 보고서를 작성해주세요."},
                    {"role": "user", "content": report_prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Formatted output generation failed: {str(e)}")
            return self._get_basic_formatted_output(store_analysis, persona_result, risk_result, strategy_result)
    
    def _create_social_content_prompt(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any]) -> str:
        """소셜 콘텐츠 생성 프롬프트"""
        return f"""
        매장 정보: {store_analysis.get('store_name', 'N/A')}
        업종: {store_analysis.get('industry', 'N/A')}
        페르소나: {persona_result.get('persona_type', 'N/A')}
        
        위 정보를 바탕으로 인스타그램 포스트 3개를 생성해주세요.
        각 포스트는 제목, 내용, 해시태그, 포스트 타입을 포함해야 합니다.
        
        JSON 형식으로 응답해주세요:
        {{
            "instagram_posts": [
                {{
                    "title": "포스트 제목",
                    "content": "포스트 내용",
                    "hashtags": ["#해시태그1", "#해시태그2"],
                    "post_type": "feed"
                }}
            ],
            "facebook_posts": [],
            "promotion_texts": []
        }}
        """
    
    def _create_report_prompt(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any], 
                            risk_result: Dict[str, Any], strategy_result: Dict[str, Any]) -> str:
        """보고서 생성 프롬프트"""
        return f"""
        매장 분석 데이터를 바탕으로 상세한 마케팅 보고서를 작성해주세요.
        
        매장 정보: {store_analysis.get('store_name', 'N/A')}
        업종: {store_analysis.get('industry', 'N/A')}
        페르소나: {persona_result.get('persona_type', 'N/A')}
        위험 요소: {len(risk_result.get('detected_risks', []))}개
        전략 수: {len(strategy_result.get('strategies', []))}개
        
        다음 섹션을 포함해주세요:
        1. 종합 결론
        2. 홍보 아이디어
        3. 타겟 전략
        4. 마케팅 채널 전략
        5. 핵심 인사이트
        6. 다음 단계 제안
        
        마크다운 형식으로 작성해주세요.
        """
    
    def _parse_social_content(self, content: str) -> Dict[str, Any]:
        """소셜 콘텐츠 파싱"""
        return {
            "instagram_posts": [
                {
                    "title": "매장 소개",
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "hashtags": ["#매장", "#맛집"],
                    "post_type": "feed"
                }
            ],
            "facebook_posts": [],
            "promotion_texts": []
        }
    
    async def _save_results(self, marketing_result: Dict[str, Any]) -> None:
        """결과 저장"""
        try:
            # marketing_result.json 저장
            result_file = self.analysis_dir / "marketing_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(marketing_result, f, ensure_ascii=False, indent=2)
            logger.info(f"Marketing result saved: {result_file}")
            
            # marketing_strategy.json 저장 (전략만)
            strategy_data = {
                "store_code": self.store_code,
                "analysis_timestamp": marketing_result["analysis_timestamp"],
                "persona_analysis": marketing_result["persona_analysis"],
                "risk_analysis": marketing_result["risk_analysis"],
                "marketing_strategies": marketing_result["marketing_strategies"],
                "campaign_plan": marketing_result["campaign_plan"],
                "channel_recommendation": marketing_result["channel_recommendation"],
                "marketing_focus_points": marketing_result["marketing_focus_points"],
                "social_content": marketing_result["social_content"],
                "recommendations": marketing_result["recommendations"],
                "formatted_output": marketing_result["formatted_output"]
            }
            
            strategy_file = self.analysis_dir / "marketing_strategy.json"
            with open(strategy_file, 'w', encoding='utf-8') as f:
                json.dump(strategy_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Marketing strategy saved: {strategy_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            raise
    
    # Fallback methods for error handling
    def _get_basic_persona(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """기본 페르소나"""
        return {
            "persona_type": "일반_고객",
            "persona_description": "일반적인 매장 고객",
            "components": {
                "industry": store_analysis.get("industry", "N/A"),
                "commercial_zone": "일반",
                "is_franchise": False,
                "store_age": "안정기",
                "customer_demographics": {"gender": "혼합", "age": "혼합"},
                "customer_type": "거주형",
                "trends": {"new_customer": "정체", "revisit": "정체"},
                "delivery_ratio": "중간"
            },
            "marketing_tone": "친근하고 신뢰감을 주는",
            "key_channels": ["인스타그램", "네이버 플레이스"],
            "core_insights": {
                "persona": {"summary": "일반적인 고객층"},
                "risk_diagnosis": {"summary": "위험 요소 없음", "table_data": []}
            }
        }
    
    def _get_basic_risk_analysis(self) -> Dict[str, Any]:
        """기본 위험 분석"""
        return {
            "overall_risk_level": "낮음",
            "detected_risks": [],
            "analysis_summary": "특별한 위험 요소가 감지되지 않았습니다."
        }
    
    def _get_basic_strategies(self) -> Dict[str, Any]:
        """기본 전략"""
        return {
            "strategies": [
                {
                    "strategy_id": "BASIC_STRAT_1",
                    "name": "기본 마케팅 전략",
                    "description": "기본적인 마케팅 전략을 실행합니다.",
                    "risk_codes": [],
                    "channel": "다양한 채널",
                    "tactics": ["기본 마케팅 활동"],
                    "expected_impact": "매출 증대",
                    "implementation_time": "1-2주",
                    "budget_estimate": "낮음",
                    "success_metrics": ["매출 증가"],
                    "priority": 1
                }
            ],
            "campaign_plan": {
                "campaign_id": "BASIC_CAMP",
                "name": "기본 캠페인",
                "description": "기본 마케팅 캠페인",
                "duration": "1개월",
                "budget_allocation": {"다양한 채널": 100.0},
                "timeline": [],
                "expected_kpis": {},
                "success_probability": 0.5
            }
        }
    
    def _get_basic_channel_recommendation(self) -> Dict[str, Any]:
        """기본 채널 추천"""
        return {
            "channels": "인스타그램 + 네이버 플레이스",
            "primary_channel": "인스타그램",
            "usage_rate": 50.0,
            "reasoning": "일반적인 추천 채널",
            "avoid_channels": [],
            "channel_data": [
                {
                    "rank": 1,
                    "channel": "인스타그램",
                    "usage_percent": 50.0,
                    "trend_label": "안정",
                    "trend_emoji": "➡️",
                    "total_change": 0.0,
                    "recommendation": "추천"
                }
            ],
            "source": "기본 추천"
        }
    
    def _get_basic_social_content(self) -> Dict[str, Any]:
        """기본 소셜 콘텐츠"""
        return {
            "instagram_posts": [
                {
                    "title": "매장 소개",
                    "content": "저희 매장을 방문해주셔서 감사합니다.",
                    "hashtags": ["#매장", "#맛집"],
                    "post_type": "feed"
                }
            ],
            "facebook_posts": [],
            "promotion_texts": []
        }
    
    def _get_basic_formatted_output(self, store_analysis: Dict[str, Any], persona_result: Dict[str, Any], 
                                  risk_result: Dict[str, Any], strategy_result: Dict[str, Any]) -> str:
        """기본 포맷된 출력"""
        return f"""
        # 마케팅 분석 보고서
        
        ## 매장 정보
        - 매장명: {store_analysis.get('store_name', 'N/A')}
        - 업종: {store_analysis.get('industry', 'N/A')}
        
        ## 페르소나 분석
        - 페르소나 타입: {persona_result.get('persona_type', 'N/A')}
        
        ## 위험 분석
        - 전체 위험 수준: {risk_result.get('overall_risk_level', 'N/A')}
        
        ## 마케팅 전략
        - 전략 수: {len(strategy_result.get('strategies', []))}개
        
        ## 추천사항
        1. 기본적인 마케팅 활동을 시작하세요.
        2. 고객 피드백을 수집하고 개선하세요.
        3. 정기적인 마케팅 성과를 모니터링하세요.
        """
    
    def _convert_store_to_marketing_format(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Store analysis를 marketing format으로 변환"""
        try:
            # 기본 변환 로직
            return {
                "store_code": self.store_code,
                "store_name": store_analysis.get("store_name", "N/A"),
                "industry": store_analysis.get("industry", "N/A"),
                "commercial_zone": store_analysis.get("commercial_zone", "N/A"),
                "is_franchise": store_analysis.get("is_franchise", False),
                "store_age": store_analysis.get("store_age", "N/A"),
                "customer_demographics": store_analysis.get("customer_demographics", {}),
                "customer_type": store_analysis.get("customer_type", "N/A"),
                "trends": store_analysis.get("trends", {}),
                "delivery_ratio": store_analysis.get("delivery_ratio", "N/A")
            }
        except Exception as e:
            logger.error(f"Store format conversion failed: {str(e)}")
            return {}
    
    def _convert_enums_to_strings(self, obj: Any) -> Any:
        """Enum을 문자열로 변환"""
        if isinstance(obj, dict):
            return {key: self._convert_enums_to_strings(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_enums_to_strings(item) for item in obj]
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        else:
            return obj
    
    def _get_basic_marketing_result(self, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """기본 마케팅 결과"""
        return {
            "store_code": self.store_code,
            "analysis_timestamp": datetime.now().isoformat(),
            "persona_analysis": self._get_basic_persona(store_analysis),
            "risk_analysis": self._get_basic_risk_analysis(),
            "marketing_strategies": self._get_basic_strategies()["strategies"],
            "campaign_plan": self._get_basic_strategies()["campaign_plan"],
            "channel_recommendation": self._get_basic_channel_recommendation(),
            "marketing_focus_points": self._get_marketing_focus_points(store_analysis),
            "social_content": self._get_basic_social_content(),
            "recommendations": self._get_recommendations({}, {}),
            "formatted_output": self._get_basic_formatted_output(store_analysis, {}, {}, {})
        }
    
    def _expand_channel_details(self, channel: str) -> Dict[str, Any]:
        """채널 상세 정보 확장"""
        try:
            # StrategyGenerator를 사용하여 채널 상세 정보 확장
            from .strategy_generator import StrategyGenerator
            sg = StrategyGenerator()
            return sg.expand_channel_details(channel)
        except Exception as e:
            logger.error(f"Channel details expansion failed: {str(e)}")
            # 기본 채널 정보 반환
            return {
                "online_channels": [channel],
                "offline_channels": [],
                "description": f"{channel} 채널 상세 정보"
            }


# 편의 함수
async def run_marketing_analysis(store_code: str, analysis_dir: str, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    마케팅 분석 실행 편의 함수
    
    Args:
        store_code: 매장 코드
        analysis_dir: 분석 결과 저장 디렉토리
        store_analysis: 매장 분석 데이터
        
    Returns:
        마케팅 분석 결과
    """
    marketing_module = MarketingModule(store_code, analysis_dir)
    return await marketing_module.run_marketing_analysis(store_analysis)

def run_marketing_sync(store_code: str, analysis_dir: str, store_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    마케팅 분석 실행 동기 함수 (asyncio.run 사용)
    
    Args:
        store_code: 매장 코드
        analysis_dir: 분석 결과 저장 디렉토리
        store_analysis: 매장 분석 데이터
        
    Returns:
        마케팅 분석 결과
    """
    import asyncio
    return asyncio.run(run_marketing_analysis(store_code, analysis_dir, store_analysis))


if __name__ == "__main__":
    # 테스트용
    import asyncio
    
    async def test():
        store_analysis = {
            "store_name": "테스트 매장",
            "industry": "카페",
            "store_code": "TEST001"
        }
        
        result = await run_marketing_analysis("TEST001", "test_output", store_analysis)
        print("Marketing analysis completed!")
        print(f"Result keys: {list(result.keys())}")
    
    asyncio.run(test())
