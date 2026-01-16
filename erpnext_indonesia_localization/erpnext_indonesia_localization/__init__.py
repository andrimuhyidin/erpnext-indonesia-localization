# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
ERPNext Indonesia Localization - Module Compatibility Layer

This module exists solely for Frappe's module discovery mechanism.
Frappe requires this nested structure (app_name.module_name) for proper
module synchronization during app installation and migration.

This is a minimal compatibility layer - all actual functionality is in
the root level modules (api, doc_events, etc.).

DO NOT import anything here to avoid circular dependencies.
"""

# This module is intentionally minimal - it exists only for Frappe module discovery
# All actual functionality is in root level modules

__all__ = []
