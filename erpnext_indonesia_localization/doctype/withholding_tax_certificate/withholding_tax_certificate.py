# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class WithholdingTaxCertificate(Document):
	"""
	Withholding Tax Certificate (Bukti Potong) for Indonesian tax compliance.
	
	Manages withholding tax certificates (e-Bupot) issued for Article 21/22/23/26
	income tax withheld from payments to suppliers or employees.
	"""

	def validate(self):
		# Validate NPWP format
		if self.supplier_npwp:
			npwp_clean = re.sub(r'[.\-]', '', str(self.supplier_npwp))
			if not re.match(r'^\d{15}$', npwp_clean):
				frappe.throw(_("Supplier NPWP format is invalid. NPWP must be 15 digits. Current value: {0}").format(self.supplier_npwp))
		
		# Auto-calculate tax amount
		self.calculate_tax_amount()
	
	def calculate_tax_amount(self):
		"""Calculate tax amount from tax base and tax rate"""
		if self.tax_base and self.tax_rate:
			self.tax_amount = (self.tax_base * self.tax_rate) / 100
		else:
			self.tax_amount = 0
	
	@frappe.whitelist()
	def load_from_purchase_invoice(self):
		"""Load supplier information from Purchase Invoice"""
		try:
			pi_doc = frappe.get_doc("Purchase Invoice", self.purchase_invoice)
			
			# Get supplier info
			if pi_doc.supplier:
				supplier_doc = frappe.get_doc("Supplier", pi_doc.supplier)
				self.supplier_name = supplier_doc.supplier_name
				if supplier_doc.tax_id:
					self.supplier_npwp = supplier_doc.tax_id
			
			# Set certificate date to posting date if not set
			if not self.certificate_date:
				self.certificate_date = pi_doc.posting_date
			
			# Calculate tax base from invoice
			if not self.tax_base:
				# Get withholding tax amount from invoice taxes
				withholding_tax = 0
				for tax in pi_doc.taxes:
					if tax.account_head and "withholding" in tax.account_head.lower():
						withholding_tax += tax.tax_amount or 0
				
				if withholding_tax > 0:
					self.tax_base = pi_doc.net_total
					# Estimate tax rate (can be improved with actual tax template)
					if self.tax_base > 0:
						self.tax_rate = (withholding_tax / self.tax_base) * 100
					self.tax_amount = withholding_tax
		except Exception as e:
			frappe.log_error(f"Error loading from Purchase Invoice: {str(e)}", "Withholding Tax Certificate Error")
	
	@frappe.whitelist()
	def export_to_ebupot_xml(self):
		"""Export certificate to e-Bupot XML format (Legacy method - kept for backward compatibility)"""
		from erpnext_indonesia_localization.utils.export.ebupot_xml_exporter import generate_ebupot_xml
		
		try:
			xml_file = generate_ebupot_xml(self)
			self.xml_file = xml_file
			self.xml_export_status = "Exported"
			self.save()
			frappe.msgprint(_("e-Bupot XML exported successfully"))
			return xml_file
		except Exception as e:
			self.xml_export_status = "Failed"
			self.save()
			frappe.log_error(f"Error exporting e-Bupot XML: {str(e)}", "e-Bupot Export Error")
			frappe.throw(_("Error exporting e-Bupot XML: {0}").format(str(e)))
	
	@frappe.whitelist()
	def call_pajakio_api(self):
		"""Create Withholding Tax via Pajak.io API"""
		from erpnext_indonesia_localization.api import create_withholding_tax
		
		try:
			response = create_withholding_tax(self)
			if response.get('code') in [200, 201]:
				frappe.msgprint(_("Withholding Tax created successfully via Pajak.io API"))
				return response
			else:
				frappe.throw(_("Failed to create Withholding Tax: {0}").format(response.get('message', 'Unknown error')))
		except Exception as e:
			frappe.log_error(f"Error calling Pajak.io API for Withholding Tax {self.name}: {str(e)}", "Pajak.io API Error")
			raise
	
	@frappe.whitelist()
	def sync_status_from_pajakio(self):
		"""Sync status from Pajak.io API"""
		from erpnext_indonesia_localization.api import get_status_bupot
		
		if not self.transactionid:
			frappe.throw(_("Transaction ID is required to sync status"))
		
		try:
			response = get_status_bupot(self.transactionid)
			if response.get('code') == 200 and 'data' in response:
				status_data = response['data']
				if isinstance(status_data, list) and len(status_data) > 0:
					status_data = status_data[0]
				
				if isinstance(status_data, dict):
					if 'status' in status_data:
						self.status = status_data['status']
					self.create_vat_response = response.get('message', 'Status synced successfully')
					self.save()
					frappe.msgprint(_("Status synced successfully from Pajak.io"))
					return response
		except Exception as e:
			frappe.log_error(f"Error syncing status for Withholding Tax {self.name}: {str(e)}", "Pajak.io API Error")
			raise
	
	@frappe.whitelist()
	def get_code_of_type(self):
		"""Get master data for kode objek pajak from Pajak.io API"""
		from erpnext_indonesia_localization.api import get_code_of_type
		
		try:
			response = get_code_of_type()
			return response
		except Exception as e:
			frappe.log_error(f"Error getting code of type: {str(e)}", "Pajak.io API Error")
			raise