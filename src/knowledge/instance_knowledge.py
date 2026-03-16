"""
Instance Knowledge (Layer 4) — Per-organization context documents.

From AGENT_ARCHITECTURE.md:
- Layer 4 is per-org knowledge: brand guides, tone docs, client preferences
- Loaded at agent runtime and injected into the system prompt
- Documents are scoped by organizationId
- Supports versioning and categories (brand, process, client, industry)

Phase 2+ implementation: This module defines the interfaces and in-memory storage.
Production will use PostgreSQL via Prisma with vector search for retrieval.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone


class KnowledgeCategory(str, Enum):
    """Categories of instance knowledge documents."""
    BRAND = "brand"          # Brand guides, voice docs, visual identity
    PROCESS = "process"      # SOPs, workflows, approval chains
    CLIENT = "client"        # Client preferences, past feedback, relationship notes
    INDUSTRY = "industry"    # Vertical-specific knowledge, market insights
    TEMPLATE = "template"    # Reusable templates, frameworks
    REFERENCE = "reference"  # General reference material


@dataclass
class KnowledgeDocument:
    """A knowledge document belonging to a specific organization."""
    id: str
    organization_id: str
    title: str
    content: str
    category: KnowledgeCategory
    tags: list[str] = field(default_factory=list)

    # Scoping: which agents/modules can access this document
    allowed_agents: list[str] = field(default_factory=list)  # Empty = all agents
    allowed_modules: list[str] = field(default_factory=list)  # Empty = all modules

    # Metadata
    created_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None
    version: int = 1
    is_active: bool = True


# =============================================================================
# INSTANCE KNOWLEDGE STORE (Phase 2 — will be backed by DB + vector search)
# =============================================================================

# In-memory store; Phase 2 will use Prisma/PostgreSQL + pgvector
_knowledge_store: dict[str, dict[str, KnowledgeDocument]] = {}
# Structure: { organization_id: { doc_id: KnowledgeDocument } }


async def get_knowledge_documents(
    organization_id: str,
    category: Optional[KnowledgeCategory] = None,
    agent_type: Optional[str] = None,
    module_subdomain: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> list[KnowledgeDocument]:
    """
    Get knowledge documents for an organization, optionally filtered.

    Filters:
    - category: Only docs in this category
    - agent_type: Only docs accessible to this agent (or docs with no agent restriction)
    - module_subdomain: Only docs accessible from this module (or docs with no module restriction)
    - tags: Only docs matching any of these tags
    """
    org_docs = _knowledge_store.get(organization_id, {})
    results = []

    for doc in org_docs.values():
        if not doc.is_active:
            continue
        if category and doc.category != category:
            continue
        if agent_type and doc.allowed_agents and agent_type not in doc.allowed_agents:
            continue
        if module_subdomain and doc.allowed_modules and module_subdomain not in doc.allowed_modules:
            continue
        if tags and not any(t in doc.tags for t in tags):
            continue
        results.append(doc)

    return results


async def get_knowledge_document(
    organization_id: str, doc_id: str
) -> Optional[KnowledgeDocument]:
    """Get a specific knowledge document."""
    org_docs = _knowledge_store.get(organization_id, {})
    return org_docs.get(doc_id)


async def save_knowledge_document(doc: KnowledgeDocument) -> KnowledgeDocument:
    """Save or update a knowledge document."""
    if doc.organization_id not in _knowledge_store:
        _knowledge_store[doc.organization_id] = {}
    doc.updated_at = datetime.now(timezone.utc).isoformat()
    _knowledge_store[doc.organization_id][doc.id] = doc
    return doc


async def delete_knowledge_document(organization_id: str, doc_id: str) -> bool:
    """Soft-delete a knowledge document."""
    org_docs = _knowledge_store.get(organization_id, {})
    doc = org_docs.get(doc_id)
    if doc:
        doc.is_active = False
        return True
    return False


async def build_knowledge_context(
    organization_id: str,
    agent_type: Optional[str] = None,
    module_subdomain: Optional[str] = None,
    max_docs: int = 5,
) -> str:
    """
    Build a knowledge context string for injection into agent system prompts.

    Retrieves the most relevant documents for the given org/agent/module
    and formats them as a prompt section. Called during agent initialization.

    Phase 2 will use vector similarity search for better relevance ranking.
    """
    docs = await get_knowledge_documents(
        organization_id=organization_id,
        agent_type=agent_type,
        module_subdomain=module_subdomain,
    )

    if not docs:
        return ""

    # Limit to max_docs (Phase 2: rank by relevance)
    docs = docs[:max_docs]

    sections = ["## Organization Knowledge"]
    for doc in docs:
        sections.append(f"### {doc.title} [{doc.category.value}]")
        sections.append(doc.content)
        sections.append("")

    return "\n".join(sections)
