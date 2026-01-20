"""
Zhipu AI GLM Client

Client for GLM-4.7 and related models from Zhipu AI (Z.AI).
Optimized for coding, math reasoning, and long-form report generation.

Key capabilities:
- 200K context window
- 128K output capacity (massive reports in one call)
- Strong math reasoning (95.7% AIME)
- Cost-effective: ~$0.60/1M input, ~$2.20/1M output
- Interleaved/Preserved Thinking for multi-turn stability

Best for:
- Code generation and multi-file engineering
- Financial calculations and data processing
- Long-form report generation
- Mathematical reasoning tasks
"""

import httpx
from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum

from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


class GLMModel(str, Enum):
    """Available GLM models."""
    GLM_4_7 = "glm-4.7"           # Flagship: 200K context, 128K output
    GLM_4_7_THINKING = "glm-4.7-thinking"  # Extended thinking mode
    GLM_4_5 = "glm-4.5"           # Previous gen, still capable
    GLM_4_5_FLASH = "glm-4.5-flash"  # Fast, cheaper


@dataclass
class GLMResponse:
    """Response from GLM chat completion."""
    content: str
    model: str
    usage: dict
    finish_reason: str
    thinking: Optional[str] = None  # For thinking mode


@dataclass
class GLMConfig:
    """Configuration for GLM requests."""
    temperature: float = 0.7
    max_tokens: int = 8192
    top_p: float = 0.9
    enable_thinking: bool = False
    preserve_thinking: bool = True  # Retain thinking across turns


class ZhipuClient(BaseExternalLLMClient):
    """
    Client for Zhipu AI's GLM models.

    Usage:
        client = ZhipuClient(api_key="your-api-key")

        # Basic chat
        response = await client.chat(
            messages=[{"role": "user", "content": "Explain quantum computing"}],
            model="glm-4.7",
        )

        # With thinking mode for complex reasoning
        response = await client.chat(
            messages=[{"role": "user", "content": "Solve this math problem..."}],
            model="glm-4.7-thinking",
            enable_thinking=True,
        )

        # Long report generation (uses 128K output capacity)
        response = await client.generate_report(
            topic="Q4 Financial Analysis",
            data=financial_data,
            max_tokens=50000,
        )
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if the API is accessible."""
        try:
            client = await self._get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    async def chat(
        self,
        messages: list[dict],
        model: str = GLMModel.GLM_4_7,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        top_p: float = 0.9,
        enable_thinking: bool = False,
        tools: Optional[list[dict]] = None,
        **kwargs,
    ) -> GLMResponse:
        """
        Send a chat completion request to GLM.

        Args:
            messages: List of message dicts with role and content
            model: Model to use (glm-4.7, glm-4.7-thinking, etc.)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate (up to 128K for glm-4.7)
            top_p: Nucleus sampling parameter
            enable_thinking: Enable interleaved thinking mode
            tools: Optional list of tools for function calling

        Returns:
            GLMResponse with content and metadata
        """
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }

        if enable_thinking or "thinking" in model:
            payload["enable_thinking"] = True

        if tools:
            payload["tools"] = tools

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        # Extract thinking if present
        thinking = None
        if "thinking" in message:
            thinking = message["thinking"]

        return GLMResponse(
            content=message.get("content", ""),
            model=data.get("model", model),
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", "stop"),
            thinking=thinking,
        )

    async def generate_report(
        self,
        topic: str,
        data: Optional[str] = None,
        instructions: Optional[str] = None,
        max_tokens: int = 50000,
        model: str = GLMModel.GLM_4_7,
    ) -> GLMResponse:
        """
        Generate a long-form report using GLM's 128K output capacity.

        Args:
            topic: Report topic/title
            data: Optional data to analyze
            instructions: Optional specific instructions
            max_tokens: Maximum output tokens (up to 128K)
            model: Model to use

        Returns:
            GLMResponse with full report content
        """
        system_prompt = """You are an expert report writer. Generate comprehensive,
well-structured reports with clear sections, data analysis, and actionable insights.
Use markdown formatting for readability."""

        user_content = f"Generate a detailed report on: {topic}"
        if data:
            user_content += f"\n\nData to analyze:\n{data}"
        if instructions:
            user_content += f"\n\nSpecific instructions:\n{instructions}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        return await self.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temp for factual reports
        )

    async def analyze_financial_data(
        self,
        data: str,
        analysis_type: str = "comprehensive",
        model: str = GLMModel.GLM_4_7,
    ) -> GLMResponse:
        """
        Analyze financial data with GLM's strong math reasoning.

        Args:
            data: Financial data (CSV, JSON, or text)
            analysis_type: Type of analysis (comprehensive, trends, forecast, risk)
            model: Model to use

        Returns:
            GLMResponse with financial analysis
        """
        system_prompt = """You are a financial analyst with expertise in data analysis,
trend identification, and forecasting. Provide precise calculations and clear insights.
Always show your mathematical reasoning."""

        analysis_prompts = {
            "comprehensive": "Perform a comprehensive financial analysis including trends, ratios, and recommendations.",
            "trends": "Identify and analyze trends in this financial data.",
            "forecast": "Based on this data, provide forecasts with confidence intervals.",
            "risk": "Analyze risks and provide risk-adjusted metrics.",
        }

        prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{prompt}\n\nData:\n{data}"},
        ]

        return await self.chat(
            messages=messages,
            model=model,
            max_tokens=16000,
            temperature=0.2,  # Low temp for accuracy
            enable_thinking=True,  # Use thinking for complex math
        )

    async def code_generation(
        self,
        task: str,
        context: Optional[str] = None,
        language: str = "python",
        model: str = GLMModel.GLM_4_7,
    ) -> GLMResponse:
        """
        Generate code using GLM's strong coding capabilities.

        Args:
            task: Description of what to build
            context: Optional existing code or context
            language: Programming language
            model: Model to use

        Returns:
            GLMResponse with generated code
        """
        system_prompt = f"""You are an expert {language} developer. Write clean,
well-documented, production-ready code. Include error handling and tests where appropriate."""

        user_content = f"Task: {task}"
        if context:
            user_content += f"\n\nExisting code/context:\n```{language}\n{context}\n```"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        return await self.chat(
            messages=messages,
            model=model,
            max_tokens=32000,
            temperature=0.3,
        )


# Convenience functions for direct usage
async def glm_chat(
    prompt: str,
    model: str = GLMModel.GLM_4_7,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Quick chat completion with GLM.

    Args:
        prompt: User prompt
        model: Model to use
        system: Optional system prompt

    Returns:
        Response content string
    """
    from .factory import get_llm_factory

    factory = get_llm_factory()
    client = factory.get_zhipu()

    if not client:
        raise ValueError("Zhipu client not configured. Set ZHIPU_API_KEY.")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat(messages=messages, model=model, **kwargs)
    return response.content


async def glm_report(
    topic: str,
    data: Optional[str] = None,
    max_tokens: int = 50000,
) -> str:
    """
    Generate a long-form report with GLM's 128K output capacity.

    Args:
        topic: Report topic
        data: Optional data to include
        max_tokens: Maximum output tokens

    Returns:
        Report content string
    """
    from .factory import get_llm_factory

    factory = get_llm_factory()
    client = factory.get_zhipu()

    if not client:
        raise ValueError("Zhipu client not configured. Set ZHIPU_API_KEY.")

    response = await client.generate_report(
        topic=topic,
        data=data,
        max_tokens=max_tokens,
    )
    return response.content


async def glm_analyze(
    data: str,
    analysis_type: str = "comprehensive",
) -> str:
    """
    Analyze financial/numerical data with GLM.

    Args:
        data: Data to analyze
        analysis_type: Type of analysis

    Returns:
        Analysis content string
    """
    from .factory import get_llm_factory

    factory = get_llm_factory()
    client = factory.get_zhipu()

    if not client:
        raise ValueError("Zhipu client not configured. Set ZHIPU_API_KEY.")

    response = await client.analyze_financial_data(
        data=data,
        analysis_type=analysis_type,
    )
    return response.content


async def glm_code(
    task: str,
    context: Optional[str] = None,
    language: str = "python",
) -> str:
    """
    Generate code with GLM's strong coding capabilities.

    Args:
        task: What to build
        context: Existing code context
        language: Programming language

    Returns:
        Generated code string
    """
    from .factory import get_llm_factory

    factory = get_llm_factory()
    client = factory.get_zhipu()

    if not client:
        raise ValueError("Zhipu client not configured. Set ZHIPU_API_KEY.")

    response = await client.code_generation(
        task=task,
        context=context,
        language=language,
    )
    return response.content
