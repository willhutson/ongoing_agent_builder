"""Tests for Phase 18B: integration context formatting with seeded data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.context_injector import format_integrations


class TestGoogleDriveFormatting:

    def test_with_folder_count(self):
        result = format_integrations([
            {"provider": "google_drive", "status": "ACTIVE", "seededData": {"folderCount": 14}}
        ])
        assert "14 folders scanned" in result

    def test_single_folder(self):
        result = format_integrations([
            {"provider": "google", "status": "ACTIVE", "seededData": {"folderCount": 1}}
        ])
        assert "1 folder scanned" in result

    def test_no_seeded_data(self):
        result = format_integrations([
            {"provider": "google_drive", "status": "ACTIVE"}
        ])
        assert "connected" in result
        assert "no folders found" in result


class TestSlackFormatting:

    def test_with_channel_breakdown(self):
        result = format_integrations([
            {"provider": "slack", "status": "ACTIVE", "seededData": {
                "channelCount": 38, "clientChannels": 6, "projectChannels": 9, "teamChannels": 5
            }}
        ])
        assert "38 channels" in result
        assert "6 client" in result
        assert "9 project" in result
        assert "5 team" in result

    def test_channels_without_breakdown(self):
        result = format_integrations([
            {"provider": "slack", "status": "ACTIVE", "seededData": {"channelCount": 10}}
        ])
        assert "10 channels" in result

    def test_no_seeded_data(self):
        result = format_integrations([
            {"provider": "slack", "status": "ACTIVE"}
        ])
        assert "channel scan pending" in result


class TestHubSpotFormatting:

    def test_contacts_and_companies(self):
        result = format_integrations([
            {"provider": "hubspot", "status": "ACTIVE", "seededData": {
                "contactCount": 23, "companyCount": 11
            }}
        ])
        assert "23 contacts" in result
        assert "11 companies" in result

    def test_contacts_only(self):
        result = format_integrations([
            {"provider": "hubspot", "status": "ACTIVE", "seededData": {"contactCount": 5}}
        ])
        assert "5 contacts" in result
        assert "companies" not in result

    def test_single_contact(self):
        result = format_integrations([
            {"provider": "hubspot", "status": "ACTIVE", "seededData": {"contactCount": 1}}
        ])
        assert "1 contact" in result
        assert "contacts" not in result  # singular

    def test_no_seeded_data(self):
        result = format_integrations([
            {"provider": "hubspot", "status": "ACTIVE"}
        ])
        assert "sync pending" in result


class TestOtherProviders:

    def test_gmail(self):
        result = format_integrations([{"provider": "gmail", "status": "ACTIVE"}])
        assert "Gmail" in result
        assert "email" in result

    def test_figma_with_projects(self):
        result = format_integrations([
            {"provider": "figma", "status": "ACTIVE", "seededData": {"projectCount": 7}}
        ])
        assert "7 projects" in result

    def test_github_with_repos(self):
        result = format_integrations([
            {"provider": "github", "status": "ACTIVE", "seededData": {"repoCount": 3}}
        ])
        assert "3 repositories" in result

    def test_github_single_repo(self):
        result = format_integrations([
            {"provider": "github", "status": "ACTIVE", "seededData": {"repoCount": 1}}
        ])
        assert "1 repository" in result

    def test_quickbooks_with_customers(self):
        result = format_integrations([
            {"provider": "quickbooks", "status": "ACTIVE", "seededData": {"customerCount": 15}}
        ])
        assert "15 customers" in result

    def test_unknown_provider(self):
        result = format_integrations([
            {"provider": "snowflake", "status": "ACTIVE"}
        ])
        assert "snowflake: connected" in result


class TestEdgeCases:

    def test_empty_list(self):
        assert format_integrations([]) == ""

    def test_none_input(self):
        assert format_integrations(None) == ""

    def test_seeded_data_none(self):
        result = format_integrations([
            {"provider": "google_drive", "status": "ACTIVE", "seededData": None}
        ])
        assert "connected" in result

    def test_string_counts_coerced(self):
        """Counts stored as strings should be handled gracefully."""
        result = format_integrations([
            {"provider": "hubspot", "status": "ACTIVE", "seededData": {
                "contactCount": "23", "companyCount": "11"
            }}
        ])
        assert "23 contacts" in result
        assert "11 companies" in result

    def test_multiple_integrations(self):
        result = format_integrations([
            {"provider": "google_drive", "status": "ACTIVE", "seededData": {"folderCount": 14}},
            {"provider": "slack", "status": "ACTIVE", "seededData": {"channelCount": 38}},
            {"provider": "hubspot", "status": "ACTIVE", "seededData": {"contactCount": 23}},
        ])
        assert "Google Drive" in result
        assert "Slack" in result
        assert "HubSpot" in result
