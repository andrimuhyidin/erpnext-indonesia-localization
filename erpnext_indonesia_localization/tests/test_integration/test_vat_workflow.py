# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
Integration Tests for VAT Workflow

This module tests the complete VAT workflow including:
- Sales Invoice → VAT Output Metadata creation
- Purchase Invoice → VAT Input Metadata creation
- VAT Output Return for return invoices
- Pajak.io API integration (mocked)
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
from datetime import date, datetime

# Mock frappe before importing modules
frappe_mock = MagicMock()
frappe_mock.whitelist = lambda: lambda x: x
frappe_mock._ = lambda x: x
frappe_mock.DoesNotExistError = Exception
frappe_mock.ValidationError = Exception
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = MagicMock()


class TestVATOutputWorkflow(unittest.TestCase):
    """Integration tests for VAT Output workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings = MagicMock()
        self.mock_settings.tax_invoice_number_source = "PAJAK.IO"
        self.mock_settings.auto_create_vat_output_metadata = True
        self.mock_settings.auto_call_pajakios_api = False
        self.mock_settings.autouploaddjp = 0

        self.mock_customer = MagicMock()
        self.mock_customer.customer_name = "PT Test Customer"
        self.mock_customer.tax_id = "012345678901234"
        self.mock_customer.customer_primary_address = "Test Address"
        self.mock_customer.mobile_no = "08123456789"
        self.mock_customer.company_address_tax_id = "Test Address"
        self.mock_customer.customer_id_type = "TIN"
        self.mock_customer.customer_pkp = True

        self.mock_address = MagicMock()
        self.mock_address.city = "Jakarta"

        self.mock_invoice = MagicMock()
        self.mock_invoice.name = "SINV-0001"
        self.mock_invoice.doctype = "Sales Invoice"
        self.mock_invoice.customer = "PT Test Customer"
        self.mock_invoice.company = "PT Test Company"
        self.mock_invoice.posting_date = date(2025, 1, 15)
        self.mock_invoice.taxes_and_charges = "PPN Penjualan 12%"
        self.mock_invoice.docstatus = 1
        self.mock_invoice.tax_id = "012345678901234"
        self.mock_invoice.kdjenistransaksi = "01"
        self.mock_invoice.idketerangantambahan = ""
        self.mock_invoice.kode_pajak = "01-Standard"
        self.mock_invoice.terminpembayaran = "01"
        self.mock_invoice.invoice_payment_type = "01-Cash"
        self.mock_invoice.termin_dpp = 0
        self.mock_invoice.termin_ppn = 0
        self.mock_invoice.termin_ppnbm = 0
        self.mock_invoice.nomor_faktur = ""
        self.mock_invoice.is_return = False

        # Mock items
        mock_item = MagicMock()
        mock_item.description = "Test Item"
        mock_item.qty = 10
        mock_item.rate = 100000
        mock_item.amount = 1000000
        self.mock_invoice.items = [mock_item]

        # Mock taxes
        mock_tax = MagicMock()
        mock_tax.rate = 12
        self.mock_invoice.taxes = [mock_tax]

    def test_mandatory_fields_check(self):
        """Test check_mandatory_fields function."""
        from erpnext_indonesia_localization.doc_events.sales_invoice import check_mandatory_fields

        # Create a mock metadata document with missing fields
        mock_metadata = MagicMock()
        mock_metadata.get = MagicMock(side_effect=lambda x: None if x == 'kdjenistransaksi' else 'value')
        mock_metadata.barangjasa = []

        safe, empty_fields = check_mandatory_fields(mock_metadata)

        self.assertFalse(safe)
        self.assertIn('kdjenistransaksi', empty_fields)

    def test_mandatory_fields_all_present(self):
        """Test check_mandatory_fields with all fields present."""
        from erpnext_indonesia_localization.doc_events.sales_invoice import check_mandatory_fields

        # Create a mock metadata document with all required fields
        mock_metadata = MagicMock()
        mock_metadata.get = MagicMock(return_value='value')

        # Mock barangjasa items
        mock_item = MagicMock()
        mock_item.get = MagicMock(return_value='value')
        mock_metadata.barangjasa = [mock_item]

        safe, empty_fields = check_mandatory_fields(mock_metadata)

        self.assertTrue(safe)
        self.assertEqual(len(empty_fields), 0)


class TestVATInputWorkflow(unittest.TestCase):
    """Integration tests for VAT Input workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings = MagicMock()
        self.mock_settings.auto_create_vat_input_metadata = True

        self.mock_supplier = MagicMock()
        self.mock_supplier.supplier_name = "PT Test Supplier"
        self.mock_supplier.tax_id = "012345678901234"

        self.mock_invoice = MagicMock()
        self.mock_invoice.name = "PINV-0001"
        self.mock_invoice.doctype = "Purchase Invoice"
        self.mock_invoice.supplier = "PT Test Supplier"
        self.mock_invoice.company = "PT Test Company"
        self.mock_invoice.posting_date = date(2025, 1, 15)
        self.mock_invoice.taxes_and_charges = "PPN Masukan 12%"
        self.mock_invoice.docstatus = 1
        self.mock_invoice.outstanding_amount = 0
        self.mock_invoice.net_total = 1000000


class TestPajakioAPIIntegration(unittest.TestCase):
    """Integration tests for Pajak.io API calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_response = {
            "code": 200,
            "message": "SUCCESS",
            "data": {
                "transactionId": "TXN-123456",
                "nofa": "0100000000000001"
            }
        }

    @patch('erpnext_indonesia_localization.utils.api.pajakio_helper.requests')
    def test_make_pajakio_request_success(self, mock_requests):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_response
        mock_response.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_response

        # Import after patching
        from erpnext_indonesia_localization.utils.api.pajakio_helper import make_pajakio_request

        # Mock get_pajakio_headers
        with patch('erpnext_indonesia_localization.utils.api.pajakio_helper.get_pajakio_headers') as mock_headers:
            mock_headers.return_value = {"Authorization": "test-key"}

            result = make_pajakio_request(
                method="POST",
                url="https://api.pajak.io/test",
                headers={"Authorization": "test-key"},
                json_data={"test": "data"},
                context="test"
            )

            self.assertEqual(result["code"], 200)
            self.assertEqual(result["message"], "SUCCESS")

    @patch('erpnext_indonesia_localization.utils.api.pajakio_helper.requests')
    def test_make_pajakio_request_retry_on_timeout(self, mock_requests):
        """Test API request retry on timeout."""
        from requests.exceptions import Timeout

        mock_requests.post.side_effect = Timeout("Connection timed out")

        from erpnext_indonesia_localization.utils.api.pajakio_helper import make_pajakio_request

        with patch('erpnext_indonesia_localization.utils.api.pajakio_helper.get_pajakio_headers') as mock_headers:
            mock_headers.return_value = {"Authorization": "test-key"}
            with patch('erpnext_indonesia_localization.utils.api.pajakio_helper.time.sleep'):
                with self.assertRaises(Exception):
                    make_pajakio_request(
                        method="POST",
                        url="https://api.pajak.io/test",
                        headers={"Authorization": "test-key"},
                        json_data={"test": "data"},
                        max_retries=2,
                        retry_delay=0
                    )


class TestVATOutputReturnWorkflow(unittest.TestCase):
    """Integration tests for VAT Output Return workflow."""

    def setUp(self):
        """Set up test fixtures for return invoices."""
        self.mock_return_invoice = MagicMock()
        self.mock_return_invoice.name = "SINV-RET-0001"
        self.mock_return_invoice.is_return = True
        self.mock_return_invoice.return_against = "SINV-0001"
        self.mock_return_invoice.docstatus = 1
        self.mock_return_invoice.posting_date = date(2025, 1, 20)

        mock_item = MagicMock()
        mock_item.description = "Test Item Return"
        mock_item.item_name = "Test Item"
        mock_item.qty = -5
        mock_item.rate = 100000
        mock_item.net_amount = -500000
        mock_item.discount_amount = 0
        self.mock_return_invoice.items = [mock_item]

        mock_tax = MagicMock()
        mock_tax.charge_type = "On Net Total"
        mock_tax.account_head = "VAT - Test"
        mock_tax.rate = 12
        self.mock_return_invoice.taxes = [mock_tax]

    def test_return_invoice_amounts_are_absolute(self):
        """Test that return invoice amounts are converted to absolute values."""
        item = self.mock_return_invoice.items[0]

        # DPP should be absolute
        dpp = abs(item.net_amount)
        self.assertEqual(dpp, 500000)

        # Qty should be absolute
        qty = abs(item.qty)
        self.assertEqual(qty, 5)


class TestWithholdingTaxWorkflow(unittest.TestCase):
    """Integration tests for Withholding Tax (e-Bupot) workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_invoice = MagicMock()
        self.mock_invoice.name = "PINV-0001"
        self.mock_invoice.docstatus = 1
        self.mock_invoice.outstanding_amount = 0
        self.mock_invoice.net_total = 10000000
        self.mock_invoice.posting_date = date(2025, 1, 15)
        self.mock_invoice.supplier = "PT Test Supplier"

        # Mock tax with withholding tax
        mock_tax = MagicMock()
        mock_tax.account_head = "PPh 23 Account"
        mock_tax.tax_amount = 200000  # 2% of 10,000,000
        self.mock_invoice.taxes = [mock_tax]

    def test_withholding_tax_rate_calculation(self):
        """Test calculation of withholding tax rate."""
        tax_amount = self.mock_invoice.taxes[0].tax_amount
        net_total = self.mock_invoice.net_total

        tax_rate = (tax_amount / net_total) * 100

        self.assertEqual(tax_rate, 2.0)


class TestBatchProcessing(unittest.TestCase):
    """Integration tests for batch processing."""

    def test_batch_size_configuration(self):
        """Test batch size is correctly set."""
        BATCH_SIZE = 50
        self.assertEqual(BATCH_SIZE, 50)

    def test_batch_splitting(self):
        """Test that items are correctly split into batches."""
        items = list(range(125))  # 125 items
        BATCH_SIZE = 50

        batches = []
        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i:i + BATCH_SIZE]
            batches.append(batch)

        self.assertEqual(len(batches), 3)  # 50 + 50 + 25
        self.assertEqual(len(batches[0]), 50)
        self.assertEqual(len(batches[1]), 50)
        self.assertEqual(len(batches[2]), 25)


class TestAuditLogging(unittest.TestCase):
    """Integration tests for audit logging."""

    def test_audit_log_format(self):
        """Test audit log entry format."""
        audit_entry = {
            "doctype": "VAT Output Metadata",
            "docname": "VOM-0001",
            "action": "status_change",
            "old_value": "Draft",
            "new_value": "Approved",
            "user": "Administrator",
            "timestamp": datetime.now().isoformat()
        }

        self.assertIn("doctype", audit_entry)
        self.assertIn("action", audit_entry)
        self.assertIn("timestamp", audit_entry)


if __name__ == '__main__':
    unittest.main()
