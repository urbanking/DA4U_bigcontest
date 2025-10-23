"""
동적 페르소나 생성기 - AI 기반 맞춤형 페르소나 생성
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import asyncio
from datetime import datetime

# 순환 import 방지를 위해 TYPE_CHECKING 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    try:
        # 패키지로 실행될 때
        from .persona_engine import PersonaComponents, IndustryType, CommercialZone, CustomerType, StoreAge
    except ImportError:
        # 독립 실행될 때
        from persona_engine import PersonaComponents, IndustryType, CommercialZone, CustomerType, StoreAge

import sys
from pathlib import Path
import os

# Langfuse tracing 추가 (올바른 방식)
try:
    from langfuse import observe
    from langfuse.openai import openai as langfuse_openai
    LANGFUSE_AVAILABLE = True
    print("[OK] Langfuse initialized in DynamicPersonaGenerator")
except ImportError:
    print("[WARN] Langfuse not available in DynamicPersonaGenerator - tracing disabled")
    LANGFUSE_AVAILABLE = False
    langfuse_openai = None

# GeminiClient import (utils에서 가져오기)
try:
    # agents_new/utils/gemini_client.py에서 import
    sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
    from gemini_client import GeminiClient
except ImportError:
    # Fallback: 간단한 로컬 구현
    import aiohttp
    
    class GeminiClient:
        """Fallback Gemini API 클라이언트"""
        
        def __init__(self):
            self.api_key = os.getenv('GEMINI_API_KEY', '')
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        async def generate_content_async(self, prompt: str, **kwargs):
            """Gemini API 호출"""
            if not self.api_key:
                from types import SimpleNamespace
                return SimpleNamespace(text="Gemini API 키가 설정되지 않았습니다.")
            
            try:
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/models/gemini-2.5-flash:generateContent",
                        headers=headers,
                        json=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            text = result["candidates"][0]["content"]["parts"][0]["text"]
                            from types import SimpleNamespace
                            return SimpleNamespace(text=text)
                        else:
                            error_text = await response.text()
                            from types import SimpleNamespace
                            return SimpleNamespace(text=f"API 오류: {response.status} - {error_text}")
            
            except Exception as e:
                from types import SimpleNamespace
                return SimpleNamespace(text=f"Gemini API 호출 실패: {str(e)}")

# Langfuse tracing (선택적)
LANGFUSE_AVAILABLE = False
langfuse_client = None
try:
    from langfuse import Langfuse
    # API 키가 있을 때만 초기화
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        langfuse_client = Langfuse()
        LANGFUSE_AVAILABLE = True
except (ImportError, Exception):
    # Langfuse가 없거나 초기화 실패해도 동작하도록 함
    pass


@dataclass
class DynamicPersona:
    """동적으로 생성된 페르소나"""
    persona_name: str
    description: str
    characteristics: Dict[str, Any]
    target_demographics: Dict[str, str]
    behavioral_patterns: List[str]
    pain_points: List[str]
    motivations: List[str]
    marketing_tone: str
    key_channels: List[str]
    strategies: List[str]
    risk_codes: List[str]
    confidence_score: float
    generated_at: str


class DynamicPersonaGenerator:
    """AI 기반 동적 페르소나 생성기"""
    
    def __init__(self):
        try:
            self.gemini_client = GeminiClient()
        except Exception as e:
            print(f"[WARN] GeminiClient 초기화 실패: {e}")
            self.gemini_client = None
        self.persona_cache = {}  # 생성된 페르소나 캐시
    
    @observe()
    async def generate_dynamic_persona(
        self, 
        store_data: Dict[str, Any], 
        persona_components: "PersonaComponents",
        risk_codes: List[str] = None
    ) -> DynamicPersona:
        """매장 데이터를 기반으로 동적 페르소나 생성"""
        
        # GeminiClient가 없으면 폴백
        if not self.gemini_client:
            print("[WARN] GeminiClient 없음, 기본 페르소나 사용")
            return self._create_fallback_persona(store_data, persona_components)
        
        # Langfuse tracing 시작 (선택적)
        trace_id = None
        if LANGFUSE_AVAILABLE and langfuse_client:
            try:
                trace_id = langfuse_client.trace(
                    name="Dynamic_Persona_Generation",
                    input={
                        "store_data": store_data,
                        "risk_codes": risk_codes or []
                    },
                    metadata={
                        "agent_type": "DynamicPersonaGenerator"
                    }
                )
            except Exception:
                # Langfuse 실패해도 계속 진행
                pass
        
        # 캐시 확인
        cache_key = self._generate_cache_key(store_data, persona_components)
        if cache_key in self.persona_cache:
            if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Cache_Hit",
                    input_data={"cache_key": cache_key},
                    output_data={"cached_persona": self.persona_cache[cache_key].persona_name},
                    metadata={"cache_status": "hit"}
                )
            return self.persona_cache[cache_key]
        
        try:
            # 1. 페르소나 분석 프롬프트 생성
            analysis_prompt = self._create_analysis_prompt(store_data, persona_components, risk_codes)
            
            if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Prompt_Generation",
                    input_data={"store_data": store_data, "persona_components": persona_components.__dict__},
                    output_data={"prompt_length": len(analysis_prompt)},
                    metadata={"step": "1", "description": "페르소나 분석 프롬프트 생성"}
                )
            
            # 2. LLM을 통한 페르소나 분석
            analysis_result = await self._analyze_with_llm(analysis_prompt, trace_id)
            
            # 3. 페르소나 구조화
            structured_persona = self._structure_persona(analysis_result, persona_components, risk_codes)
            
            if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Persona_Structuring",
                    input_data={"analysis_result": analysis_result},
                    output_data={"structured_persona": structured_persona},
                    metadata={"step": "3", "description": "분석 결과를 구조화된 페르소나로 변환"}
                )
            
            # 4. 전략 생성
            strategies = await self._generate_strategies(structured_persona, store_data, risk_codes, trace_id)
            structured_persona["strategies"] = strategies
            
            # 5. DynamicPersona 객체 생성
            dynamic_persona = DynamicPersona(
                persona_name=structured_persona["persona_name"],
                description=structured_persona["description"],
                characteristics=structured_persona["characteristics"],
                target_demographics=structured_persona["target_demographics"],
                behavioral_patterns=structured_persona["behavioral_patterns"],
                pain_points=structured_persona["pain_points"],
                motivations=structured_persona["motivations"],
                marketing_tone=structured_persona["marketing_tone"],
                key_channels=structured_persona["key_channels"],
                strategies=structured_persona["strategies"],
                risk_codes=risk_codes or [],
                confidence_score=structured_persona.get("confidence_score", 0.8),
                generated_at=datetime.now().isoformat()
            )
            
            # 캐시에 저장
            self.persona_cache[cache_key] = dynamic_persona
            
            # 최종 결과 추적
            if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Final_Persona_Creation",
                    input_data={"structured_persona": structured_persona},
                    output_data={
                        "persona_name": dynamic_persona.persona_name,
                        "confidence_score": dynamic_persona.confidence_score,
                        "strategy_count": len(dynamic_persona.strategies)
                    },
                    metadata={"step": "5", "description": "최종 DynamicPersona 객체 생성"}
                )
            
            return dynamic_persona
            
        except Exception as e:
            # 오류 추적
            if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Error_Fallback",
                    input_data={"error": str(e)},
                    output_data={"fallback_persona": "created"},
                    metadata={"error": True, "description": "오류 발생으로 기본 페르소나 생성"}
                )
            
            # 오류 시 기본 페르소나 반환
            return self._create_fallback_persona(persona_components, risk_codes)
    
    def _create_analysis_prompt(
        self, 
        store_data: Dict[str, Any], 
        persona_components: "PersonaComponents",
        risk_codes: List[str] = None
    ) -> str:
        """페르소나 분석을 위한 프롬프트 생성"""
        
        prompt = f"""
당신은 전문 마케팅 컨설턴트입니다. 주어진 매장 데이터를 분석하여 고유한 페르소나를 생성해주세요.

## 매장 기본 정보
- 업종: {persona_components.industry.value}
- 상권 유형: {persona_components.commercial_zone.value}
- 프랜차이즈 여부: {'예' if persona_components.is_franchise else '아니오'}
- 매장 단계: {persona_components.store_age.value}
- 주요 고객 성별: {persona_components.main_customer_gender}
- 주요 고객 연령: {persona_components.main_customer_age}
- 고객 유형: {persona_components.customer_type.value}
- 신규 고객 트렌드: {persona_components.new_customer_trend}
- 재방문 트렌드: {persona_components.revisit_trend}
- 배달 비중: {persona_components.delivery_ratio}

## 매장 상세 데이터
{json.dumps(store_data, ensure_ascii=False, indent=2)}

## 위험 코드 (해결해야 할 문제점)
{risk_codes if risk_codes else "없음"}

## 요청사항
위 정보를 바탕으로 다음 JSON 형식으로 페르소나를 생성해주세요:

{{
    "persona_name": "매장의 고유한 페르소나 이름 (예: '도심_프리미엄_카페_워킹맘층')",
    "description": "페르소나에 대한 간단한 설명",
    "characteristics": {{
        "primary_traits": ["주요 특성 3-5개"],
        "secondary_traits": ["부차적 특성 3-5개"],
        "unique_selling_points": ["차별화 포인트 2-3개"]
    }},
    "target_demographics": {{
        "age_range": "연령대",
        "gender": "성별",
        "income_level": "소득 수준",
        "lifestyle": "라이프스타일",
        "location_preference": "위치 선호도"
    }},
    "behavioral_patterns": [
        "고객 행동 패턴 5-7개"
    ],
    "pain_points": [
        "고객의 주요 불만사항 3-5개"
    ],
    "motivations": [
        "고객의 구매 동기 3-5개"
    ],
    "marketing_tone": "마케팅 톤앤매너 (예: '감성적이고 프리미엄한')",
    "key_channels": [
        "주요 마케팅 채널 5-7개"
    ],
    "confidence_score": 0.85
}}

중요한 점:
1. 기존 템플릿에 얽매이지 말고 매장의 고유한 특성을 반영
2. 실제 데이터를 기반으로 현실적인 페르소나 생성
3. 위험 코드가 있다면 이를 해결할 수 있는 방향으로 페르소나 설계
4. 구체적이고 실행 가능한 마케팅 채널과 전략 제시
"""
        
        return prompt
    
    async def _analyze_with_llm(self, prompt: str, trace_id: str = None) -> Dict[str, Any]:
        """LLM을 통한 페르소나 분석"""
        
        # LLM 분석 시작 추적
        llm_span_id = None
        if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
            llm_span_id = langfuse_client.create_span(
                trace_id=trace_id,
                name="LLM_Persona_Analysis",
                input_data={"prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt},
                metadata={"step": "2", "description": "Gemini를 통한 페르소나 분석", "model": "gemini-2.5-flash"}
            )
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "당신은 전문 마케팅 컨설턴트입니다. 매장 데이터를 분석하여 고유한 페르소나를 생성하는 것이 전문 분야입니다."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = self.gemini_client.chat_completion_json(
                messages=messages,
                temperature=0.7,
                model="gemini-2.5-flash"
            )
            
            # JSON 파싱 (마크다운 코드 블록 제거)
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
                    
                    parsed_result = json.loads(response)
                    
                    # LLM 분석 결과 추적
                    if llm_span_id and LANGFUSE_AVAILABLE and langfuse_client:
                        langfuse_client.create_span(
                            trace_id=trace_id,
                            name="LLM_Response_Parsing",
                            input_data={"raw_response": response[:200] + "..." if len(response) > 200 else response},
                            output_data={"parsed_result": parsed_result},
                            metadata={"step": "2.1", "description": "LLM 응답 JSON 파싱"}
                        )
                    
                    return parsed_result
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                    print(f"응답 내용: {response[:200]}...")
                    
                    # 파싱 오류 추적
                    if llm_span_id and LANGFUSE_AVAILABLE and langfuse_client:
                        langfuse_client.create_span(
                            trace_id=trace_id,
                            name="JSON_Parsing_Error",
                            input_data={"error": str(e), "response": response[:200]},
                            output_data={"fallback": "default_analysis"},
                            metadata={"error": True, "description": "JSON 파싱 실패로 기본 분석 반환"}
                        )
                    
                    return self._get_default_analysis()
            else:
                return response
                
        except Exception as e:
            print(f"LLM 분석 오류: {e}")
            
            # LLM 오류 추적
            if llm_span_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="LLM_Analysis_Error",
                    input_data={"error": str(e)},
                    output_data={"fallback": "default_analysis"},
                    metadata={"error": True, "description": "LLM 분석 실패로 기본 분석 반환"}
                )
            
            return self._get_default_analysis()
    
    def _structure_persona(
        self, 
        analysis_result: Dict[str, Any], 
        persona_components: "PersonaComponents",
        risk_codes: List[str] = None
    ) -> Dict[str, Any]:
        """분석 결과를 구조화된 페르소나로 변환"""
        
        # 기본값 설정
        structured = {
            "persona_name": analysis_result.get("persona_name", f"{persona_components.industry.value}_{persona_components.commercial_zone.value}_매장"),
            "description": analysis_result.get("description", "동적으로 생성된 매장 페르소나"),
            "characteristics": analysis_result.get("characteristics", {
                "primary_traits": ["고객 중심", "품질 추구"],
                "secondary_traits": ["신뢰성", "편의성"],
                "unique_selling_points": ["차별화된 서비스"]
            }),
            "target_demographics": analysis_result.get("target_demographics", {
                "age_range": persona_components.main_customer_age,
                "gender": persona_components.main_customer_gender,
                "income_level": "중간",
                "lifestyle": "일반적",
                "location_preference": persona_components.commercial_zone.value
            }),
            "behavioral_patterns": analysis_result.get("behavioral_patterns", [
                "정기적인 방문",
                "가격 민감성",
                "편의성 추구"
            ]),
            "pain_points": analysis_result.get("pain_points", [
                "대기 시간",
                "가격 부담",
                "서비스 품질"
            ]),
            "motivations": analysis_result.get("motivations", [
                "편의성",
                "가성비",
                "신뢰성"
            ]),
            "marketing_tone": analysis_result.get("marketing_tone", "친근하고 신뢰할 수 있는"),
            "key_channels": analysis_result.get("key_channels", [
                "지역 광고",
                "구전",
                "온라인 리뷰"
            ]),
            "confidence_score": analysis_result.get("confidence_score", 0.7)
        }
        
        return structured
    
    @observe()
    async def _generate_strategies(
        self, 
        structured_persona: Dict[str, Any], 
        store_data: Dict[str, Any],
        risk_codes: List[str] = None,
        trace_id: str = None
    ) -> List[str]:
        """생성된 페르소나에 맞는 마케팅 전략 생성"""
        
        # 전략 생성 시작 추적
        strategy_span_id = None
        if trace_id and LANGFUSE_AVAILABLE and langfuse_client:
            strategy_span_id = langfuse_client.create_span(
                trace_id=trace_id,
                name="Strategy_Generation",
                input_data={
                    "persona_name": structured_persona.get("persona_name"),
                    "persona_characteristics": structured_persona.get("characteristics"),
                    "risk_codes": risk_codes or []
                },
                metadata={"step": "4", "description": "페르소나 기반 마케팅 전략 생성", "model": "gemini-2.5-flash"}
            )
        
        strategy_prompt = f"""
다음 페르소나에 맞는 구체적인 마케팅 전략을 생성해주세요:

## 페르소나 정보
- 이름: {structured_persona['persona_name']}
- 설명: {structured_persona['description']}
- 특성: {structured_persona['characteristics']}
- 타겟: {structured_persona['target_demographics']}
- 행동 패턴: {structured_persona['behavioral_patterns']}
- 불만사항: {structured_persona['pain_points']}
- 동기: {structured_persona['motivations']}
- 마케팅 톤: {structured_persona['marketing_tone']}
- 주요 채널: {structured_persona['key_channels']}

## 위험 코드 (해결해야 할 문제)
{risk_codes if risk_codes else "없음"}

## 매장 데이터
{json.dumps(store_data, ensure_ascii=False, indent=2)}

다음 형식으로 5-7개의 구체적인 마케팅 전략을 제시해주세요:
1. [전략명]: [구체적인 실행 방법] - [예상 효과]
2. [전략명]: [구체적인 실행 방법] - [예상 효과]
...

각 전략은:
- 페르소나의 특성과 맞아야 함
- 위험 코드를 해결할 수 있어야 함
- 구체적이고 실행 가능해야 함
- 예상 효과가 명확해야 함
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "당신은 전문 마케팅 전략가입니다. 페르소나에 맞는 구체적이고 실행 가능한 마케팅 전략을 제시하는 것이 전문 분야입니다."
                },
                {
                    "role": "user",
                    "content": strategy_prompt
                }
            ]
            
            response = self.gemini_client.chat_completion(
                messages=messages,
                temperature=0.8,
                model="gemini-2.5-flash"
            )
            
            # 응답을 리스트로 변환
            strategies = []
            lines = response.strip().split('\n')
            for line in lines:
                if line.strip() and (line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.'))):
                    strategies.append(line.strip())
            
            final_strategies = strategies if strategies else [
                "고객 맞춤형 서비스 강화",
                "디지털 마케팅 채널 확대",
                "고객 리텐션 프로그램 도입"
            ]
            
            # 전략 생성 결과 추적
            if strategy_span_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Strategy_Parsing",
                    input_data={"raw_response": response[:300] + "..." if len(response) > 300 else response},
                    output_data={"strategies": final_strategies, "strategy_count": len(final_strategies)},
                    metadata={"step": "4.1", "description": "LLM 응답을 전략 리스트로 변환"}
                )
            
            return final_strategies
            
        except Exception as e:
            print(f"전략 생성 오류: {e}")
            
            # 전략 생성 오류 추적
            if strategy_span_id and LANGFUSE_AVAILABLE and langfuse_client:
                langfuse_client.create_span(
                    trace_id=trace_id,
                    name="Strategy_Generation_Error",
                    input_data={"error": str(e)},
                    output_data={"fallback_strategies": "default"},
                    metadata={"error": True, "description": "전략 생성 실패로 기본 전략 반환"}
                )
            
            return [
                "고객 맞춤형 서비스 강화",
                "디지털 마케팅 채널 확대", 
                "고객 리텐션 프로그램 도입"
            ]
    
    def _generate_cache_key(self, store_data: Dict[str, Any], persona_components: "PersonaComponents") -> str:
        """캐시 키 생성"""
        key_data = {
            "industry": persona_components.industry.value,
            "commercial_zone": persona_components.commercial_zone.value,
            "is_franchise": persona_components.is_franchise,
            "store_age": persona_components.store_age.value,
            "customer_type": persona_components.customer_type.value,
            "main_customer_gender": persona_components.main_customer_gender,
            "main_customer_age": persona_components.main_customer_age
        }
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """기본 분석 결과 반환"""
        return {
            "persona_name": "일반_매장_페르소나",
            "description": "기본적인 매장 페르소나",
            "characteristics": {
                "primary_traits": ["고객 중심", "품질 추구"],
                "secondary_traits": ["신뢰성", "편의성"],
                "unique_selling_points": ["차별화된 서비스"]
            },
            "target_demographics": {
                "age_range": "30-50대",
                "gender": "혼합",
                "income_level": "중간",
                "lifestyle": "일반적",
                "location_preference": "주거형"
            },
            "behavioral_patterns": [
                "정기적인 방문",
                "가격 민감성",
                "편의성 추구"
            ],
            "pain_points": [
                "대기 시간",
                "가격 부담",
                "서비스 품질"
            ],
            "motivations": [
                "편의성",
                "가성비",
                "신뢰성"
            ],
            "marketing_tone": "친근하고 신뢰할 수 있는",
            "key_channels": [
                "지역 광고",
                "구전",
                "온라인 리뷰"
            ],
            "confidence_score": 0.5
        }
    
    def _create_fallback_persona(
        self, 
        persona_components: "PersonaComponents", 
        risk_codes: List[str] = None
    ) -> DynamicPersona:
        """오류 시 기본 페르소나 생성"""
        return DynamicPersona(
            persona_name=f"{persona_components.industry.value}_{persona_components.commercial_zone.value}_기본",
            description="기본 페르소나 (오류 발생 시)",
            characteristics={
                "primary_traits": ["고객 중심", "품질 추구"],
                "secondary_traits": ["신뢰성", "편의성"],
                "unique_selling_points": ["차별화된 서비스"]
            },
            target_demographics={
                "age_range": persona_components.main_customer_age,
                "gender": persona_components.main_customer_gender,
                "income_level": "중간",
                "lifestyle": "일반적",
                "location_preference": persona_components.commercial_zone.value
            },
            behavioral_patterns=["정기적인 방문", "가격 민감성", "편의성 추구"],
            pain_points=["대기 시간", "가격 부담", "서비스 품질"],
            motivations=["편의성", "가성비", "신뢰성"],
            marketing_tone="친근하고 신뢰할 수 있는",
            key_channels=["지역 광고", "구전", "온라인 리뷰"],
            strategies=["고객 맞춤형 서비스 강화", "디지털 마케팅 채널 확대"],
            risk_codes=risk_codes or [],
            confidence_score=0.3,
            generated_at=datetime.now().isoformat()
        )
    
    def get_persona_summary(self, dynamic_persona: DynamicPersona) -> Dict[str, Any]:
        """페르소나 요약 정보 반환"""
        return {
            "persona_name": dynamic_persona.persona_name,
            "description": dynamic_persona.description,
            "confidence_score": dynamic_persona.confidence_score,
            "key_characteristics": dynamic_persona.characteristics.get("primary_traits", []),
            "target_demographics": dynamic_persona.target_demographics,
            "marketing_tone": dynamic_persona.marketing_tone,
            "strategy_count": len(dynamic_persona.strategies),
            "generated_at": dynamic_persona.generated_at
        }
