"""
Gemini API Client using OpenAI Compatibility Layer
Reference: https://ai.google.dev/gemini-api/docs/openai
"""
import os
import asyncio
from types import SimpleNamespace
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Langfuse tracing 추가 (올바른 방식)
try:
    from langfuse import observe
    from langfuse.openai import openai as langfuse_openai
    LANGFUSE_AVAILABLE = True
    print("[OK] Langfuse initialized in GeminiClient")
except ImportError:
    print("[WARN] Langfuse not available in GeminiClient - tracing disabled")
    LANGFUSE_AVAILABLE = False
    langfuse_openai = None

# 환경변수 로드 (최신 키 사용을 위해 매번 로드)
def load_env_with_override():
    try:
        # 프로젝트 루트의 env 파일 찾기
        current_path = Path(__file__)
        root_path = current_path
        while root_path.parent != root_path:
            root_path = root_path.parent
            env_path = root_path / "env"
            if env_path.exists():
                load_dotenv(env_path, override=True)
                return
        # fallback
        load_dotenv(override=True)
    except Exception:
        pass

load_env_with_override()


class GeminiClient:
    """Gemini API client using OpenAI compatibility"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client with OpenAI compatibility layer
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        # 환경변수 다시 로드하여 최신 키 사용
        load_env_with_override()
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .env file or pass as parameter"
            )
        
        # API 키 로드 확인을 위한 로깅
        print(f"[GeminiClient] Using API key: {self.api_key[:20]}...")
        
        # Initialize OpenAI client with Gemini endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    async def generate_content_async(self, prompt: str, *, json_only: bool = True, **kwargs) -> Any:
        """
        Async helper matching google-generativeai-style API used in agents.

        - Wraps chat completion call in a thread to avoid blocking.
        - Optionally enforces JSON-only responses to simplify downstream parsing.

        Returns an object with a `.text` attribute containing the model output.
        """
        system = (
            "You are a helpful assistant."
            if not json_only
            else "You are a helpful assistant that responds with valid JSON only. No markdown fences or commentary."
        )
        user = prompt if not json_only else f"{prompt}\n\nReturn only valid JSON. No code fences."

        def _call() -> str:
            return self.chat_completion(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                **kwargs,
            )

        content = await asyncio.to_thread(_call)
        # Match expected interface: object with `.text`
        return SimpleNamespace(text=content or "")
        
    @observe()
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate chat completion using Gemini
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Gemini model name (default: gemini-2.0-flash-exp)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            reasoning_effort: Thinking level - "low", "medium", "high", or None
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        # Default model: prefer 2.5, allow env override
        if model is None:
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if reasoning_effort:
            params["reasoning_effort"] = reasoning_effort
            
        params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            content = response.choices[0].message.content
            
            # 빈 응답 체크
            if content is None or content.strip() == "":
                raise RuntimeError("Gemini returned empty response")
            
            return content
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    @observe()
    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate JSON-formatted response
        
        Args:
            messages: List of message dicts
            model: Gemini model name
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            JSON string response
        """
        # Add JSON instruction to system message
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanations."
        else:
            messages.insert(0, {
                "role": "system",
                "content": "You are a helpful assistant that responds in valid JSON format only. No markdown, no explanations."
            })
        
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs
        )
    
    def chat_completion_with_thinking(
        self,
        messages: List[Dict[str, str]],
        thinking_budget: Optional[int] = None,
        include_thoughts: bool = False,
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response with thinking/reasoning
        
        Args:
            messages: List of message dicts
            thinking_budget: Exact thinking token budget (alternative to reasoning_effort)
            include_thoughts: Whether to include thought process in response
            model: Gemini thinking model name
            **kwargs: Additional parameters
            
        Returns:
            Dict with 'content' and optionally 'thoughts'
        """
        extra_body = {}
        
        if thinking_budget is not None:
            extra_body = {
                'google': {
                    'thinking_config': {
                        'thinking_budget': thinking_budget,
                        'include_thoughts': include_thoughts
                    }
                }
            }
        
        # Default thinking model (allow env override or fallback)
        if model is None:
            model = os.getenv("GEMINI_THINKING_MODEL", "gemini-2.5-flash-thinking")

        params = {
            "model": model,
            "messages": messages,
        }
        
        if extra_body:
            params["extra_body"] = extra_body
            
        params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            result = {
                "content": response.choices[0].message.content
            }
            
            # Extract thoughts if included
            if include_thoughts and hasattr(response.choices[0].message, 'thoughts'):
                result["thoughts"] = response.choices[0].message.thoughts
                
            return result
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")


# Global client instance
_global_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create global Gemini client instance (with fresh API key reload)"""
    global _global_client
    
    # 항상 새로운 환경변수로 클라이언트 재생성 (API 키 변경 대응)
    load_env_with_override()
    
    # 클라이언트 강제 재생성 (API 키 변경 시 필요한 경우)
    current_api_key = os.getenv("GEMINI_API_KEY")
    if _global_client is None or (_global_client.api_key != current_api_key):
        _global_client = GeminiClient()
        print(f"[GeminiClient] Client refreshed with new API key")
    
    return _global_client

