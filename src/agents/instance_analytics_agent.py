from typing import Any
import httpx
from .base import BaseAgent


class InstanceAnalyticsAgent(BaseAgent):
    """
    Platform-level analytics for ERP instances.

    This agent provides intelligence about how instances are performing,
    used for capacity planning, product decisions, and identifying patterns.

    Capabilities:
    - Usage metrics aggregation and trending
    - Health scoring with composite metrics
    - Peer benchmarking by vertical/size/region
    - Anomaly detection for proactive alerts
    - Growth forecasting for capacity planning
    - Feature adoption tracking
    - ROI calculation and value tracking
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
        return "instance_analytics_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert platform analytics specialist for ERP instances.

Your role is to provide deep insights into how instances are performing across the platform.

## Primary Capabilities

### 1. Usage Metrics
Track and analyze how instances are being used:
- **API Calls**: Volume, patterns, peak hours
- **Active Users**: DAU, WAU, MAU trends
- **Session Data**: Duration, depth, frequency
- **Feature Usage**: Heatmaps, adoption funnels
- **Module Utilization**: Which modules are active vs dormant

### 2. Health Scoring
Calculate composite health scores based on:
- **Uptime**: Instance availability
- **Performance**: Response times, error rates
- **Engagement**: User activity levels
- **Growth**: User/data growth trajectory
- **Integration Health**: Connected platform status

Health Score Formula:
```
health_score = (
    uptime_score * 0.25 +
    performance_score * 0.20 +
    engagement_score * 0.25 +
    growth_score * 0.15 +
    integration_score * 0.15
)
```

### 3. Benchmarking
Compare instances against peers:
- **By Vertical**: Agency vs Studio vs In-house
- **By Size**: Solo, Small, Medium, Large, Enterprise
- **By Region**: GCC, MENA, Europe, Americas, APAC
- **By Age**: Time since onboarding
- **Percentiles**: Top 10%, median, bottom 25%

### 4. Anomaly Detection
Identify unusual patterns:
- **Usage Drops**: Sudden decrease in activity
- **Error Spikes**: Increased error rates
- **User Churn Signals**: Users going inactive
- **Security Anomalies**: Unusual access patterns
- **Cost Anomalies**: Unexpected resource usage

### 5. Forecasting
Predict future needs:
- **User Growth**: Expected user count
- **Storage Needs**: Data growth projection
- **API Limits**: When limits will be hit
- **Cost Forecast**: Infrastructure spend
- **Capacity Planning**: Resource requirements

### 6. Adoption Analytics
Track feature and module adoption:
- **Activation Funnel**: Onboarding completion rates
- **Time-to-Value**: How fast instances see ROI
- **Feature Discovery**: Which features are found organically
- **Stickiness**: Features that drive retention
- **Module Depth**: How deeply modules are used

### 7. ROI Calculation
Measure value delivered:
- **Time Saved**: Automation efficiency
- **Cost Reduction**: Manual work eliminated
- **Revenue Impact**: Business value generated
- **Productivity Gains**: Output per user

## Analysis Approach
1. Start with the specific question or metric requested
2. Gather relevant data across the time period
3. Compare against benchmarks when applicable
4. Identify trends and patterns
5. Surface actionable insights
6. Provide recommendations when appropriate

Be data-driven, precise, and focus on actionable insights."""

    def _define_tools(self) -> list[dict]:
        return [
            # Usage Metrics
            {
                "name": "get_usage_metrics",
                "description": "Get comprehensive usage metrics for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d", "90d", "1y"],
                            "description": "Time period for metrics",
                        },
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["api_calls", "active_users", "sessions", "page_views", "all"],
                            },
                            "description": "Specific metrics to retrieve",
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["hourly", "daily", "weekly", "monthly"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_active_users",
                "description": "Get active user counts (DAU, WAU, MAU).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string", "enum": ["7d", "30d", "90d"]},
                        "include_breakdown": {
                            "type": "boolean",
                            "description": "Include breakdown by role/department",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_session_analytics",
                "description": "Analyze user session patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics: avg_duration, depth, bounce_rate, peak_hours",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_api_usage",
                "description": "Get API usage statistics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "group_by": {
                            "type": "string",
                            "enum": ["endpoint", "user", "hour", "day"],
                        },
                        "include_errors": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Health Scoring
            {
                "name": "calculate_health_score",
                "description": "Calculate composite health score for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "include_breakdown": {
                            "type": "boolean",
                            "description": "Include component scores",
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include score history",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_performance_metrics",
                "description": "Get performance metrics (response times, error rates).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "percentiles": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Response time percentiles (e.g., [50, 95, 99])",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_uptime_stats",
                "description": "Get uptime and availability statistics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "include_incidents": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Benchmarking
            {
                "name": "benchmark_instance",
                "description": "Compare instance against peer group.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "compare_by": {
                            "type": "string",
                            "enum": ["vertical", "size", "region", "age", "all"],
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to compare: engagement, growth, health, adoption",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_percentile_ranking",
                "description": "Get percentile ranking for specific metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "metric": {
                            "type": "string",
                            "enum": ["health_score", "engagement", "growth", "adoption", "api_usage"],
                        },
                        "peer_group": {
                            "type": "string",
                            "enum": ["all", "same_vertical", "same_size", "same_region"],
                        },
                    },
                    "required": ["instance_id", "metric"],
                },
            },
            {
                "name": "get_best_in_class",
                "description": "Identify best performing instances for learning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string"},
                        "vertical": {"type": "string"},
                        "size": {"type": "string"},
                        "top_n": {"type": "integer", "default": 10},
                    },
                    "required": ["metric"],
                },
            },
            # Anomaly Detection
            {
                "name": "detect_anomalies",
                "description": "Detect anomalies in instance behavior.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "anomaly_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["usage_drop", "error_spike", "user_churn", "security", "cost"],
                            },
                        },
                        "sensitivity": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                        "period": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_alerts",
                "description": "Get active alerts for an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "warning", "info", "all"],
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "acknowledged", "resolved", "all"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "analyze_user_churn_signals",
                "description": "Identify users showing churn signals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "lookback_days": {"type": "integer", "default": 30},
                        "threshold": {
                            "type": "string",
                            "enum": ["aggressive", "moderate", "conservative"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            # Forecasting
            {
                "name": "forecast_growth",
                "description": "Forecast user and data growth.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "forecast_period": {
                            "type": "string",
                            "enum": ["30d", "90d", "6m", "1y"],
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to forecast: users, storage, api_calls",
                        },
                        "confidence_interval": {"type": "number", "default": 0.95},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "forecast_costs",
                "description": "Forecast infrastructure costs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "forecast_period": {"type": "string"},
                        "include_breakdown": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "predict_limit_breach",
                "description": "Predict when limits will be reached.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "limit_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Limits: users, storage, api_calls, seats",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            # Feature Adoption
            {
                "name": "analyze_feature_adoption",
                "description": "Analyze feature and module adoption.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific features or 'all'",
                        },
                        "include_funnel": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_module_utilization",
                "description": "Get utilization rates for each module.",
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
                "name": "track_activation_funnel",
                "description": "Track onboarding activation funnel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "funnel_steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom funnel steps or use default",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "calculate_time_to_value",
                "description": "Calculate time to first value.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "value_events": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Events that indicate value: first_project, first_client, etc.",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "identify_power_users",
                "description": "Identify power users within an instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Criteria: sessions, features_used, content_created",
                        },
                        "top_n": {"type": "integer", "default": 10},
                    },
                    "required": ["instance_id"],
                },
            },
            # ROI & Value
            {
                "name": "calculate_roi",
                "description": "Calculate ROI and value metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "value_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics: time_saved, automation_rate, productivity",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_productivity_gains",
                "description": "Calculate productivity improvements.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "baseline_comparison": {"type": "boolean"},
                    },
                    "required": ["instance_id"],
                },
            },
            # Reporting
            {
                "name": "generate_executive_report",
                "description": "Generate executive summary report.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period": {"type": "string"},
                        "sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sections: usage, health, growth, adoption, roi",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["summary", "detailed", "slides"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "compare_periods",
                "description": "Compare metrics across time periods.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "period_1": {"type": "string"},
                        "period_2": {"type": "string"},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["instance_id", "period_1", "period_2"],
                },
            },
            {
                "name": "get_cohort_analysis",
                "description": "Analyze cohorts over time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cohort_by": {
                            "type": "string",
                            "enum": ["onboarding_month", "vertical", "size", "region"],
                        },
                        "metric": {"type": "string"},
                        "periods": {"type": "integer", "description": "Number of periods"},
                    },
                    "required": ["cohort_by", "metric"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute analytics tool against platform API."""
        try:
            # Usage Metrics
            if tool_name == "get_usage_metrics":
                return await self._get_usage_metrics(tool_input)
            elif tool_name == "get_active_users":
                return await self._get_active_users(tool_input)
            elif tool_name == "get_session_analytics":
                return await self._get_session_analytics(tool_input)
            elif tool_name == "get_api_usage":
                return await self._get_api_usage(tool_input)

            # Health Scoring
            elif tool_name == "calculate_health_score":
                return await self._calculate_health_score(tool_input)
            elif tool_name == "get_performance_metrics":
                return await self._get_performance_metrics(tool_input)
            elif tool_name == "get_uptime_stats":
                return await self._get_uptime_stats(tool_input)

            # Benchmarking
            elif tool_name == "benchmark_instance":
                return await self._benchmark_instance(tool_input)
            elif tool_name == "get_percentile_ranking":
                return await self._get_percentile_ranking(tool_input)
            elif tool_name == "get_best_in_class":
                return await self._get_best_in_class(tool_input)

            # Anomaly Detection
            elif tool_name == "detect_anomalies":
                return await self._detect_anomalies(tool_input)
            elif tool_name == "get_alerts":
                return await self._get_alerts(tool_input)
            elif tool_name == "analyze_user_churn_signals":
                return await self._analyze_user_churn_signals(tool_input)

            # Forecasting
            elif tool_name == "forecast_growth":
                return await self._forecast_growth(tool_input)
            elif tool_name == "forecast_costs":
                return await self._forecast_costs(tool_input)
            elif tool_name == "predict_limit_breach":
                return await self._predict_limit_breach(tool_input)

            # Feature Adoption
            elif tool_name == "analyze_feature_adoption":
                return await self._analyze_feature_adoption(tool_input)
            elif tool_name == "get_module_utilization":
                return await self._get_module_utilization(tool_input)
            elif tool_name == "track_activation_funnel":
                return await self._track_activation_funnel(tool_input)
            elif tool_name == "calculate_time_to_value":
                return await self._calculate_time_to_value(tool_input)
            elif tool_name == "identify_power_users":
                return await self._identify_power_users(tool_input)

            # ROI & Value
            elif tool_name == "calculate_roi":
                return await self._calculate_roi(tool_input)
            elif tool_name == "get_productivity_gains":
                return await self._get_productivity_gains(tool_input)

            # Reporting
            elif tool_name == "generate_executive_report":
                return await self._generate_executive_report(tool_input)
            elif tool_name == "compare_periods":
                return await self._compare_periods(tool_input)
            elif tool_name == "get_cohort_analysis":
                return await self._get_cohort_analysis(tool_input)

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    # Usage Metrics Methods

    async def _get_usage_metrics(self, params: dict) -> dict:
        """Get comprehensive usage metrics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/usage",
            params={
                "period": params.get("period", "30d"),
                "metrics": ",".join(params.get("metrics", ["all"])),
                "granularity": params.get("granularity", "daily"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "period": params.get("period", "30d"),
            "metrics": {
                "api_calls": {"total": 0, "trend": []},
                "active_users": {"dau": 0, "wau": 0, "mau": 0},
                "sessions": {"total": 0, "avg_duration": 0},
                "page_views": {"total": 0},
            },
            "instruction": "Aggregate usage metrics from instance telemetry.",
        }

    async def _get_active_users(self, params: dict) -> dict:
        """Get active user counts."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/active-users",
            params={"period": params.get("period", "30d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "dau": 0,
            "wau": 0,
            "mau": 0,
            "dau_mau_ratio": 0,
            "trend": "stable",
            "instruction": "Calculate DAU, WAU, MAU from session data.",
        }

    async def _get_session_analytics(self, params: dict) -> dict:
        """Analyze session patterns."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/sessions",
            params={"period": params.get("period", "30d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "avg_duration_minutes": 0,
            "avg_depth": 0,
            "bounce_rate": 0,
            "peak_hours": [],
            "instruction": "Analyze session duration, depth, and patterns.",
        }

    async def _get_api_usage(self, params: dict) -> dict:
        """Get API usage statistics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/api-usage",
            params={
                "period": params.get("period", "30d"),
                "group_by": params.get("group_by", "endpoint"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "total_calls": 0,
            "by_endpoint": {},
            "error_rate": 0,
            "instruction": "Aggregate API call metrics.",
        }

    # Health Scoring Methods

    async def _calculate_health_score(self, params: dict) -> dict:
        """Calculate composite health score."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/health-score"
        )
        if response.status_code == 200:
            return response.json()

        # Calculate health score components
        return {
            "instance_id": params["instance_id"],
            "health_score": 0,
            "grade": "N/A",
            "components": {
                "uptime": {"score": 0, "weight": 0.25},
                "performance": {"score": 0, "weight": 0.20},
                "engagement": {"score": 0, "weight": 0.25},
                "growth": {"score": 0, "weight": 0.15},
                "integration": {"score": 0, "weight": 0.15},
            },
            "trend": "stable",
            "instruction": "Calculate weighted health score from components.",
        }

    async def _get_performance_metrics(self, params: dict) -> dict:
        """Get performance metrics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/performance",
            params={"period": params.get("period", "30d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "response_times": {
                "p50": 0,
                "p95": 0,
                "p99": 0,
            },
            "error_rate": 0,
            "throughput": 0,
            "instruction": "Collect response time percentiles and error rates.",
        }

    async def _get_uptime_stats(self, params: dict) -> dict:
        """Get uptime statistics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/uptime",
            params={"period": params.get("period", "30d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "uptime_percent": 99.9,
            "incidents": [],
            "mttr_minutes": 0,
            "instruction": "Track availability and incident data.",
        }

    # Benchmarking Methods

    async def _benchmark_instance(self, params: dict) -> dict:
        """Compare instance against peers."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/benchmark",
            params={"compare_by": params.get("compare_by", "all")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "peer_group": params.get("compare_by", "all"),
            "comparisons": {
                "engagement": {"instance": 0, "peer_avg": 0, "percentile": 0},
                "growth": {"instance": 0, "peer_avg": 0, "percentile": 0},
                "health": {"instance": 0, "peer_avg": 0, "percentile": 0},
            },
            "instruction": "Compare metrics against peer group averages.",
        }

    async def _get_percentile_ranking(self, params: dict) -> dict:
        """Get percentile ranking for metric."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/percentile",
            params={
                "metric": params["metric"],
                "peer_group": params.get("peer_group", "all"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "metric": params["metric"],
            "percentile": 0,
            "value": 0,
            "peer_group_size": 0,
            "instruction": "Calculate percentile rank within peer group.",
        }

    async def _get_best_in_class(self, params: dict) -> dict:
        """Get best performing instances."""
        response = await self.http_client.get(
            f"/api/v1/analytics/best-in-class",
            params={
                "metric": params["metric"],
                "vertical": params.get("vertical"),
                "size": params.get("size"),
                "top_n": params.get("top_n", 10),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "metric": params["metric"],
            "top_instances": [],
            "instruction": "Identify top performers for learning insights.",
        }

    # Anomaly Detection Methods

    async def _detect_anomalies(self, params: dict) -> dict:
        """Detect anomalies in instance behavior."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/anomalies",
            params={
                "types": ",".join(params.get("anomaly_types", ["all"])),
                "sensitivity": params.get("sensitivity", "medium"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "anomalies": [],
            "anomaly_count": 0,
            "instruction": "Run anomaly detection algorithms on metrics.",
        }

    async def _get_alerts(self, params: dict) -> dict:
        """Get active alerts."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/alerts",
            params={
                "severity": params.get("severity", "all"),
                "status": params.get("status", "active"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "alerts": [],
            "instruction": "Retrieve alert queue for instance.",
        }

    async def _analyze_user_churn_signals(self, params: dict) -> dict:
        """Identify users with churn signals."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/churn-signals",
            params={
                "lookback_days": params.get("lookback_days", 30),
                "threshold": params.get("threshold", "moderate"),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "at_risk_users": [],
            "churn_risk_score": 0,
            "instruction": "Identify users showing declining engagement.",
        }

    # Forecasting Methods

    async def _forecast_growth(self, params: dict) -> dict:
        """Forecast growth metrics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/forecast/growth",
            params={
                "period": params.get("forecast_period", "90d"),
                "metrics": ",".join(params.get("metrics", ["users", "storage"])),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "forecast_period": params.get("forecast_period", "90d"),
            "forecasts": {
                "users": {"current": 0, "forecast": 0, "growth_rate": 0},
                "storage_gb": {"current": 0, "forecast": 0, "growth_rate": 0},
            },
            "confidence_interval": params.get("confidence_interval", 0.95),
            "instruction": "Use time series forecasting on historical data.",
        }

    async def _forecast_costs(self, params: dict) -> dict:
        """Forecast infrastructure costs."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/forecast/costs",
            params={"period": params.get("forecast_period", "90d")},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "current_monthly_cost": 0,
            "forecast_monthly_cost": 0,
            "breakdown": {
                "compute": 0,
                "storage": 0,
                "bandwidth": 0,
                "api": 0,
            },
            "instruction": "Project costs based on usage growth.",
        }

    async def _predict_limit_breach(self, params: dict) -> dict:
        """Predict when limits will be reached."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/limits/forecast"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "limits": {
                "users": {"current": 0, "limit": 0, "breach_date": None},
                "storage": {"current": 0, "limit": 0, "breach_date": None},
                "api_calls": {"current": 0, "limit": 0, "breach_date": None},
            },
            "instruction": "Extrapolate current growth to predict limit breaches.",
        }

    # Feature Adoption Methods

    async def _analyze_feature_adoption(self, params: dict) -> dict:
        """Analyze feature adoption."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/adoption",
            params={"features": ",".join(params.get("features", ["all"]))},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "adoption_rates": {},
            "funnel": [] if params.get("include_funnel") else None,
            "instruction": "Track feature discovery and usage rates.",
        }

    async def _get_module_utilization(self, params: dict) -> dict:
        """Get module utilization rates."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/modules/utilization"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "modules": {},
            "underutilized": [],
            "recommendations": [] if params.get("include_recommendations") else None,
            "instruction": "Calculate usage depth per module.",
        }

    async def _track_activation_funnel(self, params: dict) -> dict:
        """Track activation funnel."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/activation-funnel"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "funnel_steps": [
                {"step": "signup", "completed": True, "conversion": 100},
                {"step": "first_login", "completed": False, "conversion": 0},
                {"step": "first_project", "completed": False, "conversion": 0},
                {"step": "first_client", "completed": False, "conversion": 0},
            ],
            "instruction": "Track onboarding milestone completion.",
        }

    async def _calculate_time_to_value(self, params: dict) -> dict:
        """Calculate time to first value."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/time-to-value"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "value_events": {
                "first_project": {"achieved": False, "days": None},
                "first_client": {"achieved": False, "days": None},
                "first_content": {"achieved": False, "days": None},
            },
            "overall_ttv_days": None,
            "instruction": "Calculate days from signup to value events.",
        }

    async def _identify_power_users(self, params: dict) -> dict:
        """Identify power users."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/power-users",
            params={"top_n": params.get("top_n", 10)},
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "power_users": [],
            "criteria_used": params.get("criteria", ["sessions", "features_used"]),
            "instruction": "Rank users by engagement metrics.",
        }

    # ROI Methods

    async def _calculate_roi(self, params: dict) -> dict:
        """Calculate ROI metrics."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/roi"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "time_saved_hours": 0,
            "automation_rate": 0,
            "estimated_value": 0,
            "instruction": "Calculate value from automation and efficiency gains.",
        }

    async def _get_productivity_gains(self, params: dict) -> dict:
        """Calculate productivity improvements."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/productivity"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "productivity_index": 0,
            "output_per_user": 0,
            "efficiency_gains": {},
            "instruction": "Measure output metrics per user over time.",
        }

    # Reporting Methods

    async def _generate_executive_report(self, params: dict) -> dict:
        """Generate executive summary."""
        response = await self.http_client.post(
            f"/api/v1/analytics/instances/{params['instance_id']}/reports/executive",
            json={
                "period": params.get("period", "30d"),
                "sections": params.get("sections", ["usage", "health", "growth"]),
                "format": params.get("format", "summary"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "report_type": "executive",
            "sections": params.get("sections", ["usage", "health", "growth"]),
            "instruction": "Compile metrics into executive summary format.",
        }

    async def _compare_periods(self, params: dict) -> dict:
        """Compare metrics across periods."""
        response = await self.http_client.get(
            f"/api/v1/analytics/instances/{params['instance_id']}/compare",
            params={
                "period_1": params["period_1"],
                "period_2": params["period_2"],
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "period_1": params["period_1"],
            "period_2": params["period_2"],
            "comparisons": {},
            "instruction": "Compare metrics between two time periods.",
        }

    async def _get_cohort_analysis(self, params: dict) -> dict:
        """Analyze cohorts over time."""
        response = await self.http_client.get(
            f"/api/v1/analytics/cohorts",
            params={
                "cohort_by": params["cohort_by"],
                "metric": params["metric"],
                "periods": params.get("periods", 12),
            },
        )
        if response.status_code == 200:
            return response.json()
        return {
            "cohort_by": params["cohort_by"],
            "metric": params["metric"],
            "cohorts": [],
            "instruction": "Group instances by cohort and track metric over time.",
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
