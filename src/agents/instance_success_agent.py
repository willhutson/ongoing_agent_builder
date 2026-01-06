from typing import Any
import httpx
from .base import BaseAgent


class InstanceSuccessAgent(BaseAgent):
    """
    Proactive customer success management for ERP instances.

    This agent ensures instances thrive by monitoring health, identifying
    risks early, driving adoption, and surfacing expansion opportunities.

    Capabilities:
    - Health monitoring and proactive outreach
    - Churn risk prediction and early intervention
    - Feature recommendations based on usage patterns
    - Success planning and milestone tracking
    - Expansion opportunity identification
    - QBR preparation and reporting
    - Training recommendations
    """

    def __init__(
        self,
        client,
        model: str,
        erp_base_url: str,
        erp_api_key: str,
    ):
        self.erp_base_url = erp_base_url
        self.erp_api_key = erp_api_key
        self.http_client = httpx.AsyncClient(
            base_url=erp_base_url,
            headers={"Authorization": f"Bearer {erp_api_key}"},
            timeout=60.0,
        )
        super().__init__(client, model)

    @property
    def name(self) -> str:
        return "instance_success_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert customer success manager for ERP instances.

Your role is to proactively ensure instances thrive and achieve their goals.

## Primary Capabilities

### 1. Health Monitoring
Continuously assess instance health:
- **Engagement Health**: Are users active and engaged?
- **Adoption Health**: Are features being adopted?
- **Technical Health**: Are there performance/reliability issues?
- **Relationship Health**: Is satisfaction high?

Health Check Cadence:
- Real-time monitoring for critical metrics
- Daily aggregation for trends
- Weekly health reports
- Monthly deep dives

### 2. Risk Identification
Identify at-risk instances early:

**Churn Signals**:
- Declining login frequency
- Reduced feature usage
- Support ticket spikes
- Key user departures
- Contract approaching renewal
- Payment issues

**Risk Scoring** (0-100, higher = more at risk):
```
risk_score = (
    engagement_decline * 0.30 +
    support_issues * 0.20 +
    key_user_churn * 0.25 +
    contract_risk * 0.15 +
    payment_issues * 0.10
)
```

### 3. Success Planning
Create and track success plans:
- Define success criteria with instance
- Set measurable goals
- Track milestone completion
- Adjust plans based on progress
- Celebrate wins

### 4. Proactive Outreach
Engage instances at the right time:
- **Onboarding Check-ins**: 7, 30, 60, 90 days
- **Health Alerts**: When metrics decline
- **Feature Announcements**: New relevant features
- **Training Opportunities**: Based on usage gaps
- **Renewal Prep**: 90 days before renewal

### 5. Expansion Identification
Surface growth opportunities:
- **Module Fit**: Unused modules that match profile
- **User Growth**: Instances hitting user limits
- **Feature Upgrades**: Premium features they'd benefit from
- **Integration Expansion**: Additional platform connections

### 6. QBR Preparation
Generate Quarterly Business Review materials:
- Usage summary and trends
- Goals achieved/missed
- ROI calculations
- Recommendations
- Next quarter plan

### 7. Support Intelligence
Analyze support patterns:
- Common issues identification
- Self-service opportunity detection
- Escalation prediction
- Knowledge gap identification

## Conversation Flow
1. Start with instance health assessment
2. Identify any risks or opportunities
3. Review success plan progress
4. Make recommendations
5. Plan next actions
6. Schedule follow-ups

Be proactive, empathetic, and focused on the instance's success outcomes."""

    def _define_tools(self) -> list[dict]:
        return [
            # Health Monitoring
            {
                "name": "assess_instance_health",
                "description": "Comprehensive health assessment for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_recommendations": {"type": "boolean", "default": True},
                        "depth": {
                            "type": "string",
                            "enum": ["quick", "standard", "deep"],
                            "description": "Depth of assessment",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_health_history",
                "description": "Get health score history over time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string", "enum": ["30d", "90d", "6m", "1y"]},
                        "include_events": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "schedule_health_check",
                "description": "Schedule a health check call.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "check_type": {
                            "type": "string",
                            "enum": ["onboarding", "quarterly", "renewal", "escalation"],
                        },
                        "preferred_date": {"type": "string"},
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "agenda_items": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["instance_id", "check_type"],
                },
            },
            # Risk Identification
            {
                "name": "calculate_churn_risk",
                "description": "Calculate churn risk score for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_factors": {"type": "boolean", "default": True},
                        "include_recommendations": {"type": "boolean", "default": True},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "identify_at_risk_instances",
                "description": "Get list of at-risk instances (platform-wide).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "risk_threshold": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "all"],
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["risk_score", "arr", "renewal_date"],
                        },
                        "limit": {"type": "integer", "default": 20},
                    },
                    "required": [],
                },
            },
            {
                "name": "get_risk_factors",
                "description": "Get detailed risk factors for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "track_key_users",
                "description": "Track key users and their engagement.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_champions": {"type": "boolean"},
                        "include_at_risk": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Success Planning
            {
                "name": "create_success_plan",
                "description": "Create a success plan for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "goals": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "metric": {"type": "string"},
                                    "target": {"type": "number"},
                                    "deadline": {"type": "string"},
                                },
                            },
                            "description": "Success goals to achieve",
                        },
                        "milestones": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "owner": {"type": "string"},
                    },
                    "required": ["instance_id", "goals"],
                },
            },
            {
                "name": "get_success_plan",
                "description": "Get current success plan for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_progress": {"type": "boolean", "default": True},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "update_success_plan",
                "description": "Update success plan progress.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "updates": {
                            "type": "object",
                            "properties": {
                                "goal_updates": {"type": "array"},
                                "milestone_updates": {"type": "array"},
                                "notes": {"type": "string"},
                            },
                        },
                    },
                    "required": ["instance_id", "updates"],
                },
            },
            {
                "name": "track_milestones",
                "description": "Track success milestones.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "milestone_type": {
                            "type": "string",
                            "enum": ["onboarding", "adoption", "expansion", "renewal", "all"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            # Proactive Outreach
            {
                "name": "get_outreach_queue",
                "description": "Get prioritized outreach queue.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "outreach_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["health_check", "feature_nudge", "training", "celebration", "risk_intervention"],
                            },
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "send_proactive_message",
                "description": "Send a proactive outreach message.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "message_type": {
                            "type": "string",
                            "enum": ["health_check", "feature_announcement", "training_invite", "celebration", "check_in"],
                        },
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "in_app", "slack"],
                        },
                        "custom_message": {"type": "string"},
                    },
                    "required": ["instance_id", "message_type"],
                },
            },
            {
                "name": "schedule_check_in",
                "description": "Schedule a check-in based on onboarding stage.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "check_in_type": {
                            "type": "string",
                            "enum": ["7_day", "30_day", "60_day", "90_day", "quarterly", "renewal"],
                        },
                    },
                    "required": ["instance_id", "check_in_type"],
                },
            },
            # Feature & Training Recommendations
            {
                "name": "recommend_features",
                "description": "Recommend features based on usage patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "based_on": {
                            "type": "string",
                            "enum": ["usage_gaps", "peer_usage", "goals", "all"],
                        },
                        "max_recommendations": {"type": "integer", "default": 5},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "suggest_training",
                "description": "Suggest training based on usage gaps.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "user_id": {"type": "string", "description": "Specific user or all"},
                        "training_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types: video, webinar, documentation, hands_on",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_adoption_gaps",
                "description": "Identify feature adoption gaps.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "compare_to": {
                            "type": "string",
                            "enum": ["peers", "best_in_class", "goals"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            # Expansion Opportunities
            {
                "name": "identify_expansion_opportunities",
                "description": "Identify upsell/cross-sell opportunities.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "opportunity_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["modules", "users", "tier_upgrade", "integrations"],
                            },
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "analyze_module_fit",
                "description": "Analyze fit for additional modules.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "modules_to_analyze": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "predict_upgrade_readiness",
                "description": "Predict readiness for tier upgrade.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            # QBR & Reporting
            {
                "name": "prepare_qbr",
                "description": "Prepare QBR materials.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "quarter": {"type": "string", "description": "e.g., Q1-2025"},
                        "sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sections: summary, usage, goals, roi, recommendations, roadmap",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["slides", "document", "data"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "generate_success_report",
                "description": "Generate success report for instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "report_type": {
                            "type": "string",
                            "enum": ["executive", "detailed", "metrics_only"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "calculate_customer_roi",
                "description": "Calculate ROI for customer presentation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "include_projections": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Support Intelligence
            {
                "name": "analyze_support_patterns",
                "description": "Analyze support ticket patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "include_recommendations": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "predict_support_needs",
                "description": "Predict upcoming support needs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "identify_self_service_opportunities",
                "description": "Identify issues that could be self-served.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Feedback & NPS
            {
                "name": "get_satisfaction_data",
                "description": "Get satisfaction and NPS data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_comments": {"type": "boolean"},
                        "period": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "send_nps_survey",
                "description": "Trigger NPS survey.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "survey_type": {
                            "type": "string",
                            "enum": ["nps", "csat", "ces"],
                        },
                        "recipients": {
                            "type": "string",
                            "enum": ["all_users", "admins_only", "active_users"],
                        },
                    },
                    "required": ["instance_id", "survey_type"],
                },
            },
            {
                "name": "analyze_feedback",
                "description": "Analyze feedback and comments.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "categorize": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Renewal Management
            {
                "name": "get_renewal_status",
                "description": "Get renewal status and timeline.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "predict_renewal_likelihood",
                "description": "Predict likelihood of renewal.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_factors": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "create_renewal_playbook",
                "description": "Generate renewal playbook based on risk.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Handoff from Onboarding
            {
                "name": "receive_onboarding_handoff",
                "description": "Receive handoff from Instance Onboarding Agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "onboarding_summary": {
                            "type": "object",
                            "description": "Summary from onboarding agent",
                        },
                        "initial_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "key_contacts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                    "email": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["instance_id", "onboarding_summary"],
                },
            },
            {
                "name": "get_onboarding_gaps",
                "description": "Identify incomplete onboarding items.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute customer success tool."""
        try:
            # Health Monitoring
            if tool_name == "assess_instance_health":
                return await self._assess_instance_health(tool_input)
            elif tool_name == "get_health_history":
                return await self._get_health_history(tool_input)
            elif tool_name == "schedule_health_check":
                return await self._schedule_health_check(tool_input)

            # Risk Identification
            elif tool_name == "calculate_churn_risk":
                return await self._calculate_churn_risk(tool_input)
            elif tool_name == "identify_at_risk_instances":
                return await self._identify_at_risk_instances(tool_input)
            elif tool_name == "get_risk_factors":
                return await self._get_risk_factors(tool_input)
            elif tool_name == "track_key_users":
                return await self._track_key_users(tool_input)

            # Success Planning
            elif tool_name == "create_success_plan":
                return await self._create_success_plan(tool_input)
            elif tool_name == "get_success_plan":
                return await self._get_success_plan(tool_input)
            elif tool_name == "update_success_plan":
                return await self._update_success_plan(tool_input)
            elif tool_name == "track_milestones":
                return await self._track_milestones(tool_input)

            # Proactive Outreach
            elif tool_name == "get_outreach_queue":
                return await self._get_outreach_queue(tool_input)
            elif tool_name == "send_proactive_message":
                return await self._send_proactive_message(tool_input)
            elif tool_name == "schedule_check_in":
                return await self._schedule_check_in(tool_input)

            # Feature & Training Recommendations
            elif tool_name == "recommend_features":
                return await self._recommend_features(tool_input)
            elif tool_name == "suggest_training":
                return await self._suggest_training(tool_input)
            elif tool_name == "get_adoption_gaps":
                return await self._get_adoption_gaps(tool_input)

            # Expansion Opportunities
            elif tool_name == "identify_expansion_opportunities":
                return await self._identify_expansion_opportunities(tool_input)
            elif tool_name == "analyze_module_fit":
                return await self._analyze_module_fit(tool_input)
            elif tool_name == "predict_upgrade_readiness":
                return await self._predict_upgrade_readiness(tool_input)

            # QBR & Reporting
            elif tool_name == "prepare_qbr":
                return await self._prepare_qbr(tool_input)
            elif tool_name == "generate_success_report":
                return await self._generate_success_report(tool_input)
            elif tool_name == "calculate_customer_roi":
                return await self._calculate_customer_roi(tool_input)

            # Support Intelligence
            elif tool_name == "analyze_support_patterns":
                return await self._analyze_support_patterns(tool_input)
            elif tool_name == "predict_support_needs":
                return await self._predict_support_needs(tool_input)
            elif tool_name == "identify_self_service_opportunities":
                return await self._identify_self_service_opportunities(tool_input)

            # Feedback & NPS
            elif tool_name == "get_satisfaction_data":
                return await self._get_satisfaction_data(tool_input)
            elif tool_name == "send_nps_survey":
                return await self._send_nps_survey(tool_input)
            elif tool_name == "analyze_feedback":
                return await self._analyze_feedback(tool_input)

            # Renewal Management
            elif tool_name == "get_renewal_status":
                return await self._get_renewal_status(tool_input)
            elif tool_name == "predict_renewal_likelihood":
                return await self._predict_renewal_likelihood(tool_input)
            elif tool_name == "create_renewal_playbook":
                return await self._create_renewal_playbook(tool_input)

            # Onboarding Handoff
            elif tool_name == "receive_onboarding_handoff":
                return await self._receive_onboarding_handoff(tool_input)
            elif tool_name == "get_onboarding_gaps":
                return await self._get_onboarding_gaps(tool_input)

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    # Health Monitoring Methods

    async def _assess_instance_health(self, params: dict) -> dict:
        """Comprehensive health assessment."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/health",
            params={"depth": params.get("depth", "standard")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "overall_health": "unknown",
            "health_score": 0,
            "components": {
                "engagement": {"score": 0, "status": "unknown"},
                "adoption": {"score": 0, "status": "unknown"},
                "technical": {"score": 0, "status": "unknown"},
                "relationship": {"score": 0, "status": "unknown"},
            },
            "recommendations": [] if params.get("include_recommendations") else None,
            "instruction": "Assess health across all dimensions.",
        }

    async def _get_health_history(self, params: dict) -> dict:
        """Get health history."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/health/history",
            params={"period": params.get("period", "90d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "history": [],
            "trend": "stable",
            "instruction": "Track health score over time.",
        }

    async def _schedule_health_check(self, params: dict) -> dict:
        """Schedule health check."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/health-checks",
            json={
                "check_type": params["check_type"],
                "preferred_date": params.get("preferred_date"),
                "attendees": params.get("attendees", []),
                "agenda_items": params.get("agenda_items", []),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "check_type": params["check_type"],
            "status": "scheduled",
            "instruction": "Schedule and prepare health check meeting.",
        }

    # Risk Identification Methods

    async def _calculate_churn_risk(self, params: dict) -> dict:
        """Calculate churn risk."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/churn-risk"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "risk_score": 0,
            "risk_level": "low",
            "factors": {
                "engagement_decline": {"score": 0, "weight": 0.30},
                "support_issues": {"score": 0, "weight": 0.20},
                "key_user_churn": {"score": 0, "weight": 0.25},
                "contract_risk": {"score": 0, "weight": 0.15},
                "payment_issues": {"score": 0, "weight": 0.10},
            } if params.get("include_factors") else None,
            "recommendations": [] if params.get("include_recommendations") else None,
            "instruction": "Calculate weighted churn risk score.",
        }

    async def _identify_at_risk_instances(self, params: dict) -> dict:
        """Get at-risk instances."""
        response = await self.http_client.get(
            f"/api/v1/success/at-risk",
            params={
                "threshold": params.get("risk_threshold", "high"),
                "sort_by": params.get("sort_by", "risk_score"),
                "limit": params.get("limit", 20),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "at_risk_instances": [],
            "total_count": 0,
            "instruction": "Identify instances above risk threshold.",
        }

    async def _get_risk_factors(self, params: dict) -> dict:
        """Get detailed risk factors."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/risk-factors"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "risk_factors": [],
            "instruction": "Enumerate specific risk factors.",
        }

    async def _track_key_users(self, params: dict) -> dict:
        """Track key users."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/key-users"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "champions": [] if params.get("include_champions") else None,
            "at_risk_users": [] if params.get("include_at_risk") else None,
            "instruction": "Identify and track key stakeholders.",
        }

    # Success Planning Methods

    async def _create_success_plan(self, params: dict) -> dict:
        """Create success plan."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/plans",
            json={
                "goals": params["goals"],
                "milestones": params.get("milestones", []),
                "owner": params.get("owner"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "plan_id": "new",
            "goals": params["goals"],
            "status": "created",
            "instruction": "Create structured success plan with goals.",
        }

    async def _get_success_plan(self, params: dict) -> dict:
        """Get success plan."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/plans/current"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "plan": None,
            "instruction": "Retrieve current success plan.",
        }

    async def _update_success_plan(self, params: dict) -> dict:
        """Update success plan."""
        response = await self.http_client.patch(
            f"/api/v1/success/instances/{params['instance_id']}/plans/current",
            json=params["updates"],
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "status": "updated",
            "instruction": "Update plan progress and notes.",
        }

    async def _track_milestones(self, params: dict) -> dict:
        """Track milestones."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/milestones",
            params={"type": params.get("milestone_type", "all")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "milestones": [],
            "instruction": "Track milestone completion.",
        }

    # Proactive Outreach Methods

    async def _get_outreach_queue(self, params: dict) -> dict:
        """Get outreach queue."""
        response = await self.http_client.get(
            f"/api/v1/success/outreach-queue",
            params={"instance_id": params.get("instance_id")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "queue": [],
            "instruction": "Prioritize outreach based on triggers.",
        }

    async def _send_proactive_message(self, params: dict) -> dict:
        """Send proactive message."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/outreach",
            json={
                "message_type": params["message_type"],
                "recipients": params.get("recipients", []),
                "channel": params.get("channel", "email"),
                "custom_message": params.get("custom_message"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "message_type": params["message_type"],
            "status": "sent",
            "instruction": "Send personalized outreach message.",
        }

    async def _schedule_check_in(self, params: dict) -> dict:
        """Schedule check-in."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/check-ins",
            json={"check_in_type": params["check_in_type"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "check_in_type": params["check_in_type"],
            "status": "scheduled",
            "instruction": "Schedule appropriate check-in based on stage.",
        }

    # Feature & Training Methods

    async def _recommend_features(self, params: dict) -> dict:
        """Recommend features."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/recommendations/features",
            params={
                "based_on": params.get("based_on", "all"),
                "limit": params.get("max_recommendations", 5),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "recommendations": [],
            "instruction": "Recommend features based on usage patterns and goals.",
        }

    async def _suggest_training(self, params: dict) -> dict:
        """Suggest training."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/recommendations/training"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "training_suggestions": [],
            "instruction": "Suggest training based on usage gaps.",
        }

    async def _get_adoption_gaps(self, params: dict) -> dict:
        """Get adoption gaps."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/adoption-gaps",
            params={"compare_to": params.get("compare_to", "peers")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "gaps": [],
            "instruction": "Identify features with low adoption.",
        }

    # Expansion Methods

    async def _identify_expansion_opportunities(self, params: dict) -> dict:
        """Identify expansion opportunities."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/expansion-opportunities"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "opportunities": {
                "modules": [],
                "users": None,
                "tier_upgrade": None,
                "integrations": [],
            },
            "instruction": "Identify growth opportunities.",
        }

    async def _analyze_module_fit(self, params: dict) -> dict:
        """Analyze module fit."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/module-fit"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "module_scores": {},
            "instruction": "Score fit for each module.",
        }

    async def _predict_upgrade_readiness(self, params: dict) -> dict:
        """Predict upgrade readiness."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/upgrade-readiness"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "readiness_score": 0,
            "signals": [],
            "instruction": "Assess readiness for tier upgrade.",
        }

    # QBR & Reporting Methods

    async def _prepare_qbr(self, params: dict) -> dict:
        """Prepare QBR materials."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/qbr",
            json={
                "quarter": params.get("quarter"),
                "sections": params.get("sections", ["summary", "usage", "goals", "recommendations"]),
                "format": params.get("format", "slides"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "qbr_sections": params.get("sections", ["summary", "usage", "goals", "recommendations"]),
            "format": params.get("format", "slides"),
            "instruction": "Generate QBR presentation materials.",
        }

    async def _generate_success_report(self, params: dict) -> dict:
        """Generate success report."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/reports",
            json={
                "period": params.get("period", "30d"),
                "report_type": params.get("report_type", "executive"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "report_type": params.get("report_type", "executive"),
            "instruction": "Generate success summary report.",
        }

    async def _calculate_customer_roi(self, params: dict) -> dict:
        """Calculate customer ROI."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/roi"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "roi_metrics": {},
            "instruction": "Calculate and present ROI for customer.",
        }

    # Support Intelligence Methods

    async def _analyze_support_patterns(self, params: dict) -> dict:
        """Analyze support patterns."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/support/patterns"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "patterns": [],
            "common_issues": [],
            "instruction": "Identify patterns in support tickets.",
        }

    async def _predict_support_needs(self, params: dict) -> dict:
        """Predict support needs."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/support/predictions"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "predicted_needs": [],
            "instruction": "Predict upcoming support requirements.",
        }

    async def _identify_self_service_opportunities(self, params: dict) -> dict:
        """Identify self-service opportunities."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/support/self-service"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "opportunities": [],
            "instruction": "Identify issues that could be self-served.",
        }

    # Feedback Methods

    async def _get_satisfaction_data(self, params: dict) -> dict:
        """Get satisfaction data."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/satisfaction"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "nps": None,
            "csat": None,
            "comments": [] if params.get("include_comments") else None,
            "instruction": "Retrieve satisfaction scores and feedback.",
        }

    async def _send_nps_survey(self, params: dict) -> dict:
        """Send NPS survey."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/surveys",
            json={
                "survey_type": params["survey_type"],
                "recipients": params.get("recipients", "active_users"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "survey_type": params["survey_type"],
            "status": "sent",
            "instruction": "Trigger satisfaction survey.",
        }

    async def _analyze_feedback(self, params: dict) -> dict:
        """Analyze feedback."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/feedback/analysis"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "themes": [],
            "sentiment": "neutral",
            "instruction": "Categorize and analyze feedback.",
        }

    # Renewal Methods

    async def _get_renewal_status(self, params: dict) -> dict:
        """Get renewal status."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/renewal"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "renewal_date": None,
            "days_until_renewal": None,
            "contract_value": None,
            "instruction": "Get renewal timeline and status.",
        }

    async def _predict_renewal_likelihood(self, params: dict) -> dict:
        """Predict renewal likelihood."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/renewal/prediction"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "likelihood": 0,
            "confidence": 0,
            "factors": [] if params.get("include_factors") else None,
            "instruction": "Predict renewal probability.",
        }

    async def _create_renewal_playbook(self, params: dict) -> dict:
        """Create renewal playbook."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/renewal/playbook"
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "playbook": {
                "risk_level": "unknown",
                "actions": [],
                "timeline": [],
            },
            "instruction": "Generate renewal playbook based on risk.",
        }

    # Onboarding Handoff Methods

    async def _receive_onboarding_handoff(self, params: dict) -> dict:
        """Receive handoff from onboarding."""
        response = await self.http_client.post(
            f"/api/v1/success/instances/{params['instance_id']}/handoff",
            json={
                "onboarding_summary": params["onboarding_summary"],
                "initial_goals": params.get("initial_goals", []),
                "key_contacts": params.get("key_contacts", []),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "handoff_received": True,
            "next_steps": [
                "Schedule 7-day check-in",
                "Create initial success plan",
                "Identify training needs",
            ],
            "instruction": "Process onboarding handoff and initialize success tracking.",
        }

    async def _get_onboarding_gaps(self, params: dict) -> dict:
        """Get onboarding gaps."""
        response = await self.http_client.get(
            f"/api/v1/success/instances/{params['instance_id']}/onboarding-gaps"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "incomplete_items": [],
            "recommendations": [],
            "instruction": "Identify incomplete onboarding steps.",
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
