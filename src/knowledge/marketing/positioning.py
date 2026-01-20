"""
Positioning & Value Proposition Frameworks

A library of positioning angles, value proposition formulas, and messaging frameworks
that agents can use to craft compelling marketing messages.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarketStage(str, Enum):
    """Market sophistication stages."""
    NEW = "new"           # First to market - simple promise works
    GROWING = "growing"   # Competition emerging - need bigger claims
    CROWDED = "crowded"   # Many competitors - need unique mechanism
    JADED = "jaded"       # Audience skeptical - need proof
    MATURE = "mature"     # Saturated - sell identity/belonging


class PositioningAngle(str, Enum):
    """Core positioning angles."""
    CONTRARIAN = "contrarian"         # Challenge conventional wisdom
    TRANSFORMATION = "transformation"  # Before/after state change
    ENEMY = "enemy"                   # Common enemy to fight
    SPEED = "speed"                   # Fast results, no sacrifice
    SPECIFICITY = "specificity"       # Hyper-targeted audience


@dataclass
class MarketStageStrategy:
    """Strategy for a specific market stage."""
    stage: MarketStage
    approach: str
    template: str
    example: str


@dataclass
class AngleFramework:
    """A positioning angle with template and examples."""
    angle: PositioningAngle
    description: str
    template: str
    examples: list[str]
    best_for: list[str]
    avoid_when: list[str]


# =============================================================================
# MARKET STAGE STRATEGIES
# =============================================================================

MARKET_STAGE_STRATEGIES: dict[MarketStage, MarketStageStrategy] = {
    MarketStage.NEW: MarketStageStrategy(
        stage=MarketStage.NEW,
        approach="Simple promise",
        template="Now you can [X]",
        example="Now you can build websites without code",
    ),
    MarketStage.GROWING: MarketStageStrategy(
        stage=MarketStage.GROWING,
        approach="Bigger claim",
        template="[X] in [specific time]",
        example="Launch your store in 30 minutes",
    ),
    MarketStage.CROWDED: MarketStageStrategy(
        stage=MarketStage.CROWDED,
        approach="Show mechanism",
        template="The [method] that works",
        example="The 3-step system that 10x'd our pipeline",
    ),
    MarketStage.JADED: MarketStageStrategy(
        stage=MarketStage.JADED,
        approach="Prove it",
        template="[Data/proof] that shows",
        example="How 2,847 companies cut CAC by 43%",
    ),
    MarketStage.MATURE: MarketStageStrategy(
        stage=MarketStage.MATURE,
        approach="Sell identity",
        template="For [people who are X]",
        example="For founders who refuse to settle",
    ),
}


# =============================================================================
# POSITIONING ANGLES
# =============================================================================

POSITIONING_ANGLES: dict[PositioningAngle, AngleFramework] = {
    PositioningAngle.CONTRARIAN: AngleFramework(
        angle=PositioningAngle.CONTRARIAN,
        description="Challenge what everyone believes is true",
        template="Everything you know about [X] is wrong",
        examples=[
            "Everything you know about SEO is wrong",
            "Stop doing X the way everyone else does",
            "Why the 'best practice' is actually killing your conversion",
            "The counterintuitive approach to [X] that actually works",
        ],
        best_for=["Crowded markets", "Commoditized products", "Thought leadership"],
        avoid_when=["New market category", "Risk-averse audience", "Regulated industries"],
    ),
    PositioningAngle.TRANSFORMATION: AngleFramework(
        angle=PositioningAngle.TRANSFORMATION,
        description="Show the journey from painful state to desired outcome",
        template="From [painful state] to [desired state]",
        examples=[
            "From spreadsheet chaos to automated clarity",
            "Go from 0 to 10K subscribers in 90 days",
            "Transform your team from stressed to strategic",
            "From struggling startup to category leader",
        ],
        best_for=["B2B SaaS", "Education", "Services", "Personal development"],
        avoid_when=["Quick-win products", "Low-involvement purchases"],
    ),
    PositioningAngle.ENEMY: AngleFramework(
        angle=PositioningAngle.ENEMY,
        description="Identify a common enemy and position against it",
        template="Stop letting [X] steal your [Y]",
        examples=[
            "Stop letting manual processes steal your weekends",
            "Don't let bad data destroy your campaigns",
            "Why legacy software is costing you $50K/year",
            "The hidden tax that's killing your margins",
        ],
        best_for=["Replacement products", "Disruptive tech", "Strong competitors"],
        avoid_when=["New categories", "Collaborative sales process"],
    ),
    PositioningAngle.SPEED: AngleFramework(
        angle=PositioningAngle.SPEED,
        description="Promise fast results without typical sacrifices",
        template="[Outcome] in [time] without [sacrifice]",
        examples=[
            "Ship features 10x faster without breaking things",
            "Get enterprise security in hours, not months",
            "Scale your team without the hiring headaches",
            "Launch campaigns in minutes, not days",
        ],
        best_for=["Productivity tools", "Automation", "Developer tools"],
        avoid_when=["Complex enterprise sales", "Trust-dependent products"],
    ),
    PositioningAngle.SPECIFICITY: AngleFramework(
        angle=PositioningAngle.SPECIFICITY,
        description="Hyper-target a specific audience with specific needs",
        template="For [exact person] who wants [exact thing]",
        examples=[
            "For B2B SaaS founders scaling past $1M ARR",
            "For marketing teams tired of 10+ tool subscriptions",
            "For agencies billing over $500K annually",
            "For e-commerce brands doing $10M+ in revenue",
        ],
        best_for=["Niche products", "Premium pricing", "Account-based marketing"],
        avoid_when=["Mass market products", "Early-stage startups seeking PMF"],
    ),
}


# =============================================================================
# VALUE PROPOSITION FORMULAS
# =============================================================================

VALUE_PROP_FORMULAS = {
    "classic": {
        "name": "Classic Value Prop",
        "template": "We help [target customer] [achieve outcome] by [unique mechanism]",
        "example": "We help B2B SaaS companies reduce churn by 40% through predictive analytics",
    },
    "problem_solution": {
        "name": "Problem-Solution",
        "template": "[Target customer] struggle with [problem]. [Product] solves this by [solution]",
        "example": "Marketing teams waste 10 hours/week on reporting. Acme automates it in 5 minutes.",
    },
    "before_after": {
        "name": "Before-After-Bridge",
        "template": "Before: [painful situation]. After: [desired outcome]. Bridge: [your solution]",
        "example": "Before: Chasing leads manually. After: Qualified meetings on autopilot. How: Our AI SDR.",
    },
    "unique_mechanism": {
        "name": "Unique Mechanism",
        "template": "The only [category] with [unique feature] that [delivers benefit]",
        "example": "The only CRM with built-in revenue intelligence that predicts deal outcomes.",
    },
    "proof_based": {
        "name": "Proof-Based",
        "template": "[Specific result] achieved by [number of customers] using [product]",
        "example": "43% lower CAC achieved by 2,847 companies using our attribution platform.",
    },
    "comparison": {
        "name": "Vs. Alternative",
        "template": "[Benefit of your product] vs. [pain of alternative]",
        "example": "One-click deploys vs. 3-hour DevOps tickets.",
    },
}


# =============================================================================
# HEADLINE FORMULAS
# =============================================================================

HEADLINE_FORMULAS = {
    "how_to": {
        "template": "How to [achieve desired outcome] [without common pain]",
        "examples": [
            "How to scale content production without hiring",
            "How to get enterprise clients without cold calling",
        ],
    },
    "number_list": {
        "template": "[Number] ways to [achieve outcome] [qualifier]",
        "examples": [
            "7 ways to reduce churn that actually work",
            "12 landing page mistakes killing your conversions",
        ],
    },
    "question": {
        "template": "Are you making these [number] [category] mistakes?",
        "examples": [
            "Are you making these 5 pricing mistakes?",
            "Is your onboarding costing you customers?",
        ],
    },
    "secret": {
        "template": "The [adjective] secret [audience] use to [outcome]",
        "examples": [
            "The simple secret top founders use to fundraise faster",
            "The hidden metric that predicts churn 30 days early",
        ],
    },
    "warning": {
        "template": "Warning: [common practice] is [negative consequence]",
        "examples": [
            "Warning: Your 'best practice' is killing conversions",
            "Warning: This common SEO tactic can get you penalized",
        ],
    },
    "direct": {
        "template": "[Exact outcome] for [exact audience]",
        "examples": [
            "More demos booked. Less manual work.",
            "Enterprise security. Startup speed.",
        ],
    },
}


# =============================================================================
# POSITIONING VALIDATION CHECKLIST
# =============================================================================

POSITIONING_CHECKLIST = {
    "specific": {
        "question": "Is it specific?",
        "bad": "Better results",
        "good": "20 lbs in 6 weeks",
        "test": "Can you measure it? Does it have a number or timeframe?",
    },
    "differentiated": {
        "question": "Is it differentiated?",
        "bad": "Best-in-class solution",
        "good": "The only CRM with built-in revenue intelligence",
        "test": "Could a competitor claim the exact same thing?",
    },
    "believable": {
        "question": "Is it believable?",
        "bad": "10x your revenue overnight",
        "good": "43% higher conversions (based on 2,847 customers)",
        "test": "Is there proof, mechanism, or social proof to support it?",
    },
    "relevant": {
        "question": "Is it relevant to the audience?",
        "bad": "Cutting-edge AI technology",
        "good": "Close 3 more deals per month",
        "test": "Does it address what they actually care about?",
    },
    "memorable": {
        "question": "Is it memorable?",
        "bad": "Integrated platform solution",
        "good": "The anti-CRM",
        "test": "Would someone remember and repeat it?",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_stage_strategy(stage: MarketStage) -> MarketStageStrategy:
    """Get positioning strategy for a market stage."""
    return MARKET_STAGE_STRATEGIES[stage]


def get_angle_framework(angle: PositioningAngle) -> AngleFramework:
    """Get framework for a positioning angle."""
    return POSITIONING_ANGLES[angle]


def suggest_angles_for_context(
    market_stage: Optional[MarketStage] = None,
    product_type: Optional[str] = None,
    audience_sophistication: Optional[str] = None,
) -> list[PositioningAngle]:
    """Suggest positioning angles based on context."""
    suggestions = []

    if market_stage == MarketStage.NEW:
        suggestions.extend([PositioningAngle.TRANSFORMATION, PositioningAngle.SPEED])
    elif market_stage == MarketStage.CROWDED:
        suggestions.extend([PositioningAngle.CONTRARIAN, PositioningAngle.SPECIFICITY])
    elif market_stage == MarketStage.JADED:
        suggestions.extend([PositioningAngle.CONTRARIAN, PositioningAngle.ENEMY])
    elif market_stage == MarketStage.MATURE:
        suggestions.extend([PositioningAngle.SPECIFICITY, PositioningAngle.TRANSFORMATION])

    # Default to most versatile angles
    if not suggestions:
        suggestions = [PositioningAngle.TRANSFORMATION, PositioningAngle.SPEED]

    return suggestions


def validate_positioning(
    headline: str,
    value_prop: str,
) -> dict[str, dict]:
    """Validate positioning against the checklist."""
    results = {}
    for key, check in POSITIONING_CHECKLIST.items():
        # Simple heuristic checks
        results[key] = {
            "question": check["question"],
            "good_example": check["good"],
            "test": check["test"],
            # In practice, an LLM would evaluate these
            "needs_review": True,
        }
    return results


def get_all_frameworks() -> dict:
    """Get all positioning frameworks for agent injection."""
    return {
        "market_stages": {
            stage.value: {
                "approach": strategy.approach,
                "template": strategy.template,
                "example": strategy.example,
            }
            for stage, strategy in MARKET_STAGE_STRATEGIES.items()
        },
        "positioning_angles": {
            angle.value: {
                "description": framework.description,
                "template": framework.template,
                "examples": framework.examples,
                "best_for": framework.best_for,
                "avoid_when": framework.avoid_when,
            }
            for angle, framework in POSITIONING_ANGLES.items()
        },
        "value_prop_formulas": VALUE_PROP_FORMULAS,
        "headline_formulas": HEADLINE_FORMULAS,
        "validation_checklist": POSITIONING_CHECKLIST,
    }
