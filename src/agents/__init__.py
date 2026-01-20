# Agent definitions
from .base import BaseAgent

# Foundation agents
from .rfp_agent import RFPAgent
from .brief_agent import BriefAgent
from .content_agent import ContentAgent
from .commercial_agent import CommercialAgent

# Studio agents
from .presentation_agent import PresentationAgent
from .copy_agent import CopyAgent
from .image_agent import ImageAgent

# Video pipeline
from .video_script_agent import VideoScriptAgent
from .video_storyboard_agent import VideoStoryboardAgent
from .video_production_agent import VideoProductionAgent

# Distribution agents
from .report_agent import ReportAgent
from .approve_agent import ApproveAgent
from .brief_update_agent import BriefUpdateAgent

# Gateways
from .gateway_whatsapp import WhatsAppGateway
from .gateway_email import EmailGateway
from .gateway_slack import SlackGateway
from .gateway_sms import SMSGateway

# Brand agents
from .brand_voice_agent import BrandVoiceAgent
from .brand_visual_agent import BrandVisualAgent
from .brand_guidelines_agent import BrandGuidelinesAgent

# Operations agents
from .resource_agent import ResourceAgent
from .workflow_agent import WorkflowAgent
from .ops_reporting_agent import OpsReportingAgent

# Client agents
from .crm_agent import CRMAgent
from .scope_agent import ScopeAgent
from .onboarding_agent import OnboardingAgent
from .instance_onboarding_agent import InstanceOnboardingAgent
from .instance_analytics_agent import InstanceAnalyticsAgent
from .instance_success_agent import InstanceSuccessAgent

# Media agents
from .media_buying_agent import MediaBuyingAgent
from .campaign_agent import CampaignAgent

# Social agents
from .social_listening_agent import SocialListeningAgent
from .community_agent import CommunityAgent
from .social_analytics_agent import SocialAnalyticsAgent

# Performance agents
from .brand_performance_agent import BrandPerformanceAgent
from .campaign_analytics_agent import CampaignAnalyticsAgent
from .competitor_agent import CompetitorAgent

# Finance agents
from .invoice_agent import InvoiceAgent
from .forecast_agent import ForecastAgent
from .budget_agent import BudgetAgent

# Quality agents
from .qa_agent import QAAgent
from .legal_agent import LegalAgent

# Knowledge agents
from .knowledge_agent import KnowledgeAgent
from .training_agent import TrainingAgent

# Specialized agents
from .influencer_agent import InfluencerAgent
from .pr_agent import PRAgent
from .events_agent import EventsAgent
from .localization_agent import LocalizationAgent
from .accessibility_agent import AccessibilityAgent

# Meta agents
from .prompt_helper_agent import PromptHelperAgent

__all__ = [
    # Base
    "BaseAgent",
    # Foundation
    "RFPAgent",
    "BriefAgent",
    "ContentAgent",
    "CommercialAgent",
    # Studio
    "PresentationAgent",
    "CopyAgent",
    "ImageAgent",
    # Video
    "VideoScriptAgent",
    "VideoStoryboardAgent",
    "VideoProductionAgent",
    # Distribution
    "ReportAgent",
    "ApproveAgent",
    "BriefUpdateAgent",
    # Gateways
    "WhatsAppGateway",
    "EmailGateway",
    "SlackGateway",
    "SMSGateway",
    # Brand
    "BrandVoiceAgent",
    "BrandVisualAgent",
    "BrandGuidelinesAgent",
    # Operations
    "ResourceAgent",
    "WorkflowAgent",
    "OpsReportingAgent",
    # Client
    "CRMAgent",
    "ScopeAgent",
    "OnboardingAgent",
    "InstanceOnboardingAgent",
    "InstanceAnalyticsAgent",
    "InstanceSuccessAgent",
    # Media
    "MediaBuyingAgent",
    "CampaignAgent",
    # Social
    "SocialListeningAgent",
    "CommunityAgent",
    "SocialAnalyticsAgent",
    # Performance
    "BrandPerformanceAgent",
    "CampaignAnalyticsAgent",
    "CompetitorAgent",
    # Finance
    "InvoiceAgent",
    "ForecastAgent",
    "BudgetAgent",
    # Quality
    "QAAgent",
    "LegalAgent",
    # Knowledge
    "KnowledgeAgent",
    "TrainingAgent",
    # Specialized
    "InfluencerAgent",
    "PRAgent",
    "EventsAgent",
    "LocalizationAgent",
    "AccessibilityAgent",
    # Meta
    "PromptHelperAgent",
]
