# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
import unittest
from unittest.mock import patch, MagicMock
from erpnext_indonesia_localization.doctype.vat_input_metadata.vat_input_metadata import (
	create_vat_input_metadata
)
from erpnext_indonesia_localization.doc_events.purchase_invoice import (
	auto_create_vim_on_submit,
	validate_purchase_invoice_tax_data
)


class TestVATInput(unittest.TestCase):
	"""Test cases for VAT Input (PPN Masukan) functionality"""
	
	def setUp(self):
		"""Set up test fixtures"""
		pass
	
	@patch('frappe.get_single')
	@patch('frappe.get_doc')
	@patch('frappe.new_doc')
	def test_create_vat_input_metadata(self, mock_new_doc, mock_get_doc, mock_get_single):
		"""Test creation of VAT Input Metadata from Purchase Invoice"""
		# Mock settings
		mock_settings = MagicMock()
		mock_get_single.return_value = mock_settings
		
		# Mock Purchase Invoice
		mock_pi = MagicMock()
		mock_pi.name = "PI-001"
		mock_pi.doctype = "Purchase Invoice"
		mock_pi.supplier = "SUP-001"
		mock_pi.bill_date = "2025-01-01"
		mock_pi.taxes_and_charges = "Tax Template"
		mock_pi.taxes = []
		mock_pi.items = []
		
		# Mock Supplier
		mock_supplier = MagicMock()
		mock_supplier.supplier_name = "Test Supplier"
		mock_supplier.supplier_primary_address = "ADDR-001"
		mock_supplier.mobile_no = "081234567890"
		mock_supplier.tax_id = "123456789012345"
		
		# Mock Address
		mock_address = MagicMock()
		mock_address.address_line1 = "Test Address"
		mock_address.city = "Jakarta"
		
		mock_get_doc.side_effect = lambda doctype, name: {
			"Supplier": mock_supplier,
			"Address": mock_address
		}.get(doctype, MagicMock())
		
		# Mock new doc
		mock_vim = MagicMock()
		mock_new_doc.return_value = mock_vim
		
		# Test
		success, message = create_vat_input_metadata(mock_pi, mock_settings)
		
		# Assertions
		self.assertTrue(success)
		mock_new_doc.assert_called_once_with('VAT Input Metadata')
		mock_vim.save.assert_called_once()
	
	def test_validate_purchase_invoice_tax_data(self):
		"""Test validation of Purchase Invoice tax data"""
		# Placeholder for validation tests
		# This would require creating actual Purchase Invoice documents
		pass
	
	def test_auto_create_vim_on_submit(self):
		"""Test auto-creation of VAT Input Metadata on Purchase Invoice submit"""
		# Placeholder for auto-create tests
		# This would require creating actual Purchase Invoice documents and submitting them
		pass


if __name__ == '__main__':
	unittest.main()
