# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from ..doctype.vat_input_metadata.vat_input_metadata import create_vat_input_metadata


def auto_create_vim_on_submit(doc, method):
	"""
	Auto-create VAT Input Metadata when Purchase Invoice is submitted.
	Similar to auto_create_vom_on_submit for Sales Invoice.
	"""
	try:
		indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
		
		# Check if auto-create is enabled (can reuse same setting or create new one)
		# For now, we'll check if the setting exists, if not, skip
		if not hasattr(indonesia_localization_settings, 'auto_create_vat_input_metadata'):
			# Setting doesn't exist yet, skip for now
			return
		
		if not indonesia_localization_settings.auto_create_vat_input_metadata:
			return
		
		# Only create for submitted invoices with taxes
		if doc.docstatus != 1:
			return
		
		if not doc.taxes_and_charges:
			return
		
		# Check if VAT Input Metadata already exists for this invoice
		existing_vim = frappe.db.exists("VAT Input Metadata", {"noinvoice": doc.name})
		if existing_vim:
			return
		
		# Create VAT Input Metadata
		success_status, message = create_vat_input_metadata(doc, indonesia_localization_settings)
		
		if not success_status:
			frappe.log_error(
				f"Failed to auto-create VAT Input Metadata for Purchase Invoice {doc.name}: {message}",
				"Auto Create VIM Error"
			)
		else:
			frappe.logger().info(f"Auto-created VAT Input Metadata for Purchase Invoice {doc.name}")
			
	except Exception as e:
		frappe.log_error(
			f"Error in auto_create_vim_on_submit for Purchase Invoice {doc.name}: {str(e)}",
			"Auto Create VIM Error"
		)


def validate_purchase_invoice_tax_data(doc, method):
	"""
	Validate tax data for Purchase Invoice.
	Similar to validate_tax_data_formats for Sales Invoice.
	"""
	errors = []
	
	# Validate supplier tax data if supplier exists
	if doc.supplier:
		supplier_doc = frappe.get_doc("Supplier", doc.supplier)
		
		# Validate NPWP format (15 digits) if supplier has tax_id
		if supplier_doc.tax_id:
			import re
			npwp_clean = re.sub(r'[.\-]', '', supplier_doc.tax_id)
			if not re.match(r'^\d{15}$', npwp_clean):
				errors.append(_("Supplier NPWP format is invalid. NPWP must be 15 digits. Current value: {0}").format(supplier_doc.tax_id))
	
	# Validate date consistency: tanggal faktur should not be before bill date
	if doc.custom_tanggal_faktur_pajak and doc.bill_date:
		if doc.custom_tanggal_faktur_pajak < doc.bill_date:
			errors.append(_("Tanggal Faktur Pajak ({0}) cannot be before Bill Date ({1})").format(
				doc.custom_tanggal_faktur_pajak, doc.bill_date
			))
	
	# Raise errors if any
	if errors:
		frappe.throw("<br>".join(errors), title=_("Data Validation Error"))


def auto_create_ebupot_on_payment(doc, method):
	"""
	Auto-create Withholding Tax Certificate when Purchase Invoice is paid.
	This function checks if there's withholding tax in the invoice and creates e-Bupot certificate.
	Triggered on on_update_after_submit when outstanding_amount becomes 0.
	"""
	try:
		# Only process if invoice is submitted
		if doc.docstatus != 1:
			return
		
		# Check if invoice is paid (outstanding amount is 0)
		if doc.outstanding_amount > 0:
			return
		
		# Check if Withholding Tax Certificate already exists
		existing_cert = frappe.db.exists("Withholding Tax Certificate", {"purchase_invoice": doc.name})
		if existing_cert:
			return
		
		# Check if there's withholding tax in the invoice
		has_withholding_tax = False
		withholding_tax_amount = 0
		withholding_tax_rate = 0
		
		for tax in doc.taxes:
			# Check if this is a withholding tax (PPh)
			if tax.account_head:
				account_doc = frappe.get_doc("Account", tax.account_head)
				# Check if account name contains withholding tax keywords
				account_name_lower = (account_doc.account_name or "").lower()
				if any(keyword in account_name_lower for keyword in ["pph", "withholding", "potong", "pajak penghasilan"]):
					has_withholding_tax = True
					withholding_tax_amount += tax.tax_amount or 0
		
		# If no withholding tax found, skip
		if not has_withholding_tax or withholding_tax_amount == 0:
			return
		
		# Get supplier information
		supplier_npwp = ""
		supplier_name = ""
		if doc.supplier:
			supplier_doc = frappe.get_doc("Supplier", doc.supplier)
			supplier_name = supplier_doc.supplier_name
			supplier_npwp = supplier_doc.tax_id or ""
		
		# Calculate tax rate (estimate from tax amount and base)
		if doc.net_total > 0:
			withholding_tax_rate = (withholding_tax_amount / doc.net_total) * 100
		
		# Determine tax type (default to PPh 23, can be improved with mapping)
		tax_type = "PPh 23"  # Default, can be enhanced with tax template mapping
		
		# Create Withholding Tax Certificate
		cert_doc = frappe.get_doc({
			"doctype": "Withholding Tax Certificate",
			"purchase_invoice": doc.name,
			"certificate_date": doc.posting_date,
			"supplier_npwp": supplier_npwp,
			"supplier_name": supplier_name,
			"tax_type": tax_type,
			"tax_rate": withholding_tax_rate,
			"tax_base": doc.net_total,
			"tax_amount": withholding_tax_amount,
			"status": "Draft"
		})
		
		cert_doc.insert(ignore_permissions=True)
		
		frappe.logger().info(f"Auto-created Withholding Tax Certificate {cert_doc.name} for Purchase Invoice {doc.name}")
		
	except Exception as e:
		frappe.log_error(
			f"Error in auto_create_ebupot_on_payment for Purchase Invoice {doc.name}: {str(e)}",
			"Auto Create e-Bupot Error"
		)
