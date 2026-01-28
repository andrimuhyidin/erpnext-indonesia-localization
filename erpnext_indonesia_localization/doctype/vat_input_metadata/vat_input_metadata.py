# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VATInputMetadata(Document):
	"""
	VAT Input Metadata for tracking purchase invoice VAT.
	
	Stores metadata about VAT input documents from purchase
	invoices for crediting against VAT output obligations.
	"""

	pass


@frappe.whitelist()
def create_vat_input_metadata(doc, indonesia_localization_settings=None):
	"""
	Create VAT Input Metadata from Purchase Invoice.
	Similar to create_vat_output_metadata but for Purchase Invoice.
	"""
	if not indonesia_localization_settings:
		indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
	
	metadata_doc = frappe.new_doc('VAT Input Metadata')
	METADATA_DRAFT_STATUS = 'To Be Reviewed'
	supplier_details = frappe.get_doc("Supplier", doc.supplier)
	
	if not supplier_details.supplier_primary_address:
		message = f"Please complete primary address for {supplier_details.supplier_name}"
		return False, message
	supplier_address = frappe.get_doc("Address", supplier_details.supplier_primary_address)
	
	if not supplier_details.mobile_no:
		message = f"Please complete primary contact number for {supplier_details.supplier_name}"
		return False, message
	
	metadata_doc.noinvoice = doc.name
	metadata_doc.parent_doctype = doc.doctype
	
	# Get transaction code from Purchase Invoice or Taxes Template
	if hasattr(doc, 'transaction_code') and doc.transaction_code:
		metadata_doc.kdjenistransaksi = doc.transaction_code.strip()
	else:
		# Try to get from taxes template
		if doc.taxes_and_charges:
			tax_template = frappe.db.get_value(
				"Purchase Taxes and Charges Template",
				doc.taxes_and_charges,
				'transaction_code',
				as_dict=True
			)
			if tax_template and tax_template.transaction_code:
				metadata_doc.kdjenistransaksi = tax_template.transaction_code.strip()
	
	if hasattr(doc, 'idketerangantambahan') and doc.idketerangantambahan:
		metadata_doc.idketerangantambahan = doc.idketerangantambahan.strip()
	
	# Set dates
	metadata_doc.tanggalfaktur = frappe.utils.formatdate(doc.bill_date or frappe.utils.today(), "YYYY-mm-dd")
	metadata_doc.masapajak = frappe.utils.formatdate(frappe.utils.today(), "mm").strip()
	metadata_doc.tahunpajak = frappe.utils.formatdate(frappe.utils.today(), "yyyy").strip()
	
	# Calculate tax rate
	tariff = 0
	if doc.taxes:
		for tax in doc.taxes:
			tariff += tax.rate if tax.rate else 0
	
	metadata_doc.tarifppn = tariff
	
	# Set supplier information
	if supplier_details.tax_id:
		metadata_doc.npwp = supplier_details.tax_id.replace('.', '')
	metadata_doc.nikpassport = None
	metadata_doc.nama = doc.supplier
	metadata_doc.alamatjalan = supplier_address.address_line1 or ""
	metadata_doc.kota = supplier_address.city or ""
	metadata_doc.telp = supplier_details.mobile_no or ""
	
	# Add items
	from frappe.utils import cint
	for item in doc.items:
		metadata_doc.append('barangjasa', {
			"nama": item.description or item.item_name,
			"jumlah": item.qty,
			"harga": item.rate,
			"dpp": item.net_amount,
			"ppn": (item.net_amount * (tariff / 100)) if tariff > 0 else 0,
			"tarifppnbm": 0,
			"diskon": item.discount_amount or 0,
			"kode": ""
		})
	
	metadata_doc.status = METADATA_DRAFT_STATUS
	metadata_doc.save()
	
	message = "Successfully Created VAT Input Metadata"
	return True, message
