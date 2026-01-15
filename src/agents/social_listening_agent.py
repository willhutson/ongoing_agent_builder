from typing import Any, Optional
import httpx
from .base import BaseAgent
from src.skills.agent_browser import AgentBrowserSkill, BrowserResult


class SocialListeningAgent(BaseAgent):
    """
    Agent for social media listening and monitoring.

    Capabilities:
    - Monitor brand mentions (via API)
    - Track sentiment (via API)
    - Identify trends (via API + Browser)
    - Monitor competitors (via API + Browser)
    - Alert on issues (via API)
    - Scrape trending content (Browser)
    - Capture social proof screenshots (Browser)
    - Scrape Reddit threads and subreddits (Browser)
    - Scrape Twitter/X search results (Browser)
    - Scrape Google News mentions (Browser)
    - Scrape YouTube search results (Browser)
    - Scrape HackerNews discussions (Browser)
    - Scrape Product Hunt launches (Browser)
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
        client_id: str = None,
        instance_id: str = None,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.client_specific_id = client_id
        self.instance_id = instance_id
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        # Browser automation for scraping platforms without APIs
        session_name = f"social_listener_{instance_id}" if instance_id else "social_listener"
        self.browser = AgentBrowserSkill(session_name=session_name)
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "social_listening_agent"

    @property
    def system_prompt(self) -> str:
        return """You are a social listening and monitoring expert.

Your role is to track and analyze social conversations:
1. Monitor brand and product mentions
2. Analyze sentiment trends
3. Identify emerging topics
4. Track competitor activity
5. Alert on potential issues

You have browser automation capabilities to scrape content from:
- Social platforms: Instagram, TikTok, Twitter/X, LinkedIn, Facebook
- Community forums: Reddit, HackerNews, Product Hunt
- News sources: Google News, YouTube
- Use scrape_* tools when you need real-time data not available via APIs

When using browser tools:
- Always capture screenshots as proof of findings
- Re-snapshot after any page navigation (refs change!)
- Use interactive_only=True for efficiency"""

    def _define_tools(self) -> list[dict]:
        return [
            # ===== API-Based Tools =====
            {
                "name": "setup_monitoring",
                "description": "Set up social monitoring via API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                        "languages": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["keywords"],
                },
            },
            {
                "name": "get_mentions",
                "description": "Get brand mentions via API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral", "all"]},
                        "platform": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze sentiment trends via API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "date_range": {"type": "object"},
                        "granularity": {"type": "string", "enum": ["hourly", "daily", "weekly"]},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_trending_topics",
                "description": "Get trending topics via API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "industry": {"type": "string"},
                        "region": {"type": "string"},
                    },
                    "required": [],
                },
            },
            {
                "name": "monitor_competitors",
                "description": "Monitor competitor activity via API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "competitors": {"type": "array", "items": {"type": "string"}},
                        "date_range": {"type": "object"},
                    },
                    "required": ["competitors"],
                },
            },
            {
                "name": "create_alert",
                "description": "Create monitoring alert.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "conditions": {"type": "object"},
                        "notify": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "conditions"],
                },
            },
            # ===== Browser-Based Tools =====
            {
                "name": "scrape_trending_content",
                "description": "Scrape trending/explore content from social platforms using browser automation. Use when API doesn't expose trending data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "tiktok", "twitter", "linkedin"],
                            "description": "Social platform to scrape",
                        },
                        "topic": {
                            "type": "string",
                            "description": "Optional topic/hashtag to focus on",
                        },
                        "capture_screenshot": {
                            "type": "boolean",
                            "description": "Whether to capture screenshot proof",
                            "default": True,
                        },
                    },
                    "required": ["platform"],
                },
            },
            {
                "name": "scrape_competitor_posts",
                "description": "Scrape recent posts from a competitor's social profile using browser.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "tiktok", "twitter", "linkedin", "facebook"],
                        },
                        "profile_url": {
                            "type": "string",
                            "description": "URL of competitor's social profile",
                        },
                        "capture_screenshot": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": ["platform", "profile_url"],
                },
            },
            {
                "name": "scrape_hashtag",
                "description": "Scrape posts for a specific hashtag using browser.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "tiktok", "twitter"],
                        },
                        "hashtag": {
                            "type": "string",
                            "description": "Hashtag to search (without #)",
                        },
                        "capture_screenshot": {
                            "type": "boolean",
                            "default": True,
                        },
                    },
                    "required": ["platform", "hashtag"],
                },
            },
            {
                "name": "capture_social_proof",
                "description": "Navigate to a social URL and capture screenshot as proof.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Social media URL to capture"},
                        "output_prefix": {"type": "string", "default": "social_proof"},
                    },
                    "required": ["url"],
                },
            },
            # ===== Extended Browser Tools =====
            {
                "name": "scrape_reddit",
                "description": "Scrape Reddit for brand mentions, subreddit discussions, or search results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "search_query": {"type": "string", "description": "Search term or brand name"},
                        "subreddit": {"type": "string", "description": "Specific subreddit to search (optional)"},
                        "sort": {"type": "string", "enum": ["relevance", "hot", "top", "new", "comments"], "default": "relevance"},
                        "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"], "default": "week"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["search_query"],
                },
            },
            {
                "name": "scrape_twitter_search",
                "description": "Scrape Twitter/X search results for keywords, mentions, or hashtags.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (supports Twitter search operators)"},
                        "filter": {"type": "string", "enum": ["top", "latest", "people", "photos", "videos"], "default": "top"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_google_news",
                "description": "Scrape Google News for brand/topic mentions and press coverage.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "time_range": {"type": "string", "enum": ["hour", "day", "week", "month", "year"], "default": "week"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_youtube_search",
                "description": "Scrape YouTube search results for video mentions and discussions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "filter": {"type": "string", "enum": ["relevance", "upload_date", "view_count", "rating"], "default": "relevance"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_hackernews",
                "description": "Scrape HackerNews for tech industry discussions and mentions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "search_type": {"type": "string", "enum": ["story", "comment", "all"], "default": "all"},
                        "sort": {"type": "string", "enum": ["popularity", "date"], "default": "popularity"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_product_hunt",
                "description": "Scrape Product Hunt for product launches and discussions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query or product name"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape_quora",
                "description": "Scrape Quora for Q&A discussions about a brand or topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "capture_screenshot": {"type": "boolean", "default": True},
                    },
                    "required": ["query"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        try:
            client_id = tool_input.get("client_id") or self.client_specific_id

            # ===== API-Based Tools =====
            if tool_name == "setup_monitoring":
                response = await self.http_client.post(
                    "/api/v1/social/monitoring",
                    json={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to setup"}

            elif tool_name == "get_mentions":
                response = await self.http_client.get(
                    "/api/v1/social/mentions",
                    params={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code == 200 else {"mentions": []}

            elif tool_name == "analyze_sentiment":
                response = await self.http_client.get(
                    "/api/v1/social/sentiment",
                    params={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code == 200 else {"sentiment": None}

            elif tool_name == "get_trending_topics":
                response = await self.http_client.get("/api/v1/social/trends", params=tool_input)
                return response.json() if response.status_code == 200 else {"trends": []}

            elif tool_name == "monitor_competitors":
                response = await self.http_client.get("/api/v1/social/competitors", params=tool_input)
                return response.json() if response.status_code == 200 else {"competitors": []}

            elif tool_name == "create_alert":
                response = await self.http_client.post(
                    "/api/v1/social/alerts",
                    json={**tool_input, "client_id": client_id}
                )
                return response.json() if response.status_code in (200, 201) else {"error": "Failed to create"}

            # ===== Browser-Based Tools =====
            elif tool_name == "scrape_trending_content":
                return await self._scrape_trending(
                    platform=tool_input["platform"],
                    topic=tool_input.get("topic"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_competitor_posts":
                return await self._scrape_profile(
                    platform=tool_input["platform"],
                    profile_url=tool_input["profile_url"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_hashtag":
                return await self._scrape_hashtag(
                    platform=tool_input["platform"],
                    hashtag=tool_input["hashtag"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "capture_social_proof":
                return await self._capture_proof(
                    url=tool_input["url"],
                    prefix=tool_input.get("output_prefix", "social_proof"),
                )

            # ===== Extended Browser Tools =====
            elif tool_name == "scrape_reddit":
                return await self._scrape_reddit(
                    query=tool_input["search_query"],
                    subreddit=tool_input.get("subreddit"),
                    sort=tool_input.get("sort", "relevance"),
                    time_filter=tool_input.get("time_filter", "week"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_twitter_search":
                return await self._scrape_twitter_search(
                    query=tool_input["query"],
                    filter_type=tool_input.get("filter", "top"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_google_news":
                return await self._scrape_google_news(
                    query=tool_input["query"],
                    time_range=tool_input.get("time_range", "week"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_youtube_search":
                return await self._scrape_youtube(
                    query=tool_input["query"],
                    filter_type=tool_input.get("filter", "relevance"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_hackernews":
                return await self._scrape_hackernews(
                    query=tool_input["query"],
                    search_type=tool_input.get("search_type", "all"),
                    sort=tool_input.get("sort", "popularity"),
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_product_hunt":
                return await self._scrape_product_hunt(
                    query=tool_input["query"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            elif tool_name == "scrape_quora":
                return await self._scrape_quora(
                    query=tool_input["query"],
                    capture=tool_input.get("capture_screenshot", True),
                )

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # Browser-Based Implementations
    # =========================================================================

    async def _scrape_trending(
        self,
        platform: str,
        topic: Optional[str] = None,
        capture: bool = True
    ) -> dict:
        """Scrape trending content from social platform explore pages."""
        platform_urls = {
            "instagram": "https://www.instagram.com/explore/",
            "tiktok": "https://www.tiktok.com/discover",
            "twitter": "https://twitter.com/explore",
            "linkedin": "https://www.linkedin.com/feed/",
        }

        url = platform_urls.get(platform)
        if not url:
            return {"error": f"Unsupported platform: {platform}"}

        # If topic provided, modify URL
        if topic:
            if platform == "instagram":
                url = f"https://www.instagram.com/explore/tags/{topic}/"
            elif platform == "tiktok":
                url = f"https://www.tiktok.com/tag/{topic}"
            elif platform == "twitter":
                url = f"https://twitter.com/search?q=%23{topic}"

        try:
            # Navigate to page
            await self.browser.open(url)
            await self.browser.wait(2000)  # Let content load

            # Get snapshot of interactive elements
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "url": url,
                "topic": topic,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            # Capture screenshot proof
            if capture:
                screenshot_path = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"trending_{platform}"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"Browser scrape failed: {str(e)}"}

    async def _scrape_profile(
        self,
        platform: str,
        profile_url: str,
        capture: bool = True
    ) -> dict:
        """Scrape competitor's social profile."""
        try:
            await self.browser.open(profile_url)
            await self.browser.wait(2000)

            # Get full snapshot for content extraction
            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "profile_url": profile_url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                screenshot_path = await self.browser.capture_proof(
                    url=profile_url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"competitor_{platform}"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"Profile scrape failed: {str(e)}"}

    async def _scrape_hashtag(
        self,
        platform: str,
        hashtag: str,
        capture: bool = True
    ) -> dict:
        """Scrape posts for a specific hashtag."""
        hashtag_urls = {
            "instagram": f"https://www.instagram.com/explore/tags/{hashtag}/",
            "tiktok": f"https://www.tiktok.com/tag/{hashtag}",
            "twitter": f"https://twitter.com/hashtag/{hashtag}",
        }

        url = hashtag_urls.get(platform)
        if not url:
            return {"error": f"Hashtag search not supported for: {platform}"}

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "platform": platform,
                "hashtag": hashtag,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                screenshot_path = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"hashtag_{platform}_{hashtag}"
                )
                result["screenshot"] = screenshot_path

            return result

        except Exception as e:
            return {"error": f"Hashtag scrape failed: {str(e)}"}

    async def _capture_proof(self, url: str, prefix: str) -> dict:
        """Capture screenshot proof of social content."""
        try:
            screenshot_path = await self.browser.capture_proof(
                url=url,
                output_dir="/tmp/social_proofs",
                prefix=prefix
            )
            return {
                "url": url,
                "screenshot": screenshot_path,
                "success": True,
            }
        except Exception as e:
            return {"error": f"Screenshot capture failed: {str(e)}"}

    # =========================================================================
    # Extended Browser Implementations
    # =========================================================================

    async def _scrape_reddit(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        time_filter: str = "week",
        capture: bool = True
    ) -> dict:
        """Scrape Reddit search results or subreddit."""
        if subreddit:
            url = f"https://www.reddit.com/r/{subreddit}/search?q={query}&restrict_sr=1&sort={sort}&t={time_filter}"
        else:
            url = f"https://www.reddit.com/search?q={query}&sort={sort}&t={time_filter}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "subreddit": subreddit,
                "sort": sort,
                "time_filter": time_filter,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                prefix = f"reddit_{subreddit}" if subreddit else f"reddit_{query.replace(' ', '_')}"
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=prefix
                )

            return result

        except Exception as e:
            return {"error": f"Reddit scrape failed: {str(e)}"}

    async def _scrape_twitter_search(
        self,
        query: str,
        filter_type: str = "top",
        capture: bool = True
    ) -> dict:
        """Scrape Twitter/X search results."""
        # Map filter to Twitter URL param
        filter_map = {
            "top": "",
            "latest": "&f=live",
            "people": "&f=user",
            "photos": "&f=image",
            "videos": "&f=video",
        }
        filter_param = filter_map.get(filter_type, "")
        url = f"https://twitter.com/search?q={query}{filter_param}"

        try:
            await self.browser.open(url)
            await self.browser.wait(3000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "filter": filter_type,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"twitter_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Twitter scrape failed: {str(e)}"}

    async def _scrape_google_news(
        self,
        query: str,
        time_range: str = "week",
        capture: bool = True
    ) -> dict:
        """Scrape Google News for mentions."""
        # Map time range to Google News param
        time_map = {
            "hour": "qdr:h",
            "day": "qdr:d",
            "week": "qdr:w",
            "month": "qdr:m",
            "year": "qdr:y",
        }
        tbs = time_map.get(time_range, "qdr:w")
        url = f"https://www.google.com/search?q={query}&tbm=nws&tbs={tbs}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "time_range": time_range,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"google_news_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Google News scrape failed: {str(e)}"}

    async def _scrape_youtube(
        self,
        query: str,
        filter_type: str = "relevance",
        capture: bool = True
    ) -> dict:
        """Scrape YouTube search results."""
        # Map filter to YouTube sort param
        filter_map = {
            "relevance": "",
            "upload_date": "&sp=CAI%253D",
            "view_count": "&sp=CAM%253D",
            "rating": "&sp=CAE%253D",
        }
        filter_param = filter_map.get(filter_type, "")
        url = f"https://www.youtube.com/results?search_query={query}{filter_param}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "filter": filter_type,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"youtube_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"YouTube scrape failed: {str(e)}"}

    async def _scrape_hackernews(
        self,
        query: str,
        search_type: str = "all",
        sort: str = "popularity",
        capture: bool = True
    ) -> dict:
        """Scrape HackerNews via Algolia search."""
        # Use HN Algolia search
        type_filter = "" if search_type == "all" else f"&type={search_type}"
        sort_param = "byPopularity" if sort == "popularity" else "byDate"
        url = f"https://hn.algolia.com/?dateRange=all&page=0&prefix=true&query={query}&sort={sort_param}{type_filter}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2000)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "search_type": search_type,
                "sort": sort,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"hackernews_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"HackerNews scrape failed: {str(e)}"}

    async def _scrape_product_hunt(self, query: str, capture: bool = True) -> dict:
        """Scrape Product Hunt search results."""
        url = f"https://www.producthunt.com/search?q={query}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"producthunt_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Product Hunt scrape failed: {str(e)}"}

    async def _scrape_quora(self, query: str, capture: bool = True) -> dict:
        """Scrape Quora search results."""
        url = f"https://www.quora.com/search?q={query}"

        try:
            await self.browser.open(url)
            await self.browser.wait(2500)

            snapshot = await self.browser.snapshot(interactive_only=False)

            result = {
                "query": query,
                "url": url,
                "snapshot": snapshot.raw,
                "timestamp": snapshot.timestamp.isoformat(),
            }

            if capture:
                result["screenshot"] = await self.browser.capture_proof(
                    url=url,
                    output_dir="/tmp/social_proofs",
                    prefix=f"quora_{query.replace(' ', '_')}"
                )

            return result

        except Exception as e:
            return {"error": f"Quora scrape failed: {str(e)}"}

    async def close(self):
        """Cleanup resources."""
        await self.http_client.aclose()
        await self.browser.close()
