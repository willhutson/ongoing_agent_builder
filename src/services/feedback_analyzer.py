"""
FeedbackAnalyzer: Auto-Learning from Agent Output Feedback

Analyzes corrections and feedback to:
1. Identify patterns in rejected/corrected outputs
2. Extract learnings to improve future outputs
3. Auto-update client tuning configurations
"""

import json
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import anthropic

from ..config import get_settings
from ..db.models import (
    AgentOutputFeedback,
    ClientTuningConfig,
    FeedbackType,
    TuningTier,
    TuningAuditLog,
)


class FeedbackAnalyzer:
    """
    Analyzes feedback on agent outputs to extract learnings.

    Uses Claude to identify patterns in corrections and
    automatically updates client tuning configurations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self._client: Optional[anthropic.AsyncAnthropic] = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        """Lazy-initialize Anthropic client."""
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(
                api_key=self.settings.anthropic_api_key
            )
        return self._client

    async def analyze_feedback(
        self,
        feedback_id: UUID,
        auto_apply: bool = False,
    ) -> dict:
        """
        Analyze a single feedback entry.

        Args:
            feedback_id: ID of the feedback to analyze
            auto_apply: If True, automatically apply learnings to tuning

        Returns:
            Analysis results with extracted patterns
        """
        # Load feedback
        result = await self.db.execute(
            select(AgentOutputFeedback)
            .where(AgentOutputFeedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()

        if not feedback:
            raise ValueError(f"Feedback not found: {feedback_id}")

        if feedback.analyzed:
            return feedback.analysis_result

        # Analyze based on feedback type
        if feedback.feedback_type == FeedbackType.CORRECTED:
            analysis = await self._analyze_correction(feedback)
        elif feedback.feedback_type == FeedbackType.REJECTED:
            analysis = await self._analyze_rejection(feedback)
        else:  # APPROVED
            analysis = await self._analyze_approval(feedback)

        # Update feedback record
        feedback.analyzed = True
        feedback.analysis_result = analysis
        await self.db.commit()

        # Auto-apply if requested
        if auto_apply and feedback.client_id:
            await self._apply_learnings(feedback.client_id, analysis)
            feedback.applied_to_tuning = True
            await self.db.commit()

        return analysis

    async def analyze_batch(
        self,
        instance_id: UUID,
        client_id: Optional[UUID] = None,
        since: Optional[datetime] = None,
        auto_apply: bool = False,
    ) -> dict:
        """
        Analyze a batch of unanalyzed feedback.

        Args:
            instance_id: Instance to analyze feedback for
            client_id: Optional specific client
            since: Only analyze feedback after this time
            auto_apply: Automatically apply learnings

        Returns:
            Summary of analysis results
        """
        # Build query
        conditions = [
            AgentOutputFeedback.instance_id == instance_id,
            AgentOutputFeedback.analyzed == False,
        ]

        if client_id:
            conditions.append(AgentOutputFeedback.client_id == client_id)

        if since:
            conditions.append(AgentOutputFeedback.feedback_at >= since)

        result = await self.db.execute(
            select(AgentOutputFeedback)
            .where(and_(*conditions))
            .order_by(AgentOutputFeedback.feedback_at)
            .limit(100)  # Process in batches
        )
        feedback_items = result.scalars().all()

        # Analyze each
        results = {
            "total": len(feedback_items),
            "analyzed": 0,
            "patterns_found": [],
            "errors": [],
        }

        for feedback in feedback_items:
            try:
                analysis = await self.analyze_feedback(
                    feedback.id,
                    auto_apply=auto_apply,
                )
                results["analyzed"] += 1
                if analysis.get("patterns"):
                    results["patterns_found"].extend(analysis["patterns"])
            except Exception as e:
                results["errors"].append({
                    "feedback_id": str(feedback.id),
                    "error": str(e),
                })

        return results

    async def _analyze_correction(self, feedback: AgentOutputFeedback) -> dict:
        """Analyze a corrected output to extract patterns."""
        prompt = f"""Analyze this correction to an AI agent's output.

ORIGINAL OUTPUT:
{feedback.original_output}

CORRECTED OUTPUT:
{feedback.corrected_output}

CORRECTION REASON (if provided):
{feedback.correction_reason or "Not specified"}

Identify:
1. What was wrong with the original
2. What patterns should be avoided
3. What patterns should be followed
4. Specific words/phrases to never use
5. Specific words/phrases to prefer

Respond in JSON format:
{{
    "issue_type": "tone|accuracy|style|content|length|other",
    "patterns": [
        {{"type": "avoid", "pattern": "...", "reason": "..."}},
        {{"type": "prefer", "pattern": "...", "reason": "..."}}
    ],
    "words_to_avoid": ["..."],
    "words_to_prefer": ["..."],
    "summary": "Brief description of the correction"
}}"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",  # Use faster model for analysis
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response
        try:
            content = response.content[0].text
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            return {
                "issue_type": "unknown",
                "patterns": [],
                "summary": "Could not parse analysis",
                "raw_response": response.content[0].text,
            }

    async def _analyze_rejection(self, feedback: AgentOutputFeedback) -> dict:
        """Analyze a rejected output."""
        prompt = f"""Analyze why this AI agent output was rejected.

REJECTED OUTPUT:
{feedback.original_output}

REJECTION REASON (if provided):
{feedback.correction_reason or "Not specified"}

Identify what patterns led to rejection and should be avoided.

Respond in JSON format:
{{
    "issue_type": "tone|accuracy|style|content|length|other",
    "patterns": [
        {{"type": "avoid", "pattern": "...", "reason": "..."}}
    ],
    "summary": "Brief description of why it was rejected"
}}"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            return {
                "issue_type": "unknown",
                "patterns": [],
                "summary": "Could not parse analysis",
            }

    async def _analyze_approval(self, feedback: AgentOutputFeedback) -> dict:
        """Analyze an approved output to identify positive patterns."""
        prompt = f"""Analyze this approved AI agent output to identify what worked well.

APPROVED OUTPUT:
{feedback.original_output}

Identify patterns that contributed to its success.

Respond in JSON format:
{{
    "patterns": [
        {{"type": "positive", "pattern": "...", "reason": "..."}}
    ],
    "summary": "Brief description of what worked well"
}}"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            return {
                "patterns": [],
                "summary": "Could not parse analysis",
            }

    async def _apply_learnings(self, client_id: UUID, analysis: dict) -> None:
        """Apply analyzed patterns to client tuning config."""
        # Get or create client tuning config
        result = await self.db.execute(
            select(ClientTuningConfig)
            .where(ClientTuningConfig.client_id == client_id)
        )
        tuning = result.scalar_one_or_none()

        if not tuning:
            tuning = ClientTuningConfig(client_id=client_id)
            self.db.add(tuning)

        # Update learned preferences
        learned = tuning.learned_preferences or {
            "positive_patterns": [],
            "negative_patterns": [],
            "corrections": [],
        }

        for pattern in analysis.get("patterns", []):
            pattern_text = pattern.get("pattern", "")
            if not pattern_text:
                continue

            if pattern["type"] == "positive":
                if pattern_text not in learned["positive_patterns"]:
                    learned["positive_patterns"].append(pattern_text)
            elif pattern["type"] in ("avoid", "negative"):
                if pattern_text not in learned["negative_patterns"]:
                    learned["negative_patterns"].append(pattern_text)

        # Keep lists manageable
        learned["positive_patterns"] = learned["positive_patterns"][-20:]
        learned["negative_patterns"] = learned["negative_patterns"][-20:]

        tuning.learned_preferences = learned

        # Update content rules if words identified
        content_rules = tuning.content_rules or {
            "always": [],
            "never": [],
            "prefer": [],
            "avoid": [],
        }

        for word in analysis.get("words_to_avoid", []):
            if word and word not in content_rules["never"]:
                content_rules["never"].append(word)

        for word in analysis.get("words_to_prefer", []):
            if word and word not in content_rules["prefer"]:
                content_rules["prefer"].append(word)

        tuning.content_rules = content_rules

        # Log the change
        audit_log = TuningAuditLog(
            tuning_tier=TuningTier.CLIENT,
            client_id=client_id,
            field_changed="learned_preferences",
            old_value=None,  # Skip old value for auto-learning
            new_value={"patterns_added": len(analysis.get("patterns", []))},
            changed_by="feedback_analyzer",
            change_reason=f"Auto-learned from feedback: {analysis.get('summary', 'N/A')}",
        )
        self.db.add(audit_log)
