# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class VATOutputReturn(Document):
	def validate(self):
		"""Validate VAT Output Return document"""
		errors = []
		
		# Validate required fields
		if not self.npwp and not self.nikpassport:
			errors.append(_("NPWP or NIK/Passport is required"))
		
		if not self.nama:
			errors.append(_("Nama (Name) is required"))
		
		if not self.alamatjalan:
			errors.append(_("Alamat Jalan (Address) is required"))
		
		if not self.tanggalfaktur:
			errors.append(_("Tanggal Faktur (Invoice Date) is required"))
		
		if not self.masapajak:
			errors.append(_("Masa Pajak (Tax Period) is required"))
		
		if not self.tahunpajak:
			errors.append(_("Tahun Pajak (Tax Year) is required"))
		
		# Validate NPWP format (15 digits)
		if self.npwp:
			npwp_clean = re.sub(r'[.\-]', '', str(self.npwp))
			if not re.match(r'^\d{15}$', npwp_clean):
				errors.append(_("NPWP format is invalid. NPWP must be 15 digits. Current value: {0}").format(self.npwp))
		
		# Validate NIK format (16 digits) if NPWP not provided
		if not self.npwp and self.nikpassport:
			nik_clean = re.sub(r'[.\-]', '', str(self.nikpassport))
			if not re.match(r'^\d{16}$', nik_clean):
				errors.append(_("NIK format is invalid. NIK must be 16 digits. Current value: {0}").format(self.nikpassport))
		
		# Validate barangjasa items
		if not self.barangjasa or len(self.barangjasa) == 0:
			errors.append(_("At least one Barang/Jasa item is required"))
		else:
			for idx, item in enumerate(self.barangjasa, 1):
				if not item.nama:
					errors.append(_("Item {0}: Nama (Name) is required").format(idx))
				if not item.jumlah or item.jumlah == 0:
					errors.append(_("Item {0}: Jumlah (Quantity) must be greater than 0").format(idx))
				if not item.harga or item.harga == 0:
					errors.append(_("Item {0}: Harga (Price) must be greater than 0").format(idx))
				if not item.dpp or item.dpp == 0:
					errors.append(_("Item {0}: DPP (Tax Base) must be greater than 0").format(idx))
				# For returns, amounts can be negative
				if item.ppn and abs(item.ppn) > abs(item.dpp):
					errors.append(_("Item {0}: PPN cannot be greater than DPP in absolute value").format(idx))
		
		# Validate date consistency
		if self.tanggalfaktur and self.masapajak and self.tahunpajak:
			try:
				from frappe.utils import getdate
				from datetime import datetime
				
				invoice_date = getdate(self.tanggalfaktur)
				month = int(self.masapajak)
				year = int(self.tahunpajak)
				
				if invoice_date.month != month:
					errors.append(_("Tanggal Faktur month ({0}) does not match Masa Pajak ({1})").format(
						invoice_date.month, month
					))
				
				if invoice_date.year != year:
					errors.append(_("Tanggal Faktur year ({0}) does not match Tahun Pajak ({1})").format(
						invoice_date.year, year
					))
			except (ValueError, AttributeError) as e:
				errors.append(_("Invalid date format: {0}").format(str(e)))
		
		# Validate original VAT Output if exists
		if self.original_vat_output:
			try:
				original_vom = frappe.get_doc("VAT Output Metadata", self.original_vat_output)
				if not original_vom.transactionid:
					errors.append(_("Original VAT Output Metadata must have a Transaction ID"))
			except frappe.DoesNotExistError:
				errors.append(_("Original VAT Output Metadata not found: {0}").format(self.original_vat_output))
		
		# Raise errors if any
		if errors:
			frappe.throw("<br>".join(errors), title=_("Validation Error"))
