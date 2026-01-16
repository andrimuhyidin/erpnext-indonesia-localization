# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
Custom Exception Classes for ERPNext Indonesia Localization

This module provides standardized exception handling across the application.
All custom exceptions inherit from base classes to ensure consistent error handling.
"""

from typing import Any, Optional


class EILBaseException(Exception):
    """Base exception for all ERPNext Indonesia Localization errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Initialize base exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for categorization
            details: Additional error details for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "EIL_ERROR"
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# =============================================================================
# API Exceptions
# =============================================================================

class PajakioAPIError(EILBaseException):
    """Base exception for Pajak.io API related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Initialize Pajak.io API error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code from API response
            response_data: Raw response data from API
            details: Additional error details
        """
        super().__init__(message, error_code or "PAJAKIO_API_ERROR", details)
        self.status_code = status_code
        self.response_data = response_data or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = super().to_dict()
        result["status_code"] = self.status_code
        result["response_data"] = self.response_data
        return result


class PajakioConnectionError(PajakioAPIError):
    """Exception for Pajak.io API connection failures."""

    def __init__(
        self,
        message: str = "Failed to connect to Pajak.io API",
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="PAJAKIO_CONNECTION_ERROR",
            details=details
        )


class PajakioTimeoutError(PajakioAPIError):
    """Exception for Pajak.io API timeout errors."""

    def __init__(
        self,
        message: str = "Request to Pajak.io API timed out",
        timeout_seconds: Optional[int] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            error_code="PAJAKIO_TIMEOUT_ERROR",
            details=details
        )


class PajakioAuthenticationError(PajakioAPIError):
    """Exception for Pajak.io API authentication failures."""

    def __init__(
        self,
        message: str = "Pajak.io API authentication failed",
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="PAJAKIO_AUTH_ERROR",
            status_code=401,
            details=details
        )


class PajakioRateLimitError(PajakioAPIError):
    """Exception for Pajak.io API rate limit errors."""

    def __init__(
        self,
        message: str = "Pajak.io API rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message,
            error_code="PAJAKIO_RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        )


class PajakioValidationError(PajakioAPIError):
    """Exception for Pajak.io API validation errors."""

    def __init__(
        self,
        message: str,
        field_errors: Optional[dict[str, list[str]]] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if field_errors:
            details["field_errors"] = field_errors
        super().__init__(
            message=message,
            error_code="PAJAKIO_VALIDATION_ERROR",
            status_code=400,
            details=details
        )


# =============================================================================
# CoreTax Exceptions
# =============================================================================

class CoreTaxError(EILBaseException):
    """Base exception for CoreTax related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code=error_code or "CORETAX_ERROR",
            details=details
        )


class CoreTaxExportError(CoreTaxError):
    """Exception for CoreTax XML export failures."""

    def __init__(
        self,
        message: str,
        invoice_name: Optional[str] = None,
        export_type: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if invoice_name:
            details["invoice_name"] = invoice_name
        if export_type:
            details["export_type"] = export_type
        super().__init__(
            message=message,
            error_code="CORETAX_EXPORT_ERROR",
            details=details
        )


class CoreTaxImportError(CoreTaxError):
    """Exception for CoreTax data import failures."""

    def __init__(
        self,
        message: str,
        row_number: Optional[int] = None,
        file_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if row_number:
            details["row_number"] = row_number
        if file_name:
            details["file_name"] = file_name
        super().__init__(
            message=message,
            error_code="CORETAX_IMPORT_ERROR",
            details=details
        )


class CoreTaxValidationError(CoreTaxError):
    """Exception for CoreTax data validation failures."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        expected_format: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if field_name:
            details["field_name"] = field_name
        if field_value is not None:
            details["field_value"] = str(field_value)
        if expected_format:
            details["expected_format"] = expected_format
        super().__init__(
            message=message,
            error_code="CORETAX_VALIDATION_ERROR",
            details=details
        )


# =============================================================================
# VAT Exceptions
# =============================================================================

class VATError(EILBaseException):
    """Base exception for VAT related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        document_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if document_name:
            details["document_name"] = document_name
        super().__init__(
            message=message,
            error_code=error_code or "VAT_ERROR",
            details=details
        )


class VATOutputError(VATError):
    """Exception for VAT Output related errors."""

    def __init__(
        self,
        message: str,
        document_name: Optional[str] = None,
        transaction_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if transaction_id:
            details["transaction_id"] = transaction_id
        super().__init__(
            message=message,
            error_code="VAT_OUTPUT_ERROR",
            document_name=document_name,
            details=details
        )


class VATInputError(VATError):
    """Exception for VAT Input related errors."""

    def __init__(
        self,
        message: str,
        document_name: Optional[str] = None,
        transaction_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if transaction_id:
            details["transaction_id"] = transaction_id
        super().__init__(
            message=message,
            error_code="VAT_INPUT_ERROR",
            document_name=document_name,
            details=details
        )


# =============================================================================
# Withholding Tax Exceptions
# =============================================================================

class WithholdingTaxError(EILBaseException):
    """Exception for Withholding Tax (e-Bupot) related errors."""

    def __init__(
        self,
        message: str,
        certificate_name: Optional[str] = None,
        transaction_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if certificate_name:
            details["certificate_name"] = certificate_name
        if transaction_id:
            details["transaction_id"] = transaction_id
        super().__init__(
            message=message,
            error_code="WITHHOLDING_TAX_ERROR",
            details=details
        )


# =============================================================================
# Validation Exceptions
# =============================================================================

class TaxIDValidationError(EILBaseException):
    """Exception for Tax ID validation failures."""

    def __init__(
        self,
        message: str,
        id_type: str,  # 'NPWP', 'NIK', 'NITKU'
        id_value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        details["id_type"] = id_type
        if id_value:
            details["id_value"] = id_value
        super().__init__(
            message=message,
            error_code="TAX_ID_VALIDATION_ERROR",
            details=details
        )


class NPWPValidationError(TaxIDValidationError):
    """Exception for NPWP validation failures."""

    def __init__(
        self,
        message: str = "Invalid NPWP format. NPWP must be 15 digits.",
        npwp_value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            id_type="NPWP",
            id_value=npwp_value,
            details=details
        )


class NIKValidationError(TaxIDValidationError):
    """Exception for NIK validation failures."""

    def __init__(
        self,
        message: str = "Invalid NIK format. NIK must be 16 digits.",
        nik_value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            id_type="NIK",
            id_value=nik_value,
            details=details
        )


class NITKUValidationError(TaxIDValidationError):
    """Exception for NITKU validation failures."""

    def __init__(
        self,
        message: str = "Invalid NITKU format. NITKU must be 3 digits.",
        nitku_value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            id_type="NITKU",
            id_value=nitku_value,
            details=details
        )


# =============================================================================
# Configuration Exceptions
# =============================================================================

class ConfigurationError(EILBaseException):
    """Exception for configuration related errors."""

    def __init__(
        self,
        message: str,
        setting_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if setting_name:
            details["setting_name"] = setting_name
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details
        )


class MissingAPIKeyError(ConfigurationError):
    """Exception for missing API key configuration."""

    def __init__(
        self,
        api_name: str = "Pajak.io",
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=f"{api_name} API key is not configured. Please set it in Indonesia Localization Settings.",
            setting_name=f"{api_name.lower().replace('.', '')}_api_key",
            details=details
        )


class MissingURLConfigError(ConfigurationError):
    """Exception for missing URL configuration."""

    def __init__(
        self,
        url_field: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=f"API URL '{url_field}' is not configured in Indonesia Localization Settings.",
            setting_name=url_field,
            details=details
        )


# =============================================================================
# Batch Processing Exceptions
# =============================================================================

class BatchProcessingError(EILBaseException):
    """Exception for batch processing failures."""

    def __init__(
        self,
        message: str,
        total_items: Optional[int] = None,
        processed_items: Optional[int] = None,
        failed_items: Optional[list[str]] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if total_items is not None:
            details["total_items"] = total_items
        if processed_items is not None:
            details["processed_items"] = processed_items
        if failed_items:
            details["failed_items"] = failed_items
        super().__init__(
            message=message,
            error_code="BATCH_PROCESSING_ERROR",
            details=details
        )


# =============================================================================
# Export All Exceptions
# =============================================================================

__all__ = [
    # Base
    "EILBaseException",

    # API
    "PajakioAPIError",
    "PajakioConnectionError",
    "PajakioTimeoutError",
    "PajakioAuthenticationError",
    "PajakioRateLimitError",
    "PajakioValidationError",

    # CoreTax
    "CoreTaxError",
    "CoreTaxExportError",
    "CoreTaxImportError",
    "CoreTaxValidationError",

    # VAT
    "VATError",
    "VATOutputError",
    "VATInputError",

    # Withholding Tax
    "WithholdingTaxError",

    # Validation
    "TaxIDValidationError",
    "NPWPValidationError",
    "NIKValidationError",
    "NITKUValidationError",

    # Configuration
    "ConfigurationError",
    "MissingAPIKeyError",
    "MissingURLConfigError",

    # Batch Processing
    "BatchProcessingError",
]
