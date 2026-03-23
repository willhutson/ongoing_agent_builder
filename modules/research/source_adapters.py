"""
Source adapters — thin async wrappers that normalize platform data into Mention objects.

Each adapter checks for real API credentials first. If absent, returns realistic
mock data tagged {"mock": true} so agents stay functional during development.

Inspired by Obsei's Observer pattern: one adapter per platform, uniform output shape.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional
import random
import hashlib


# ── Data shapes ──────────────────────────────────────────────────────────

@dataclass
class Mention:
    """A single normalized mention from any platform."""
    source: str          # "twitter", "reddit", "app_store", etc.
    text: str
    author: str
    timestamp: str       # ISO 8601
    url: Optional[str] = None
    metadata: dict = field(default_factory=dict)  # platform-specific extras

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MentionBatch:
    """A batch of mentions from a single collection run."""
    mentions: list[Mention]
    source: str
    query: str
    collected_at: str
    mock: bool = False

    def to_dict(self) -> dict:
        return {
            "mentions": [m.to_dict() for m in self.mentions],
            "source": self.source,
            "query": self.query,
            "collected_at": self.collected_at,
            "mock": self.mock,
            "count": len(self.mentions),
        }


# ── Helpers ──────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mock_timestamps(count: int, period: str) -> list[str]:
    """Generate realistic-looking timestamps spread across the period."""
    days = {"day": 1, "week": 7, "month": 30, "quarter": 90}.get(period, 7)
    base = datetime.now(timezone.utc)
    return [
        (base - timedelta(hours=random.randint(1, days * 24))).isoformat()
        for _ in range(count)
    ]


def _deterministic_seed(brand: str, source: str) -> None:
    """Seed RNG so the same brand+source always produces the same mock data."""
    seed = int(hashlib.md5(f"{brand}:{source}".encode()).hexdigest()[:8], 16)
    random.seed(seed)


# ── Twitter adapter ──────────────────────────────────────────────────────

_MOCK_TWITTER = [
    "Just tried {brand}'s new feature — actually impressed. The UX is solid.",
    "Is anyone else having issues with {brand}? Support hasn't responded in 3 days.",
    "{brand} absolutely nailed their latest campaign. Clean, sharp messaging.",
    "Switching from {brand} to a competitor. The pricing changes are a dealbreaker.",
    "Hot take: {brand} is underrated. Their product is way ahead of the market.",
    "Had a great experience with {brand}'s customer team today. Quick and helpful.",
    "{brand} needs to fix their mobile app. Crashes every other session.",
    "Love what {brand} is doing with their community. Feels authentic.",
]


async def collect_twitter(
    brand: str, period: str = "week", api_key: Optional[str] = None
) -> MentionBatch:
    """Collect brand mentions from Twitter/X."""
    # TODO: Wire real Twitter API v2 when api_key is provided
    _deterministic_seed(brand, "twitter")
    timestamps = _mock_timestamps(len(_MOCK_TWITTER), period)
    mentions = [
        Mention(
            source="twitter",
            text=t.format(brand=brand),
            author=f"@user_{i + 1}",
            timestamp=timestamps[i],
            url=f"https://x.com/user_{i + 1}/status/{random.randint(10**17, 10**18)}",
            metadata={"retweets": random.randint(0, 200), "likes": random.randint(0, 500), "mock": True},
        )
        for i, t in enumerate(_MOCK_TWITTER)
    ]
    return MentionBatch(
        mentions=mentions, source="twitter", query=brand,
        collected_at=_now_iso(), mock=True,
    )


# ── Reddit adapter ───────────────────────────────────────────────────────

_MOCK_REDDIT = [
    "Has anyone used {brand} for a real project? Looking for honest reviews.",
    "PSA: {brand} just released a major update. Here's what changed...",
    "{brand} vs competitors — my experience after 6 months",
    "Unpopular opinion: {brand}'s free tier is generous enough for most teams.",
    "Frustrated with {brand}. Third outage this month.",
]


async def collect_reddit(
    brand: str, subreddits: Optional[list[str]] = None,
    period: str = "week", client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> MentionBatch:
    """Collect brand mentions from Reddit."""
    # TODO: Wire real Reddit API (PRAW) when credentials are provided
    _deterministic_seed(brand, "reddit")
    subs = subreddits or ["technology", "startups", "smallbusiness"]
    timestamps = _mock_timestamps(len(_MOCK_REDDIT), period)
    mentions = [
        Mention(
            source="reddit",
            text=t.format(brand=brand),
            author=f"u/redditor_{i + 1}",
            timestamp=timestamps[i],
            url=f"https://reddit.com/r/{random.choice(subs)}/comments/{random.randint(10**5, 10**6)}",
            metadata={
                "subreddit": random.choice(subs),
                "upvotes": random.randint(1, 300),
                "comments": random.randint(0, 80),
                "mock": True,
            },
        )
        for i, t in enumerate(_MOCK_REDDIT)
    ]
    return MentionBatch(
        mentions=mentions, source="reddit", query=brand,
        collected_at=_now_iso(), mock=True,
    )


# ── App Store adapter ────────────────────────────────────────────────────

_MOCK_REVIEWS = [
    {"text": "Great app, use it daily. {brand} keeps improving.", "stars": 5},
    {"text": "Decent but the latest update broke notifications.", "stars": 3},
    {"text": "Love {brand}! Best in class for our team.", "stars": 5},
    {"text": "Too expensive for what it offers. Downgrading.", "stars": 2},
    {"text": "Solid app. Wish they'd add dark mode.", "stars": 4},
    {"text": "Crashes on launch since the update. Please fix.", "stars": 1},
]


async def collect_app_store(
    app_id: str, platform: str = "ios", period: str = "week"
) -> MentionBatch:
    """Collect app/product reviews from iOS App Store or Google Play."""
    # TODO: Wire real App Store Connect / Google Play scraper
    _deterministic_seed(app_id, f"app_store_{platform}")
    timestamps = _mock_timestamps(len(_MOCK_REVIEWS), period)
    mentions = [
        Mention(
            source=f"app_store_{platform}",
            text=r["text"].format(brand=app_id),
            author=f"reviewer_{i + 1}",
            timestamp=timestamps[i],
            metadata={"stars": r["stars"], "platform": platform, "app_id": app_id, "mock": True},
        )
        for i, r in enumerate(_MOCK_REVIEWS)
    ]
    return MentionBatch(
        mentions=mentions, source=f"app_store_{platform}", query=app_id,
        collected_at=_now_iso(), mock=True,
    )


# ── Google Reviews adapter ───────────────────────────────────────────────

_MOCK_GOOGLE = [
    {"text": "Excellent service from {brand}. Will come back.", "stars": 5},
    {"text": "Average experience. Nothing special.", "stars": 3},
    {"text": "{brand} exceeded expectations. Highly recommend.", "stars": 5},
    {"text": "Long wait times. Staff was friendly though.", "stars": 3},
]


async def collect_google_reviews(
    place_id: str, period: str = "week", api_key: Optional[str] = None
) -> MentionBatch:
    """Collect Google Maps / Google Business reviews."""
    # TODO: Wire real Google Places API when api_key is provided
    _deterministic_seed(place_id, "google_reviews")
    timestamps = _mock_timestamps(len(_MOCK_GOOGLE), period)
    mentions = [
        Mention(
            source="google_reviews",
            text=r["text"].format(brand=place_id),
            author=f"Google User {i + 1}",
            timestamp=timestamps[i],
            url=f"https://maps.google.com/?cid={place_id}",
            metadata={"stars": r["stars"], "place_id": place_id, "mock": True},
        )
        for i, r in enumerate(_MOCK_GOOGLE)
    ]
    return MentionBatch(
        mentions=mentions, source="google_reviews", query=place_id,
        collected_at=_now_iso(), mock=True,
    )


# ── News adapter ─────────────────────────────────────────────────────────

_MOCK_NEWS = [
    {"title": "{brand} Announces Q1 Results, Beats Expectations", "outlet": "TechCrunch"},
    {"title": "Why {brand} Is Betting Big on AI", "outlet": "The Verge"},
    {"title": "{brand} Faces Scrutiny Over Data Practices", "outlet": "Reuters"},
    {"title": "{brand} CEO on the Future of the Industry", "outlet": "Forbes"},
]


async def collect_news(query: str, period: str = "week") -> MentionBatch:
    """Collect news articles mentioning a brand/topic."""
    # TODO: Wire real news API (NewsAPI, Google News RSS, etc.)
    _deterministic_seed(query, "news")
    timestamps = _mock_timestamps(len(_MOCK_NEWS), period)
    mentions = [
        Mention(
            source="news",
            text=n["title"].format(brand=query),
            author=n["outlet"],
            timestamp=timestamps[i],
            url=f"https://example.com/news/{random.randint(10000, 99999)}",
            metadata={"outlet": n["outlet"], "mock": True},
        )
        for i, n in enumerate(_MOCK_NEWS)
    ]
    return MentionBatch(
        mentions=mentions, source="news", query=query,
        collected_at=_now_iso(), mock=True,
    )


# ── Website adapter ──────────────────────────────────────────────────────

async def collect_website(url: str) -> MentionBatch:
    """Scrape/crawl a competitor website for content analysis."""
    # TODO: Wire real scraper (httpx + trafilatura, like Obsei does)
    _deterministic_seed(url, "website")
    mentions = [
        Mention(
            source="website",
            text=f"Scraped content from {url} — homepage, about page, pricing page.",
            author=url,
            timestamp=_now_iso(),
            url=url,
            metadata={"pages_scraped": 3, "mock": True},
        )
    ]
    return MentionBatch(
        mentions=mentions, source="website", query=url,
        collected_at=_now_iso(), mock=True,
    )


# ── Dispatcher ───────────────────────────────────────────────────────────

SOURCE_ADAPTERS = {
    "twitter": collect_twitter,
    "reddit": collect_reddit,
    "app_store": collect_app_store,
    "google_reviews": collect_google_reviews,
    "news": collect_news,
    "website": collect_website,
}
