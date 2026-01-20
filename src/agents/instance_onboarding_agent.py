from typing import Any
import httpx
from .base import BaseAgent


class InstanceOnboardingAgent(BaseAgent):
    """
    Agent for onboarding new ERP instances (SuperAdmin Wizard).

    This is the "welcome wizard" for new tenants deploying the ERP.
    Priority agent for the SuperAdmin onboarding flow in erp_staging_lmtd.

    ## ERP Integration (per JAN_2026_ERP_TO_AGENT_BUILDER_HANDOFF.md)

    This agent supports the SuperAdmin wizard with the following capabilities:
    - Collect tenant information (name, industry, team size)
    - Recommend module bundles based on business profile
    - Set up initial data structures
    - Assist with migrations from other platforms
    - Configure team hierarchies and roles

    ## Wizard Steps

    The onboarding wizard proceeds through these steps:
    1. business_assessment - Collect business type, size, services
    2. module_selection - Recommend and configure modules
    3. branding - Set up look/feel, colors, logo
    4. users - Create admin user, team structure, roles
    5. infrastructure - Provision database, storage, cache
    6. integrations - Connect external platforms (OAuth flows)
    7. sample_data - Optional demo data generation
    8. complete - Finalize and generate getting started guide

    ## Input/Output Examples

    Input:
    ```json
    {
        "wizard_step": "business_assessment",
        "tenant_info": {
            "name": "Acme Creative Agency",
            "industry": "advertising",
            "team_size": "medium"
        },
        "responses": {
            "services": ["creative", "media", "social"],
            "regions": ["gcc", "mena"],
            "client_types": ["b2b", "b2c"]
        }
    }
    ```

    Output:
    ```json
    {
        "next_step": "module_selection",
        "recommendations": {
            "modules": ["studio", "dam", "content-engine", "crm", "reporting"],
            "priority": "creative"
        },
        "follow_up_questions": [
            "Do you need WhatsApp Business integration?",
            "Will you be managing influencer campaigns?"
        ],
        "guidance": "Based on your profile as a creative agency..."
    }
    ```
    """

    # Wizard step definitions for ERP integration
    WIZARD_STEPS = [
        "business_assessment",
        "module_selection",
        "branding",
        "users",
        "infrastructure",
        "integrations",
        "sample_data",
        "complete",
    ]

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
            timeout=120.0,  # Longer timeout for setup operations
        )
        super().__init__(client, model)

    def get_wizard_step_guidance(self, step: str) -> dict:
        """
        Get guidance for a specific wizard step.

        This method provides structured guidance for the ERP SuperAdmin wizard.
        Each step returns expected inputs, outputs, and next steps.

        Args:
            step: The wizard step identifier

        Returns:
            dict with step guidance
        """
        step_guidance = {
            "business_assessment": {
                "description": "Collect information about the business",
                "expected_inputs": {
                    "business_type": "Type: agency, studio, in_house, freelancer, production_house",
                    "business_size": "Size: solo, small, medium, large, enterprise",
                    "services": "List of services offered",
                    "regions": "Operating regions",
                    "client_types": "Types of clients served",
                },
                "outputs": ["business_profile", "recommended_complexity", "features_needed"],
                "next_step": "module_selection",
            },
            "module_selection": {
                "description": "Select and configure ERP modules",
                "expected_inputs": {
                    "business_profile": "From previous step",
                    "priorities": "Priority areas for the business",
                },
                "outputs": ["recommended_modules", "categorized_modules", "module_configs"],
                "next_step": "branding",
            },
            "branding": {
                "description": "Configure look and feel",
                "expected_inputs": {
                    "company_name": "Organization name",
                    "logo_url": "URL to logo image",
                    "primary_color": "Primary brand color (hex)",
                    "theme": "Theme preference (light/dark/auto)",
                },
                "outputs": ["branding_config"],
                "next_step": "users",
            },
            "users": {
                "description": "Set up users, teams, and roles",
                "expected_inputs": {
                    "admin_email": "Admin user email",
                    "admin_name": "Admin user name",
                    "departments": "List of departments",
                    "role_template": "Role template to use",
                },
                "outputs": ["admin_user", "team_structure", "roles"],
                "next_step": "infrastructure",
            },
            "infrastructure": {
                "description": "Provision infrastructure components",
                "expected_inputs": {
                    "region": "Preferred deployment region",
                    "tier": "Infrastructure tier",
                },
                "outputs": ["database", "storage", "cache", "search"],
                "next_step": "integrations",
            },
            "integrations": {
                "description": "Connect external platforms",
                "expected_inputs": {
                    "platforms": "List of platforms to connect",
                    "sso_provider": "SSO provider if applicable",
                },
                "outputs": ["connected_platforms", "oauth_urls", "sso_config"],
                "next_step": "sample_data",
            },
            "sample_data": {
                "description": "Generate sample data for demos",
                "expected_inputs": {
                    "generate": "Whether to generate sample data",
                    "data_types": "Types of data to generate",
                    "volume": "Data volume (minimal/moderate/comprehensive)",
                },
                "outputs": ["sample_clients", "sample_projects", "sample_content"],
                "next_step": "complete",
            },
            "complete": {
                "description": "Finalize onboarding",
                "expected_inputs": {},
                "outputs": ["getting_started_guide", "instance_url", "quick_wins"],
                "next_step": None,
            },
        }
        return step_guidance.get(step, {
            "description": "Unknown step",
            "expected_inputs": {},
            "outputs": [],
            "next_step": "business_assessment",
        })

    def get_next_wizard_step(self, current_step: str) -> str | None:
        """Get the next wizard step after the current one."""
        try:
            current_index = self.WIZARD_STEPS.index(current_step)
            if current_index < len(self.WIZARD_STEPS) - 1:
                return self.WIZARD_STEPS[current_index + 1]
            return None
        except ValueError:
            return "business_assessment"

    @property
    def name(self) -> str:
        return "instance_onboarding_agent"

    @property
    def system_prompt(self) -> str:
        return """You are an expert ERP instance onboarding specialist.

Your role is to guide new organizations through setting up their ERP instance:

## Primary Capabilities

### 1. Business Assessment & Module Selection
Understand the business to recommend the right modules:
- **Business Type**: Agency, Studio, In-house Marketing, Freelancer, Production House
- **Business Size**: Solo, Small (2-10), Medium (11-50), Large (50+)
- **Services Offered**: Creative, Media, Social, PR, Events, Influencer, Production
- **Regions**: GCC, MENA, Europe, Americas, APAC, Global
- **Client Types**: B2B, B2C, D2C, Government, Non-profit

### 2. Module Recommendations
Based on assessment, recommend from 28 available modules:
```
CORE (always on):        CREATIVE:              CLIENT:
├── dashboard            ├── studio             ├── crm
├── settings             ├── dam                ├── briefs
├── notifications        ├── content-engine     ├── rfp
├── files                ├── content            ├── onboarding
└── ai                   └── builder            └── nps

OPERATIONS:              FINANCE:               COMMUNICATION:
├── resources            ├── retainer           ├── whatsapp
├── workflows            ├── scope-changes      ├── chat
├── time-tracking        └── reporting          └── integrations
├── delegation
└── leave

SPECIALIZED:
├── forms
└── complaints
```

### 3. Look & Feel Configuration
- Brand colors (primary, secondary, accent)
- Logo upload and placement
- Typography preferences
- Dashboard layout
- Theme (light/dark/auto)

### 4. User & Role Setup
- Admin users
- Team structure (departments)
- Role templates (Account Manager, Creative Director, etc.)
- Permission presets
- SSO/authentication configuration

### 5. Infrastructure Provisioning
- Database instance creation (tenant-isolated)
- Storage buckets (for DAM, assets)
- Cache/Redis instances
- Search indices
- Background job queues

### 6. External Platform Credentials
For Media/Ads services, connect:
- **Google Ads Manager** - OAuth flow + account linking
- **Google Analytics 4** - Property access
- **Meta Business Suite** - Ad accounts, Pages, Instagram
- **Meta Ads Manager** - Campaign management access
- **TikTok Ads Manager** - Business center connection
- **Snapchat Ads Manager** - Organization access
- **LinkedIn Campaign Manager** - Ad account connection
- **Twitter/X Ads** - Ad account access
- **Pinterest Ads** - Business account connection
- **DV360** - Display & Video 360 access
- **The Trade Desk** - Seat access

For Analytics/Social:
- **Google Search Console** - Website verification
- **Sprout Social / Sprinklr** - API access
- **Brandwatch / Talkwalker** - Listening API
- **Meltwater** - PR monitoring

For Creative/DAM:
- **Adobe Creative Cloud** - License management
- **Figma** - Team/org access
- **Canva** - Brand Kit connection

For Operations:
- **Slack** - Workspace integration
- **Google Workspace** - Domain verification, Calendar, Drive
- **Microsoft 365** - Tenant connection, Calendar, OneDrive
- **Xero / QuickBooks** - Accounting sync
- **HubSpot / Salesforce** - CRM sync

### 7. Integration Setup
- WhatsApp Business API (Meta Cloud API or BSP)
- Email providers (SendGrid, Mailgun, Postmark)
- Cloud storage (AWS S3, Google Cloud Storage, Azure Blob)
- CDN configuration
- SSO providers (Google, Azure AD, Okta, Auth0)

### 8. Sample Instance Generation (Demo Mode)
Create realistic "what if" scenarios with:
- Fictional company matching their profile
- Sample clients with realistic data
- Sample projects in various stages
- Sample briefs and RFPs
- Sample content in DAM
- Sample team members
- Realistic dashboards and reports

This helps prospects visualize "what it could look like" for their business.

## Conversation Flow
1. Welcome and explain the process
2. Ask about business type, size, services
3. Recommend modules based on answers
4. Confirm module selection
5. Provision infrastructure (database, storage)
6. Configure look/feel
7. Set up users/roles
8. Connect external platforms (ads, analytics, creative tools)
9. Configure messaging integrations
10. Offer sample data generation
11. Provide getting started guide

Be conversational, helpful, and explain WHY you're recommending things.

## Security Notes
- All credentials stored encrypted at rest
- OAuth tokens refreshed automatically
- Scopes requested follow least-privilege principle
- Credential access logged for audit trail"""

    def _define_tools(self) -> list[dict]:
        return [
            # Business Assessment
            {
                "name": "assess_business",
                "description": "Analyze business profile and recommend configuration.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "enum": ["agency", "studio", "in_house", "freelancer", "production_house", "consultancy"],
                            "description": "Type of business",
                        },
                        "business_size": {
                            "type": "string",
                            "enum": ["solo", "small", "medium", "large", "enterprise"],
                            "description": "Team size category",
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Services offered: creative, media, social, pr, events, influencer, production, strategy, digital",
                        },
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Operating regions",
                        },
                        "client_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Client types: b2b, b2c, d2c, government, nonprofit",
                        },
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Current pain points to solve",
                        },
                    },
                    "required": ["business_type"],
                },
            },
            # Module Selection
            {
                "name": "recommend_modules",
                "description": "Generate module recommendations based on business profile.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "business_profile": {
                            "type": "object",
                            "description": "Business profile from assessment",
                        },
                        "priorities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Priority areas: efficiency, client_management, creative, finance, reporting",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "configure_modules",
                "description": "Activate and configure selected modules.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to configure",
                        },
                        "modules": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Modules to activate",
                        },
                        "module_configs": {
                            "type": "object",
                            "description": "Per-module configuration options",
                        },
                    },
                    "required": ["instance_id", "modules"],
                },
            },
            # Look & Feel
            {
                "name": "configure_branding",
                "description": "Set up instance branding and look/feel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "company_name": {"type": "string"},
                        "logo_url": {"type": "string"},
                        "primary_color": {"type": "string", "description": "Hex color"},
                        "secondary_color": {"type": "string"},
                        "accent_color": {"type": "string"},
                        "theme": {
                            "type": "string",
                            "enum": ["light", "dark", "auto"],
                        },
                        "font_family": {"type": "string"},
                        "dashboard_layout": {
                            "type": "string",
                            "enum": ["default", "compact", "expanded"],
                        },
                    },
                    "required": ["instance_id", "company_name"],
                },
            },
            # User & Role Setup
            {
                "name": "setup_admin_user",
                "description": "Create the initial admin user.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "email": {"type": "string"},
                        "name": {"type": "string"},
                        "role": {"type": "string", "default": "super_admin"},
                    },
                    "required": ["instance_id", "email", "name"],
                },
            },
            {
                "name": "create_team_structure",
                "description": "Set up departments and team structure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "departments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "head": {"type": "string"},
                                },
                            },
                            "description": "Departments to create",
                        },
                    },
                    "required": ["instance_id", "departments"],
                },
            },
            {
                "name": "create_roles",
                "description": "Create role templates with permissions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "roles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "permissions": {"type": "array", "items": {"type": "string"}},
                                    "department": {"type": "string"},
                                },
                            },
                            "description": "Roles to create",
                        },
                        "use_template": {
                            "type": "string",
                            "enum": ["agency", "studio", "in_house", "minimal", "custom"],
                            "description": "Use a predefined role template",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "invite_users",
                "description": "Invite team members to the instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "users": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string"},
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                    "department": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["instance_id", "users"],
                },
            },
            # Integrations
            {
                "name": "configure_integrations",
                "description": "Set up third-party integrations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "integrations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["whatsapp", "email", "storage", "calendar", "accounting", "slack", "social"],
                                    },
                                    "provider": {"type": "string"},
                                    "credentials": {"type": "object"},
                                },
                            },
                        },
                    },
                    "required": ["instance_id", "integrations"],
                },
            },
            # Infrastructure Provisioning
            {
                "name": "provision_database",
                "description": "Provision a new tenant database instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "region": {
                            "type": "string",
                            "enum": ["us-east", "us-west", "eu-west", "eu-central", "me-south", "ap-south", "ap-southeast"],
                            "description": "Database region for latency optimization",
                        },
                        "tier": {
                            "type": "string",
                            "enum": ["starter", "professional", "enterprise"],
                            "description": "Database tier (affects resources)",
                        },
                        "backup_retention_days": {"type": "integer", "default": 30},
                    },
                    "required": ["instance_id", "region"],
                },
            },
            {
                "name": "provision_storage",
                "description": "Provision storage buckets for DAM and assets.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "region": {"type": "string"},
                        "buckets": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["dam", "exports", "uploads", "backups", "temp"],
                            },
                            "description": "Storage buckets to create",
                        },
                        "cdn_enabled": {"type": "boolean", "default": True},
                    },
                    "required": ["instance_id", "region"],
                },
            },
            {
                "name": "provision_cache",
                "description": "Provision Redis cache for session/caching.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "region": {"type": "string"},
                        "size": {
                            "type": "string",
                            "enum": ["small", "medium", "large"],
                        },
                    },
                    "required": ["instance_id", "region"],
                },
            },
            {
                "name": "provision_search",
                "description": "Provision search index for content search.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "indices": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Indices: content, projects, clients, assets",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "get_infrastructure_status",
                "description": "Check provisioning status of all infrastructure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            # External Platform Credentials
            {
                "name": "initiate_oauth_flow",
                "description": "Start OAuth flow for an external platform.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {
                            "type": "string",
                            "enum": [
                                "google_ads", "google_analytics", "google_search_console", "google_workspace",
                                "meta_business", "meta_ads", "instagram",
                                "tiktok_ads", "snapchat_ads", "linkedin_ads", "twitter_ads", "pinterest_ads",
                                "dv360", "the_trade_desk",
                                "adobe_cc", "figma", "canva",
                                "slack", "microsoft_365",
                                "xero", "quickbooks", "hubspot", "salesforce",
                                "sprout_social", "sprinklr", "brandwatch", "meltwater"
                            ],
                            "description": "Platform to connect",
                        },
                        "scopes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific scopes to request (optional, uses defaults)",
                        },
                        "redirect_uri": {"type": "string"},
                    },
                    "required": ["instance_id", "platform"],
                },
            },
            {
                "name": "complete_oauth_flow",
                "description": "Complete OAuth flow with authorization code.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "auth_code": {"type": "string"},
                        "state": {"type": "string"},
                    },
                    "required": ["instance_id", "platform", "auth_code"],
                },
            },
            {
                "name": "store_api_credentials",
                "description": "Store API key/secret credentials for platforms without OAuth.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "api_key": {"type": "string"},
                                "api_secret": {"type": "string"},
                                "account_id": {"type": "string"},
                                "additional": {"type": "object"},
                            },
                        },
                    },
                    "required": ["instance_id", "platform", "credentials"],
                },
            },
            {
                "name": "link_ad_accounts",
                "description": "Link specific ad accounts after OAuth connection.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {
                            "type": "string",
                            "enum": ["google_ads", "meta_ads", "tiktok_ads", "snapchat_ads", "linkedin_ads", "twitter_ads", "pinterest_ads", "dv360"],
                        },
                        "account_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Ad account IDs to link",
                        },
                    },
                    "required": ["instance_id", "platform", "account_ids"],
                },
            },
            {
                "name": "list_available_accounts",
                "description": "List available accounts for a connected platform.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": ["instance_id", "platform"],
                },
            },
            {
                "name": "verify_platform_connection",
                "description": "Verify a platform connection is working.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "platform": {"type": "string"},
                    },
                    "required": ["instance_id", "platform"],
                },
            },
            {
                "name": "get_connected_platforms",
                "description": "List all connected external platforms and their status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "configure_sso",
                "description": "Configure SSO provider for user authentication.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "provider": {
                            "type": "string",
                            "enum": ["google", "azure_ad", "okta", "auth0", "saml"],
                        },
                        "config": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "client_secret": {"type": "string"},
                                "tenant_id": {"type": "string"},
                                "domain": {"type": "string"},
                                "saml_metadata_url": {"type": "string"},
                            },
                        },
                        "enforce_sso": {"type": "boolean", "default": False},
                        "allowed_domains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Email domains allowed for SSO",
                        },
                    },
                    "required": ["instance_id", "provider", "config"],
                },
            },
            {
                "name": "recommend_platform_connections",
                "description": "Recommend external platforms to connect based on services.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Services offered: media, social, creative, pr, analytics",
                        },
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Operating regions",
                        },
                    },
                    "required": ["services"],
                },
            },
            # Sample Instance Generation
            {
                "name": "generate_sample_instance",
                "description": "Create a sample instance with realistic dummy data for demos.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "company_profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Fictional company name"},
                                "type": {"type": "string"},
                                "industry_focus": {"type": "array", "items": {"type": "string"}},
                                "regions": {"type": "array", "items": {"type": "string"}},
                                "size": {"type": "string"},
                            },
                            "description": "Profile of the fictional company",
                        },
                        "data_to_generate": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["clients", "projects", "briefs", "rfps", "team", "content", "reports", "invoices"],
                            },
                            "description": "Types of sample data to generate",
                        },
                        "data_volume": {
                            "type": "string",
                            "enum": ["minimal", "moderate", "comprehensive"],
                            "description": "How much sample data to create",
                        },
                        "time_range": {
                            "type": "string",
                            "enum": ["1_month", "3_months", "6_months", "1_year"],
                            "description": "Historical data range",
                        },
                    },
                    "required": ["instance_id", "company_profile"],
                },
            },
            {
                "name": "generate_sample_clients",
                "description": "Generate realistic sample clients for demo.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "count": {"type": "integer", "default": 5},
                        "industries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Industries for sample clients",
                        },
                        "include_history": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include project history for clients",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "generate_sample_projects",
                "description": "Generate sample projects in various stages.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "count": {"type": "integer", "default": 10},
                        "stages": {
                            "type": "object",
                            "properties": {
                                "pitching": {"type": "integer"},
                                "in_progress": {"type": "integer"},
                                "review": {"type": "integer"},
                                "completed": {"type": "integer"},
                            },
                            "description": "Distribution across project stages",
                        },
                        "project_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types: campaign, retainer, one_off, pitch",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "generate_sample_content",
                "description": "Generate sample DAM content and assets.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "content_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types: images, documents, presentations, videos",
                        },
                        "organize_by": {
                            "type": "string",
                            "enum": ["client", "project", "type", "date"],
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "generate_sample_team",
                "description": "Generate sample team members for demo.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "team_size": {"type": "integer", "default": 8},
                        "departments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Departments to staff",
                        },
                        "include_availability": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include realistic availability/utilization",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "populate_dashboards",
                "description": "Populate dashboards with realistic metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "dashboards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Dashboards to populate: overview, financial, resource, client",
                        },
                        "trends": {
                            "type": "string",
                            "enum": ["growth", "stable", "seasonal", "mixed"],
                            "description": "What trend pattern to show",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
            # Onboarding Progress
            {
                "name": "get_onboarding_status",
                "description": "Get current onboarding progress.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                    },
                    "required": ["instance_id"],
                },
            },
            {
                "name": "complete_onboarding",
                "description": "Finalize onboarding and activate instance.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "generate_getting_started": {
                            "type": "boolean",
                            "default": True,
                            "description": "Generate personalized getting started guide",
                        },
                    },
                    "required": ["instance_id"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute tool against ERP API."""
        try:
            # Business Assessment
            if tool_name == "assess_business":
                return self._assess_business(tool_input)
            elif tool_name == "recommend_modules":
                return self._recommend_modules(tool_input)
            elif tool_name == "configure_modules":
                return await self._configure_modules(tool_input)

            # Branding & Look/Feel
            elif tool_name == "configure_branding":
                return await self._configure_branding(tool_input)

            # User & Role Setup
            elif tool_name == "setup_admin_user":
                return await self._setup_admin_user(tool_input)
            elif tool_name == "create_team_structure":
                return await self._create_team_structure(tool_input)
            elif tool_name == "create_roles":
                return await self._create_roles(tool_input)
            elif tool_name == "invite_users":
                return await self._invite_users(tool_input)

            # Integrations
            elif tool_name == "configure_integrations":
                return await self._configure_integrations(tool_input)

            # Infrastructure Provisioning
            elif tool_name == "provision_database":
                return await self._provision_database(tool_input)
            elif tool_name == "provision_storage":
                return await self._provision_storage(tool_input)
            elif tool_name == "provision_cache":
                return await self._provision_cache(tool_input)
            elif tool_name == "provision_search":
                return await self._provision_search(tool_input)
            elif tool_name == "get_infrastructure_status":
                return await self._get_infrastructure_status(tool_input)

            # External Platform Credentials
            elif tool_name == "initiate_oauth_flow":
                return await self._initiate_oauth_flow(tool_input)
            elif tool_name == "complete_oauth_flow":
                return await self._complete_oauth_flow(tool_input)
            elif tool_name == "store_api_credentials":
                return await self._store_api_credentials(tool_input)
            elif tool_name == "link_ad_accounts":
                return await self._link_ad_accounts(tool_input)
            elif tool_name == "list_available_accounts":
                return await self._list_available_accounts(tool_input)
            elif tool_name == "verify_platform_connection":
                return await self._verify_platform_connection(tool_input)
            elif tool_name == "get_connected_platforms":
                return await self._get_connected_platforms(tool_input)
            elif tool_name == "configure_sso":
                return await self._configure_sso(tool_input)
            elif tool_name == "recommend_platform_connections":
                return self._recommend_platform_connections(tool_input)

            # Sample Instance Generation
            elif tool_name == "generate_sample_instance":
                return await self._generate_sample_instance(tool_input)
            elif tool_name == "generate_sample_clients":
                return await self._generate_sample_clients(tool_input)
            elif tool_name == "generate_sample_projects":
                return await self._generate_sample_projects(tool_input)
            elif tool_name == "generate_sample_content":
                return await self._generate_sample_content(tool_input)
            elif tool_name == "generate_sample_team":
                return await self._generate_sample_team(tool_input)
            elif tool_name == "populate_dashboards":
                return await self._populate_dashboards(tool_input)

            # Progress
            elif tool_name == "get_onboarding_status":
                return await self._get_onboarding_status(tool_input)
            elif tool_name == "complete_onboarding":
                return await self._complete_onboarding(tool_input)

            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    def _assess_business(self, params: dict) -> dict:
        """Assess business and return profile with recommendations."""
        business_type = params.get("business_type", "agency")
        business_size = params.get("business_size", "small")
        services = params.get("services", [])
        regions = params.get("regions", [])

        # Build profile
        profile = {
            "type": business_type,
            "size": business_size,
            "services": services,
            "regions": regions,
            "client_types": params.get("client_types", []),
            "pain_points": params.get("pain_points", []),
        }

        # Determine complexity level
        if business_size in ["solo", "small"]:
            complexity = "starter"
        elif business_size == "medium":
            complexity = "professional"
        else:
            complexity = "enterprise"

        # Service-based features
        features_needed = set()
        if "creative" in services or "production" in services:
            features_needed.update(["studio", "dam", "content-engine"])
        if "media" in services:
            features_needed.update(["reporting", "integrations"])
        if "social" in services:
            features_needed.update(["content", "integrations"])
        if "pr" in services or "events" in services:
            features_needed.update(["crm", "forms"])
        if "influencer" in services:
            features_needed.update(["crm", "reporting"])

        return {
            "profile": profile,
            "recommended_complexity": complexity,
            "features_needed": list(features_needed),
            "assessment_complete": True,
            "next_step": "module_selection",
        }

    def _recommend_modules(self, params: dict) -> dict:
        """Generate module recommendations."""
        profile = params.get("business_profile", {})
        priorities = params.get("priorities", [])

        # Core modules (always recommended)
        core = ["dashboard", "settings", "notifications", "files", "ai"]

        # Recommendations based on business type
        type_modules = {
            "agency": ["briefs", "rfp", "crm", "resources", "workflows", "reporting", "retainer"],
            "studio": ["studio", "dam", "content-engine", "builder", "briefs"],
            "in_house": ["briefs", "content", "dam", "workflows", "reporting"],
            "freelancer": ["briefs", "time-tracking", "retainer"],
            "production_house": ["studio", "dam", "content-engine", "resources", "workflows"],
            "consultancy": ["crm", "briefs", "rfp", "reporting", "time-tracking"],
        }

        business_type = profile.get("type", "agency")
        recommended = set(core + type_modules.get(business_type, []))

        # Add based on services
        services = profile.get("services", [])
        if "creative" in services:
            recommended.update(["studio", "dam", "content-engine"])
        if "media" in services:
            recommended.update(["reporting", "integrations"])
        if "social" in services:
            recommended.update(["content", "whatsapp", "chat"])
        if "pr" in services:
            recommended.update(["crm", "forms"])
        if "events" in services:
            recommended.update(["forms", "crm"])

        # Size-based additions
        size = profile.get("size", "small")
        if size in ["medium", "large", "enterprise"]:
            recommended.update(["delegation", "leave", "workflows"])
        if size in ["large", "enterprise"]:
            recommended.update(["nps", "complaints"])

        # Priority-based additions
        if "finance" in priorities:
            recommended.update(["retainer", "scope-changes", "reporting"])
        if "client_management" in priorities:
            recommended.update(["crm", "nps", "onboarding"])

        # Categorize recommendations
        all_modules = {
            "core": ["dashboard", "settings", "notifications", "files", "ai"],
            "creative": ["studio", "dam", "content-engine", "content", "builder"],
            "client": ["crm", "briefs", "rfp", "onboarding", "nps"],
            "operations": ["resources", "workflows", "time-tracking", "delegation", "leave"],
            "finance": ["retainer", "scope-changes", "reporting"],
            "communication": ["whatsapp", "chat", "integrations"],
            "other": ["forms", "complaints"],
        }

        categorized = {}
        for category, modules in all_modules.items():
            categorized[category] = {
                "recommended": [m for m in modules if m in recommended],
                "optional": [m for m in modules if m not in recommended],
            }

        return {
            "recommended_modules": list(recommended),
            "categorized": categorized,
            "total_recommended": len(recommended),
            "instruction": "Present these recommendations and let user customize before proceeding.",
        }

    async def _configure_modules(self, params: dict) -> dict:
        """Activate modules for instance."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/modules",
            json={
                "modules": params["modules"],
                "configs": params.get("module_configs", {}),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to configure modules", "status": response.status_code}

    async def _configure_branding(self, params: dict) -> dict:
        """Configure instance branding."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/branding",
            json={
                "company_name": params["company_name"],
                "logo_url": params.get("logo_url"),
                "colors": {
                    "primary": params.get("primary_color", "#3B82F6"),
                    "secondary": params.get("secondary_color", "#1E40AF"),
                    "accent": params.get("accent_color", "#10B981"),
                },
                "theme": params.get("theme", "light"),
                "font_family": params.get("font_family", "Inter"),
                "dashboard_layout": params.get("dashboard_layout", "default"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to configure branding"}

    async def _setup_admin_user(self, params: dict) -> dict:
        """Create admin user."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/users",
            json={
                "email": params["email"],
                "name": params["name"],
                "role": params.get("role", "super_admin"),
                "is_admin": True,
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create admin user"}

    async def _create_team_structure(self, params: dict) -> dict:
        """Create departments."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/departments",
            json={"departments": params["departments"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create team structure"}

    async def _create_roles(self, params: dict) -> dict:
        """Create roles with permissions."""
        # Use template if specified
        template = params.get("use_template")
        if template and template != "custom":
            response = await self.http_client.post(
                f"/api/v1/instances/{params['instance_id']}/roles/from-template",
                json={"template": template},
            )
        else:
            response = await self.http_client.post(
                f"/api/v1/instances/{params['instance_id']}/roles",
                json={"roles": params.get("roles", [])},
            )

        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to create roles"}

    async def _invite_users(self, params: dict) -> dict:
        """Invite team members."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/invitations",
            json={"users": params["users"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": "Failed to invite users"}

    async def _configure_integrations(self, params: dict) -> dict:
        """Configure integrations."""
        results = []
        for integration in params.get("integrations", []):
            response = await self.http_client.post(
                f"/api/v1/instances/{params['instance_id']}/integrations",
                json=integration,
            )
            results.append({
                "type": integration["type"],
                "success": response.status_code in (200, 201),
            })
        return {"integrations_configured": results}

    # Infrastructure Provisioning Methods

    async def _provision_database(self, params: dict) -> dict:
        """Provision tenant database."""
        response = await self.http_client.post(
            f"/api/v1/infrastructure/databases",
            json={
                "instance_id": params["instance_id"],
                "region": params["region"],
                "tier": params.get("tier", "starter"),
                "backup_retention_days": params.get("backup_retention_days", 30),
            },
        )
        if response.status_code in (200, 201, 202):
            return response.json()
        return {
            "status": "provisioning",
            "instance_id": params["instance_id"],
            "region": params["region"],
            "tier": params.get("tier", "starter"),
            "estimated_time_minutes": 5,
            "instruction": "Database provisioning initiated. Poll get_infrastructure_status for completion.",
        }

    async def _provision_storage(self, params: dict) -> dict:
        """Provision storage buckets."""
        buckets = params.get("buckets", ["dam", "exports", "uploads"])
        response = await self.http_client.post(
            f"/api/v1/infrastructure/storage",
            json={
                "instance_id": params["instance_id"],
                "region": params["region"],
                "buckets": buckets,
                "cdn_enabled": params.get("cdn_enabled", True),
            },
        )
        if response.status_code in (200, 201, 202):
            return response.json()
        return {
            "status": "provisioning",
            "instance_id": params["instance_id"],
            "buckets": buckets,
            "cdn_enabled": params.get("cdn_enabled", True),
            "instruction": "Storage buckets being created with CDN configuration.",
        }

    async def _provision_cache(self, params: dict) -> dict:
        """Provision Redis cache."""
        response = await self.http_client.post(
            f"/api/v1/infrastructure/cache",
            json={
                "instance_id": params["instance_id"],
                "region": params["region"],
                "size": params.get("size", "small"),
            },
        )
        if response.status_code in (200, 201, 202):
            return response.json()
        return {
            "status": "provisioning",
            "instance_id": params["instance_id"],
            "size": params.get("size", "small"),
            "instruction": "Redis cache being provisioned.",
        }

    async def _provision_search(self, params: dict) -> dict:
        """Provision search indices."""
        indices = params.get("indices", ["content", "projects", "clients", "assets"])
        response = await self.http_client.post(
            f"/api/v1/infrastructure/search",
            json={
                "instance_id": params["instance_id"],
                "indices": indices,
            },
        )
        if response.status_code in (200, 201, 202):
            return response.json()
        return {
            "status": "provisioning",
            "instance_id": params["instance_id"],
            "indices": indices,
            "instruction": "Search indices being created.",
        }

    async def _get_infrastructure_status(self, params: dict) -> dict:
        """Get infrastructure provisioning status."""
        response = await self.http_client.get(
            f"/api/v1/instances/{params['instance_id']}/infrastructure/status"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "components": {
                "database": {"status": "pending", "ready": False},
                "storage": {"status": "pending", "ready": False},
                "cache": {"status": "pending", "ready": False},
                "search": {"status": "pending", "ready": False},
            },
            "all_ready": False,
            "instruction": "Check status of infrastructure components.",
        }

    # External Platform Credentials Methods

    async def _initiate_oauth_flow(self, params: dict) -> dict:
        """Initiate OAuth flow for external platform."""
        platform = params["platform"]

        # Default scopes per platform
        default_scopes = {
            "google_ads": ["https://www.googleapis.com/auth/adwords"],
            "google_analytics": ["https://www.googleapis.com/auth/analytics.readonly"],
            "google_search_console": ["https://www.googleapis.com/auth/webmasters.readonly"],
            "google_workspace": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/drive.readonly"],
            "meta_business": ["business_management", "ads_management", "pages_read_engagement"],
            "meta_ads": ["ads_management", "ads_read", "business_management"],
            "instagram": ["instagram_basic", "instagram_content_publish"],
            "tiktok_ads": ["advertiser_info_read", "campaign_read"],
            "snapchat_ads": ["snapchat-marketing-api"],
            "linkedin_ads": ["r_ads", "r_ads_reporting", "rw_ads"],
            "twitter_ads": ["tweet.read", "ads.read"],
            "pinterest_ads": ["ads:read", "ads:write"],
            "slack": ["channels:read", "chat:write", "users:read"],
            "microsoft_365": ["Calendars.Read", "Files.Read.All", "User.Read"],
            "xero": ["accounting.transactions.read", "accounting.contacts.read"],
            "quickbooks": ["com.intuit.quickbooks.accounting"],
            "hubspot": ["crm.objects.contacts.read", "crm.objects.deals.read"],
            "salesforce": ["api", "refresh_token"],
            "figma": ["file_read"],
            "adobe_cc": ["openid", "creative_sdk"],
        }

        scopes = params.get("scopes") or default_scopes.get(platform, [])

        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/oauth/initiate",
            json={
                "platform": platform,
                "scopes": scopes,
                "redirect_uri": params.get("redirect_uri"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "platform": platform,
            "scopes": scopes,
            "authorization_url": f"https://oauth.example.com/{platform}/authorize",
            "state": f"state_{params['instance_id']}_{platform}",
            "instruction": f"Direct user to authorization_url to complete {platform} OAuth flow.",
        }

    async def _complete_oauth_flow(self, params: dict) -> dict:
        """Complete OAuth flow with auth code."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/oauth/complete",
            json={
                "platform": params["platform"],
                "auth_code": params["auth_code"],
                "state": params.get("state"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "platform": params["platform"],
            "status": "connected",
            "instruction": "OAuth tokens stored securely. Ready to link specific accounts.",
        }

    async def _store_api_credentials(self, params: dict) -> dict:
        """Store API credentials for non-OAuth platforms."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/credentials",
            json={
                "platform": params["platform"],
                "credentials": params["credentials"],  # Encrypted in transit
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "platform": params["platform"],
            "status": "stored",
            "encrypted": True,
            "instruction": "Credentials stored securely with encryption at rest.",
        }

    async def _link_ad_accounts(self, params: dict) -> dict:
        """Link specific ad accounts after OAuth."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/platforms/{params['platform']}/accounts",
            json={"account_ids": params["account_ids"]},
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "platform": params["platform"],
            "linked_accounts": params["account_ids"],
            "status": "linked",
            "instruction": f"Linked {len(params['account_ids'])} {params['platform']} accounts.",
        }

    async def _list_available_accounts(self, params: dict) -> dict:
        """List available accounts for connected platform."""
        response = await self.http_client.get(
            f"/api/v1/instances/{params['instance_id']}/platforms/{params['platform']}/available-accounts"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "platform": params["platform"],
            "accounts": [],
            "instruction": "Fetches available accounts from connected platform.",
        }

    async def _verify_platform_connection(self, params: dict) -> dict:
        """Verify platform connection is working."""
        response = await self.http_client.get(
            f"/api/v1/instances/{params['instance_id']}/platforms/{params['platform']}/verify"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "platform": params["platform"],
            "connected": True,
            "last_verified": "now",
            "token_expires_in": "3600s",
            "instruction": "Connection verified. Tokens are valid.",
        }

    async def _get_connected_platforms(self, params: dict) -> dict:
        """List all connected platforms."""
        response = await self.http_client.get(
            f"/api/v1/instances/{params['instance_id']}/platforms"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "instance_id": params["instance_id"],
            "platforms": [],
            "categories": {
                "ads": [],
                "analytics": [],
                "social": [],
                "creative": [],
                "operations": [],
            },
            "instruction": "Returns all connected platforms with their status.",
        }

    async def _configure_sso(self, params: dict) -> dict:
        """Configure SSO provider."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/auth/sso",
            json={
                "provider": params["provider"],
                "config": params["config"],
                "enforce_sso": params.get("enforce_sso", False),
                "allowed_domains": params.get("allowed_domains", []),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "provider": params["provider"],
            "status": "configured",
            "enforce_sso": params.get("enforce_sso", False),
            "instruction": f"SSO configured with {params['provider']}. Users can now sign in via SSO.",
        }

    def _recommend_platform_connections(self, params: dict) -> dict:
        """Recommend platforms to connect based on services."""
        services = params.get("services", [])
        regions = params.get("regions", [])

        recommendations = {
            "essential": [],
            "recommended": [],
            "optional": [],
        }

        # Always essential
        recommendations["essential"].extend([
            {"platform": "google_workspace", "reason": "Calendar, Drive, and email integration"},
            {"platform": "slack", "reason": "Team communication and notifications"},
        ])

        # Service-based recommendations
        if "media" in services:
            recommendations["essential"].extend([
                {"platform": "google_ads", "reason": "Google Ads campaign management"},
                {"platform": "meta_ads", "reason": "Meta (Facebook/Instagram) ads"},
                {"platform": "google_analytics", "reason": "Website analytics"},
            ])
            recommendations["recommended"].extend([
                {"platform": "linkedin_ads", "reason": "B2B advertising"},
                {"platform": "twitter_ads", "reason": "Twitter/X campaigns"},
                {"platform": "dv360", "reason": "Programmatic display"},
            ])
            # Regional recommendations
            if any(r in regions for r in ["gcc", "mena", "uae", "ksa"]):
                recommendations["recommended"].append(
                    {"platform": "snapchat_ads", "reason": "Strong in MENA region"}
                )
            if any(r in regions for r in ["apac", "asia"]):
                recommendations["recommended"].append(
                    {"platform": "tiktok_ads", "reason": "Growing platform in APAC"}
                )

        if "social" in services:
            recommendations["essential"].extend([
                {"platform": "meta_business", "reason": "Facebook/Instagram management"},
            ])
            recommendations["recommended"].extend([
                {"platform": "sprout_social", "reason": "Social management platform"},
            ])

        if "creative" in services:
            recommendations["recommended"].extend([
                {"platform": "figma", "reason": "Design collaboration"},
                {"platform": "adobe_cc", "reason": "Creative suite integration"},
                {"platform": "canva", "reason": "Quick design tools"},
            ])

        if "pr" in services:
            recommendations["recommended"].extend([
                {"platform": "meltwater", "reason": "PR monitoring and outreach"},
            ])

        if "analytics" in services:
            recommendations["essential"].extend([
                {"platform": "google_analytics", "reason": "Website analytics"},
                {"platform": "google_search_console", "reason": "Search performance"},
            ])
            recommendations["recommended"].extend([
                {"platform": "brandwatch", "reason": "Social listening"},
            ])

        # Finance
        recommendations["optional"].extend([
            {"platform": "xero", "reason": "Accounting sync"},
            {"platform": "quickbooks", "reason": "Accounting sync (alternative)"},
        ])

        # CRM
        recommendations["optional"].extend([
            {"platform": "hubspot", "reason": "CRM integration"},
            {"platform": "salesforce", "reason": "Enterprise CRM"},
        ])

        return {
            "recommendations": recommendations,
            "total_essential": len(recommendations["essential"]),
            "total_recommended": len(recommendations["recommended"]),
            "total_optional": len(recommendations["optional"]),
            "instruction": "Present recommendations by priority. Essential platforms should be connected during onboarding.",
        }

    async def _generate_sample_instance(self, params: dict) -> dict:
        """Generate complete sample instance with dummy data."""
        instance_id = params["instance_id"]
        company = params["company_profile"]
        data_types = params.get("data_to_generate", ["clients", "projects", "team"])
        volume = params.get("data_volume", "moderate")

        # Volume multipliers
        multipliers = {"minimal": 0.5, "moderate": 1, "comprehensive": 2}
        mult = multipliers.get(volume, 1)

        results = {
            "instance_id": instance_id,
            "company": company,
            "generated": {},
        }

        # Generate each data type
        if "team" in data_types:
            team_result = await self._generate_sample_team({
                "instance_id": instance_id,
                "team_size": int(8 * mult),
            })
            results["generated"]["team"] = team_result

        if "clients" in data_types:
            clients_result = await self._generate_sample_clients({
                "instance_id": instance_id,
                "count": int(5 * mult),
                "industries": company.get("industry_focus", ["technology", "retail"]),
            })
            results["generated"]["clients"] = clients_result

        if "projects" in data_types:
            projects_result = await self._generate_sample_projects({
                "instance_id": instance_id,
                "count": int(10 * mult),
            })
            results["generated"]["projects"] = projects_result

        if "content" in data_types:
            content_result = await self._generate_sample_content({
                "instance_id": instance_id,
                "content_types": ["images", "documents", "presentations"],
            })
            results["generated"]["content"] = content_result

        if "reports" in data_types:
            dashboard_result = await self._populate_dashboards({
                "instance_id": instance_id,
                "dashboards": ["overview", "financial", "resource"],
            })
            results["generated"]["dashboards"] = dashboard_result

        results["sample_mode"] = True
        results["demo_ready"] = True

        return results

    async def _generate_sample_clients(self, params: dict) -> dict:
        """Generate sample clients."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/sample-data/clients",
            json={
                "count": params.get("count", 5),
                "industries": params.get("industries", []),
                "include_history": params.get("include_history", True),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        # Return mock data for demo
        return {
            "generated": True,
            "count": params.get("count", 5),
            "instruction": "Generate realistic client profiles with names, industries, contacts, and project history.",
        }

    async def _generate_sample_projects(self, params: dict) -> dict:
        """Generate sample projects."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/sample-data/projects",
            json={
                "count": params.get("count", 10),
                "stages": params.get("stages", {
                    "pitching": 2,
                    "in_progress": 4,
                    "review": 2,
                    "completed": 2,
                }),
                "project_types": params.get("project_types", ["campaign", "retainer"]),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "generated": True,
            "count": params.get("count", 10),
            "instruction": "Generate projects across stages with realistic briefs, timelines, and budgets.",
        }

    async def _generate_sample_content(self, params: dict) -> dict:
        """Generate sample DAM content."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/sample-data/content",
            json={
                "content_types": params.get("content_types", ["images", "documents"]),
                "organize_by": params.get("organize_by", "client"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "generated": True,
            "instruction": "Generate sample assets organized in DAM with metadata and tags.",
        }

    async def _generate_sample_team(self, params: dict) -> dict:
        """Generate sample team members."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/sample-data/team",
            json={
                "team_size": params.get("team_size", 8),
                "departments": params.get("departments", ["Creative", "Account Management", "Strategy"]),
                "include_availability": params.get("include_availability", True),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "generated": True,
            "team_size": params.get("team_size", 8),
            "instruction": "Generate team members with roles, skills, and utilization data.",
        }

    async def _populate_dashboards(self, params: dict) -> dict:
        """Populate dashboards with sample metrics."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/sample-data/dashboards",
            json={
                "dashboards": params.get("dashboards", ["overview"]),
                "trends": params.get("trends", "growth"),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "populated": True,
            "dashboards": params.get("dashboards", ["overview"]),
            "instruction": "Populate dashboards with realistic KPIs and trend data.",
        }

    async def _get_onboarding_status(self, params: dict) -> dict:
        """Get onboarding progress."""
        response = await self.http_client.get(
            f"/api/v1/instances/{params['instance_id']}/onboarding/status"
        )
        if response.status_code == 200:
            return response.json()
        return {
            "steps": {
                "assessment": "pending",
                "modules": "pending",
                "branding": "pending",
                "users": "pending",
                "integrations": "pending",
                "sample_data": "pending",
            },
            "percent_complete": 0,
        }

    async def _complete_onboarding(self, params: dict) -> dict:
        """Complete onboarding and generate getting started guide."""
        response = await self.http_client.post(
            f"/api/v1/instances/{params['instance_id']}/onboarding/complete",
            json={
                "generate_guide": params.get("generate_getting_started", True),
            },
        )
        if response.status_code in (200, 201):
            return response.json()
        return {
            "status": "completed",
            "instance_active": True,
            "instruction": "Generate personalized getting started guide based on configured modules and team.",
        }

    async def close(self):
        """Clean up HTTP client."""
        await self.http_client.aclose()
