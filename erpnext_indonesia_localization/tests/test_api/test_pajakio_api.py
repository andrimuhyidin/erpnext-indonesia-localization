# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
import unittest
from unittest.mock import patch, MagicMock
from erpnext_indonesia_localization.api.pajakio import (
	create_vat_output,
	get_vat_output_detail,
	get_pdf_vat_output,
	upload_vat_output
)


class TestPajakioAPI(unittest.TestCase):
	"""Test cases for Pajak.io API integration with mock responses"""
	
	def setUp(self):
		"""Set up test fixtures"""
		self.mock_doc = MagicMock()
		self.mock_doc.autouploaddjp = 0
		self.mock_doc.pengganti = 0
		self.mock_doc.nofa = "1234567890123"
		self.mock_doc.noinvoice = "SI-001"
		self.mock_doc.kdjenistransaksi = "01"
		self.mock_doc.idketerangantambahan = ""
		self.mock_doc.barangjasa = []
		self.mock_doc.npwp = "123456789012345"
		self.mock_doc.nikpassport = None
		self.mock_doc.customername = "Test Customer"
		self.mock_doc.alamatjalan = "Test Address"
		self.mock_doc.kota = "Jakarta"
		self.mock_doc.telp = "081234567890"
		self.mock_doc.tanggalfaktur = "2025-01-01"
		self.mock_doc.masapajak = "01"
		self.mock_doc.tahunpajak = "2025"
		self.mock_doc.tarifppn = 11
		self.mock_doc.terminpembayaran = "0"
		self.mock_doc.termindpp = None
		self.mock_doc.terminppn = None
		self.mock_doc.terminppnbm = None
	
	@patch('erpnext_indonesia_localization.api.pajakio.requests.post')
	@patch('frappe.get_single')
	def test_create_vat_output_success(self, mock_get_single, mock_post):
		"""Test successful VAT output creation"""
		# Mock settings
		mock_settings = MagicMock()
		mock_settings.get_password.return_value = "test_api_key"
		mock_settings.url_create_vat = "https://api.pajak.io/vat"
		mock_get_single.return_value = mock_settings
		
		# Mock successful response
		mock_response = MagicMock()
		mock_response.json.return_value = {"code": 200, "message": "Success", "data": {"transactionId": "123"}}
		mock_response.raise_for_status = MagicMock()
		mock_post.return_value = mock_response
		
		result = create_vat_output(self.mock_doc)
		
		self.assertEqual(result["code"], 200)
		mock_post.assert_called_once()
	
	@patch('erpnext_indonesia_localization.api.pajakio.requests.post')
	@patch('frappe.get_single')
	def test_create_vat_output_timeout(self, mock_get_single, mock_post):
		"""Test timeout handling in VAT output creation"""
		from requests.exceptions import Timeout
		
		# Mock settings
		mock_settings = MagicMock()
		mock_settings.get_password.return_value = "test_api_key"
		mock_settings.url_create_vat = "https://api.pajak.io/vat"
		mock_get_single.return_value = mock_settings
		
		# Mock timeout exception
		mock_post.side_effect = Timeout("Request timeout")
		
		with self.assertRaises(frappe.ValidationError):
			create_vat_output(self.mock_doc)
	
	@patch('erpnext_indonesia_localization.api.pajakio.requests.get')
	@patch('frappe.get_single')
	def test_get_vat_output_detail_success(self, mock_get_single, mock_get):
		"""Test successful VAT output detail retrieval"""
		# Mock settings
		mock_settings = MagicMock()
		mock_settings.get_password.return_value = "test_api_key"
		mock_settings.url_get_vat = "https://api.pajak.io/vat/"
		mock_get_single.return_value = mock_settings
		
		# Mock document
		mock_doc = MagicMock()
		mock_doc.transactionid = "123"
		
		# Mock successful response
		mock_response = MagicMock()
		mock_response.json.return_value = {"code": 200, "data": [{"nofa": "1234567890123"}]}
		mock_response.raise_for_status = MagicMock()
		mock_get.return_value = mock_response
		
		result = get_vat_output_detail(mock_doc)
		
		self.assertEqual(result["code"], 200)
		mock_get.assert_called_once()
	
	@patch('erpnext_indonesia_localization.api.pajakio.requests.post')
	@patch('frappe.get_single')
	def test_upload_vat_output_success(self, mock_get_single, mock_post):
		"""Test successful VAT output upload"""
		# Mock settings
		mock_settings = MagicMock()
		mock_settings.get_password.return_value = "test_api_key"
		mock_settings.url_upload_vat = "https://api.pajak.io/vat/upload"
		mock_get_single.return_value = mock_settings
		
		# Mock document
		mock_doc = MagicMock()
		mock_doc.transactionid = "123"
		mock_doc.name = "VOM-001"
		
		# Mock successful response
		mock_response = MagicMock()
		mock_response.json.return_value = {"code": 200, "message": "Success"}
		mock_response.raise_for_status = MagicMock()
		mock_post.return_value = mock_response
		
		with patch('frappe.get_doc', return_value=mock_doc):
			result = upload_vat_output(mock_doc.name)
			
			self.assertEqual(result["code"], 200)
			mock_post.assert_called_once()


if __name__ == '__main__':
	unittest.main()
