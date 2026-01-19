"""
Perplexity Client

Provides access to:
- Search-augmented AI research
- Real-time web search
- Fact-checking
"""

from typing import Optional, Literal
from .base import BaseExternalLLMClient, GenerationResult, TaskStatus


PerplexityModel = Literal["sonar-pro", "sonar", "sonar-reasoning"]


class PerplexityClient(BaseExternalLLMClient):
    """Client for Perplexity search-augmented AI API."""

    DEFAULT_BASE_URL = "https://api.perplexity.ai"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ):
        super().__init__(api_key, base_url, timeout)

    async def search(
        self,
        query: str,
        model: PerplexityModel = "sonar-pro",
        search_domain_filter: Optional[list[str]] = None,
        search_recency_filter: Optional[str] = None,
        return_citations: bool = True,
        return_images: bool = False,
    ) -> GenerationResult:
        """
        Perform a search-augmented query.

        Args:
            query: The research question or topic
            model: Model to use (sonar-pro for best quality)
            search_domain_filter: Limit search to specific domains
            search_recency_filter: Filter by recency (day, week, month, year)
            return_citations: Include source citations
            return_images: Include relevant images

        Returns:
            GenerationResult with research findings
        """
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": query}
            ],
            "return_citations": return_citations,
            "return_images": return_images,
        }
        if search_domain_filter:
            data["search_domain_filter"] = search_domain_filter
        if search_recency_filter:
            data["search_recency_filter"] = search_recency_filter

        try:
            result = await self._post("/chat/completions", data)

            choice = result.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            citations = result.get("citations", [])

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data={
                    "answer": content,
                    "citations": citations,
                    "images": result.get("images", []),
                },
                metadata={
                    "model": model,
                    "usage": result.get("usage"),
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def research(
        self,
        topic: str,
        context: Optional[str] = None,
        focus_areas: Optional[list[str]] = None,
        model: PerplexityModel = "sonar-pro",
    ) -> GenerationResult:
        """
        Conduct in-depth research on a topic.

        Args:
            topic: The topic to research
            context: Additional context or constraints
            focus_areas: Specific aspects to focus on
            model: Model to use

        Returns:
            GenerationResult with research report
        """
        prompt = f"Research the following topic thoroughly: {topic}"
        if context:
            prompt += f"\n\nContext: {context}"
        if focus_areas:
            prompt += f"\n\nFocus on: {', '.join(focus_areas)}"

        return await self.search(
            query=prompt,
            model=model,
            return_citations=True,
        )

    async def fact_check(
        self,
        claim: str,
        context: Optional[str] = None,
        model: PerplexityModel = "sonar-pro",
    ) -> GenerationResult:
        """
        Fact-check a claim using web search.

        Args:
            claim: The claim to verify
            context: Additional context
            model: Model to use

        Returns:
            GenerationResult with fact-check results
        """
        prompt = f"""Fact-check the following claim. Provide:
1. Verdict (True, False, Partially True, Unverifiable)
2. Supporting evidence
3. Sources

Claim: {claim}"""

        if context:
            prompt += f"\n\nContext: {context}"

        return await self.search(
            query=prompt,
            model=model,
            return_citations=True,
            search_recency_filter="month",
        )

    async def competitive_analysis(
        self,
        company: str,
        competitors: list[str],
        aspects: Optional[list[str]] = None,
        model: PerplexityModel = "sonar-pro",
    ) -> GenerationResult:
        """
        Perform competitive analysis.

        Args:
            company: The company to analyze
            competitors: List of competitor companies
            aspects: Aspects to compare (pricing, features, market share, etc.)
            model: Model to use

        Returns:
            GenerationResult with competitive analysis
        """
        aspects_str = ", ".join(aspects) if aspects else "pricing, features, market position, strengths, weaknesses"

        prompt = f"""Perform a competitive analysis of {company} against its competitors: {', '.join(competitors)}.

Compare the following aspects: {aspects_str}

Provide a structured analysis with current data and sources."""

        return await self.search(
            query=prompt,
            model=model,
            return_citations=True,
        )

    async def market_research(
        self,
        market: str,
        focus: Optional[str] = None,
        region: Optional[str] = None,
        model: PerplexityModel = "sonar-pro",
    ) -> GenerationResult:
        """
        Conduct market research.

        Args:
            market: The market to research
            focus: Specific focus area (trends, size, players, etc.)
            region: Geographic region
            model: Model to use

        Returns:
            GenerationResult with market research
        """
        prompt = f"Provide comprehensive market research on the {market} market"
        if region:
            prompt += f" in {region}"
        if focus:
            prompt += f", focusing on {focus}"
        prompt += ". Include market size, key players, trends, and forecasts with sources."

        return await self.search(
            query=prompt,
            model=model,
            return_citations=True,
        )

    async def news_summary(
        self,
        topic: str,
        time_period: str = "week",
        model: PerplexityModel = "sonar",
    ) -> GenerationResult:
        """
        Get a summary of recent news on a topic.

        Args:
            topic: The topic to summarize news for
            time_period: Time period (day, week, month)
            model: Model to use

        Returns:
            GenerationResult with news summary
        """
        return await self.search(
            query=f"Summarize the most important news about {topic} from the past {time_period}. Include key developments, implications, and sources.",
            model=model,
            search_recency_filter=time_period,
            return_citations=True,
        )

    async def chat(
        self,
        messages: list[dict],
        model: PerplexityModel = "sonar-pro",
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """
        Have a multi-turn conversation with web search.

        Args:
            messages: List of message dicts with role and content
            model: Model to use
            system_prompt: Optional system prompt

        Returns:
            GenerationResult with response
        """
        data = {
            "model": model,
            "messages": messages,
            "return_citations": True,
        }
        if system_prompt:
            data["messages"].insert(0, {"role": "system", "content": system_prompt})

        try:
            result = await self._post("/chat/completions", data)

            choice = result.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")

            return GenerationResult(
                success=True,
                status=TaskStatus.COMPLETED,
                output_data={
                    "response": content,
                    "citations": result.get("citations", []),
                },
                metadata={
                    "model": model,
                    "usage": result.get("usage"),
                },
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    def _parse_status(self, result: dict) -> TaskStatus:
        """Perplexity API is synchronous."""
        return TaskStatus.COMPLETED

    def _parse_completed_result(self, result: dict) -> GenerationResult:
        """Parse Perplexity response."""
        return GenerationResult(
            success=True,
            status=TaskStatus.COMPLETED,
            output_data=result,
        )

    async def health_check(self) -> bool:
        """Check if Perplexity API is accessible."""
        try:
            # Simple test query
            result = await self.search("test", model="sonar")
            return result.success
        except Exception:
            return False
