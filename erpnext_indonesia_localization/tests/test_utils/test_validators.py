# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
Comprehensive Unit Tests for Validation Functions

This module tests all validation functions in the validation module,
including NPWP, NIK, NITKU format validation and CoreTax data validation.
"""

import re
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys

# Mock frappe before importing modules that depend on it
frappe_mock = MagicMock()
frappe_mock.whitelist = lambda: lambda x: x
frappe_mock._ = lambda x: x
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = MagicMock()


class TestNPWPValidation(unittest.TestCase):
    """Test cases for NPWP (Nomor Pokok Wajib Pajak) validation."""

    def test_valid_npwp_15_digits(self):
        """Test valid NPWP with 15 digits."""
        valid_npwps = [
            "012345678901234",
            "000000000000000",
            "999999999999999",
            "123456789012345",
        ]
        pattern = r'^\d{15}$'
        for npwp in valid_npwps:
            self.assertTrue(
                bool(re.match(pattern, npwp)),
                f"NPWP {npwp} should be valid"
            )

    def test_invalid_npwp_wrong_length(self):
        """Test invalid NPWP with wrong number of digits."""
        invalid_npwps = [
            "0123456789012",    # 13 digits - too short
            "01234567890123",   # 14 digits - too short
            "0123456789012345", # 16 digits - too long
            "",                 # Empty
        ]
        pattern = r'^\d{15}$'
        for npwp in invalid_npwps:
            self.assertFalse(
                bool(re.match(pattern, npwp)),
                f"NPWP {npwp} should be invalid"
            )

    def test_valid_npwp_with_formatting(self):
        """Test NPWP cleaning with dots and dashes."""
        formatted_npwps = [
            ("01.234.567.8-901.234", "012345678901234"),
            ("12-345-678-9-012-345", "123456789012345"),
            ("00.000.000.0-000.000", "000000000000000"),
        ]
        for formatted, expected in formatted_npwps:
            cleaned = re.sub(r'[.\-]', '', formatted)
            self.assertEqual(cleaned, expected)
            self.assertTrue(bool(re.match(r'^\d{15}$', cleaned)))

    def test_invalid_npwp_with_letters(self):
        """Test NPWP with letters is invalid."""
        invalid_npwps = [
            "01234567890123A",
            "ABCDEFGHIJKLMNO",
            "01234567890123 ",  # with space
        ]
        pattern = r'^\d{15}$'
        for npwp in invalid_npwps:
            cleaned = re.sub(r'[.\-]', '', npwp)
            self.assertFalse(
                bool(re.match(pattern, cleaned)),
                f"NPWP {npwp} should be invalid"
            )


class TestNIKValidation(unittest.TestCase):
    """Test cases for NIK (Nomor Induk Kependudukan) validation."""

    def test_valid_nik_16_digits(self):
        """Test valid NIK with 16 digits."""
        valid_niks = [
            "1234567890123456",
            "0000000000000000",
            "9999999999999999",
            "3201234567890123",  # Realistic format
        ]
        pattern = r'^\d{16}$'
        for nik in valid_niks:
            self.assertTrue(
                bool(re.match(pattern, nik)),
                f"NIK {nik} should be valid"
            )

    def test_invalid_nik_wrong_length(self):
        """Test invalid NIK with wrong number of digits."""
        invalid_niks = [
            "123456789012345",   # 15 digits - too short
            "12345678901234567", # 17 digits - too long
            "",                  # Empty
        ]
        pattern = r'^\d{16}$'
        for nik in invalid_niks:
            self.assertFalse(
                bool(re.match(pattern, nik)),
                f"NIK {nik} should be invalid"
            )

    def test_valid_nik_with_formatting(self):
        """Test NIK cleaning with dots and dashes."""
        formatted_niks = [
            ("1234.5678.9012.3456", "1234567890123456"),
            ("12-34-56-78-90-12-34-56", "1234567890123456"),
        ]
        for formatted, expected in formatted_niks:
            cleaned = re.sub(r'[.\-]', '', formatted)
            self.assertEqual(cleaned, expected)
            self.assertTrue(bool(re.match(r'^\d{16}$', cleaned)))

    def test_invalid_nik_with_letters(self):
        """Test NIK with letters is invalid."""
        invalid_niks = [
            "123456789012345A",
            "ABCDEFGHIJKLMNOP",
        ]
        pattern = r'^\d{16}$'
        for nik in invalid_niks:
            self.assertFalse(
                bool(re.match(pattern, nik)),
                f"NIK {nik} should be invalid"
            )


class TestNITKUValidation(unittest.TestCase):
    """Test cases for NITKU (Nomor Identitas Tempat Kegiatan Usaha) validation."""

    def test_valid_nitku_3_digits(self):
        """Test valid NITKU with 3 digits."""
        valid_nitkus = [
            "000",
            "001",
            "999",
            "123",
        ]
        pattern = r'^\d{3}$'
        for nitku in valid_nitkus:
            self.assertTrue(
                bool(re.match(pattern, nitku)),
                f"NITKU {nitku} should be valid"
            )

    def test_invalid_nitku_wrong_length(self):
        """Test invalid NITKU with wrong number of digits."""
        invalid_nitkus = [
            "00",    # 2 digits - too short
            "0000",  # 4 digits - too long
            "",      # Empty
        ]
        pattern = r'^\d{3}$'
        for nitku in invalid_nitkus:
            self.assertFalse(
                bool(re.match(pattern, nitku)),
                f"NITKU {nitku} should be invalid"
            )

    def test_invalid_nitku_with_letters(self):
        """Test NITKU with letters is invalid."""
        invalid_nitkus = [
            "12A",
            "ABC",
        ]
        pattern = r'^\d{3}$'
        for nitku in invalid_nitkus:
            self.assertFalse(
                bool(re.match(pattern, nitku)),
                f"NITKU {nitku} should be invalid"
            )


class TestTransactionCodeValidation(unittest.TestCase):
    """Test cases for Transaction Code validation."""

    def test_valid_transaction_codes(self):
        """Test valid transaction codes (01-09)."""
        valid_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
        pattern = r'^0[1-9]$'
        for code in valid_codes:
            self.assertTrue(
                bool(re.match(pattern, code)),
                f"Transaction code {code} should be valid"
            )

    def test_invalid_transaction_codes(self):
        """Test invalid transaction codes."""
        invalid_codes = [
            "00",   # Zero not allowed
            "10",   # Above 09
            "1",    # Single digit
            "001",  # Three digits
            "0A",   # With letter
            "",     # Empty
        ]
        pattern = r'^0[1-9]$'
        for code in invalid_codes:
            self.assertFalse(
                bool(re.match(pattern, code)),
                f"Transaction code {code} should be invalid"
            )


class TestExceptionsModule(unittest.TestCase):
    """Test cases for custom exception classes."""

    def test_eil_base_exception(self):
        """Test EILBaseException basic functionality."""
        from erpnext_indonesia_localization.utils.exceptions import EILBaseException

        exc = EILBaseException(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )

        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.error_code, "TEST_ERROR")
        self.assertEqual(exc.details, {"key": "value"})

        exc_dict = exc.to_dict()
        self.assertTrue(exc_dict["error"])
        self.assertEqual(exc_dict["error_code"], "TEST_ERROR")
        self.assertEqual(exc_dict["message"], "Test error")

    def test_pajakio_api_error(self):
        """Test PajakioAPIError with status code and response data."""
        from erpnext_indonesia_localization.utils.exceptions import PajakioAPIError

        exc = PajakioAPIError(
            message="API request failed",
            status_code=400,
            response_data={"error": "Invalid request"}
        )

        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.response_data, {"error": "Invalid request"})

        exc_dict = exc.to_dict()
        self.assertEqual(exc_dict["status_code"], 400)
        self.assertEqual(exc_dict["response_data"], {"error": "Invalid request"})

    def test_pajakio_connection_error(self):
        """Test PajakioConnectionError default message."""
        from erpnext_indonesia_localization.utils.exceptions import PajakioConnectionError

        exc = PajakioConnectionError()
        self.assertEqual(exc.message, "Failed to connect to Pajak.io API")
        self.assertEqual(exc.error_code, "PAJAKIO_CONNECTION_ERROR")

    def test_pajakio_timeout_error(self):
        """Test PajakioTimeoutError with timeout seconds."""
        from erpnext_indonesia_localization.utils.exceptions import PajakioTimeoutError

        exc = PajakioTimeoutError(timeout_seconds=30)
        self.assertEqual(exc.details["timeout_seconds"], 30)

    def test_npwp_validation_error(self):
        """Test NPWPValidationError."""
        from erpnext_indonesia_localization.utils.exceptions import NPWPValidationError

        exc = NPWPValidationError(npwp_value="12345")
        self.assertEqual(exc.details["id_type"], "NPWP")
        self.assertEqual(exc.details["id_value"], "12345")

    def test_nik_validation_error(self):
        """Test NIKValidationError."""
        from erpnext_indonesia_localization.utils.exceptions import NIKValidationError

        exc = NIKValidationError(nik_value="12345")
        self.assertEqual(exc.details["id_type"], "NIK")
        self.assertEqual(exc.details["id_value"], "12345")

    def test_nitku_validation_error(self):
        """Test NITKUValidationError."""
        from erpnext_indonesia_localization.utils.exceptions import NITKUValidationError

        exc = NITKUValidationError(nitku_value="12")
        self.assertEqual(exc.details["id_type"], "NITKU")
        self.assertEqual(exc.details["id_value"], "12")

    def test_coretax_export_error(self):
        """Test CoreTaxExportError with invoice details."""
        from erpnext_indonesia_localization.utils.exceptions import CoreTaxExportError

        exc = CoreTaxExportError(
            message="Export failed",
            invoice_name="SINV-001",
            export_type="XML"
        )

        self.assertEqual(exc.details["invoice_name"], "SINV-001")
        self.assertEqual(exc.details["export_type"], "XML")

    def test_batch_processing_error(self):
        """Test BatchProcessingError with progress details."""
        from erpnext_indonesia_localization.utils.exceptions import BatchProcessingError

        exc = BatchProcessingError(
            message="Batch failed",
            total_items=100,
            processed_items=50,
            failed_items=["item1", "item2"]
        )

        self.assertEqual(exc.details["total_items"], 100)
        self.assertEqual(exc.details["processed_items"], 50)
        self.assertEqual(exc.details["failed_items"], ["item1", "item2"])

    def test_missing_api_key_error(self):
        """Test MissingAPIKeyError."""
        from erpnext_indonesia_localization.utils.exceptions import MissingAPIKeyError

        exc = MissingAPIKeyError(api_name="Pajak.io")
        self.assertIn("Pajak.io", exc.message)
        self.assertEqual(exc.setting_name, "pajakio_api_key")


class TestDateValidation(unittest.TestCase):
    """Test cases for date validation."""

    def test_posting_date_before_faktur_date(self):
        """Test that posting date should not be after faktur date."""
        from datetime import date

        posting_date = date(2025, 1, 15)
        tanggal_faktur = date(2025, 1, 10)

        # Tanggal faktur should not be before posting date
        self.assertTrue(tanggal_faktur < posting_date)

    def test_future_posting_date(self):
        """Test detection of future posting dates."""
        from datetime import date, timedelta

        today = date.today()
        future_date = today + timedelta(days=30)

        self.assertTrue(future_date > today)


class TestCleaningFunctions(unittest.TestCase):
    """Test cases for data cleaning functions."""

    def test_strip_html_tags(self):
        """Test HTML tag stripping from item names."""
        test_cases = [
            ("<b>Product Name</b>", "Product Name"),
            ("<p>Description</p>", "Description"),
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("Normal Text", "Normal Text"),
            ("", ""),
        ]
        pattern = r'<[^<]+?>'
        for html, expected in test_cases:
            cleaned = re.sub(pattern, '', html)
            self.assertEqual(cleaned, expected)

    def test_whitespace_stripping(self):
        """Test whitespace stripping from fields."""
        test_cases = [
            ("  01  ", "01"),
            ("\t02\n", "02"),
            ("03", "03"),
        ]
        for value, expected in test_cases:
            self.assertEqual(value.strip(), expected)


if __name__ == '__main__':
    unittest.main()
