# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
ERPNext Indonesia Localization Utilities

This package contains utility functions organized by category:
- api: API integration utilities (Pajak.io helpers)
- validation: Data validation utilities
- export: Export utilities (XML, etc.)
- exceptions: Custom exception classes
- Core utilities: audit, bulk_operations, constants, data, install, template_tax
"""

# Import commonly used utilities for easier access
from erpnext_indonesia_localization.utils.constants import *
from erpnext_indonesia_localization.utils.data import *

# Import custom exceptions for easy access
from erpnext_indonesia_localization.utils.exceptions import (
    EILBaseException,
    PajakioAPIError,
    PajakioConnectionError,
    PajakioTimeoutError,
    PajakioAuthenticationError,
    PajakioRateLimitError,
    PajakioValidationError,
    CoreTaxError,
    CoreTaxExportError,
    CoreTaxImportError,
    CoreTaxValidationError,
    VATError,
    VATOutputError,
    VATInputError,
    WithholdingTaxError,
    TaxIDValidationError,
    NPWPValidationError,
    NIKValidationError,
    NITKUValidationError,
    ConfigurationError,
    MissingAPIKeyError,
    MissingURLConfigError,
    BatchProcessingError,
)

__all__ = [
    # Exceptions
    "EILBaseException",
    "PajakioAPIError",
    "PajakioConnectionError",
    "PajakioTimeoutError",
    "PajakioAuthenticationError",
    "PajakioRateLimitError",
    "PajakioValidationError",
    "CoreTaxError",
    "CoreTaxExportError",
    "CoreTaxImportError",
    "CoreTaxValidationError",
    "VATError",
    "VATOutputError",
    "VATInputError",
    "WithholdingTaxError",
    "TaxIDValidationError",
    "NPWPValidationError",
    "NIKValidationError",
    "NITKUValidationError",
    "ConfigurationError",
    "MissingAPIKeyError",
    "MissingURLConfigError",
    "BatchProcessingError",
]
