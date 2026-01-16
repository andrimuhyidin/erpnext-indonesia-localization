# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import re
from typing import Dict, List, Any


def validate_coretax_data(invoice_doc: Dict[str, Any], company_doc: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Validate CoreTax data for a single invoice.
	
	Args:
		invoice_doc: Dictionary containing invoice data
		company_doc: Dictionary containing company data
		
	Returns:
		Dictionary with validation result:
		{
			"is_valid": bool,
			"errors": List[str],
			"warnings": List[str]
		}
	"""
	errors = []
	warnings = []
	
	# Validate NPWP format (15 digits)
	if company_doc.get("tax_id"):
		npwp_clean = re.sub(r'[.\-]', '', str(company_doc["tax_id"]))
		if not re.match(r'^\d{15}$', npwp_clean):
			errors.append(_("Company NPWP format is invalid. NPWP must be 15 digits. Current value: {0}").format(company_doc["tax_id"]))
	
	# Validate NITKU format (3 digits) if exists
	if company_doc.get("companys_nitku"):
		nitku_clean = re.sub(r'[.\-]', '', str(company_doc["companys_nitku"]))
		if not re.match(r'^\d{3}$', nitku_clean):
			errors.append(_("Company NITKU format is invalid. NITKU must be 3 digits. Current value: {0}").format(company_doc["companys_nitku"]))
	
	# Get customer info for validation
	customer = invoice_doc.get("customer")
	if customer:
		customer_info = frappe.get_value("Customer", customer, 
			["tax_id", "customer_id_type", "customer_id_number", "nik", "customers_nitku", "tax_country_code"],
			as_dict=True
		)
		
		if customer_info:
			# Validate customer NPWP if exists
			if customer_info.get("tax_id"):
				npwp_clean = re.sub(r'[.\-]', '', str(customer_info["tax_id"]))
				if not re.match(r'^\d{15}$', npwp_clean):
					errors.append(_("Customer NPWP format is invalid. NPWP must be 15 digits. Customer: {0}, Value: {1}").format(
						customer, customer_info["tax_id"]
					))
			
			# Validate NIK format (16 digits) if customer_id_type is "National ID"
			if customer_info.get("customer_id_type") == "National ID":
				if customer_info.get("nik"):
					nik_clean = re.sub(r'[.\-]', '', str(customer_info["nik"]))
					if not re.match(r'^\d{16}$', nik_clean):
						errors.append(_("Customer NIK format is invalid. NIK must be 16 digits. Customer: {0}, Value: {1}").format(
							customer, customer_info["nik"]
						))
				elif customer_info.get("customer_id_number"):
					nik_clean = re.sub(r'[.\-]', '', str(customer_info["customer_id_number"]))
					if not re.match(r'^\d{16}$', nik_clean):
						errors.append(_("Customer NIK format is invalid. NIK must be 16 digits. Customer: {0}, Value: {1}").format(
							customer, customer_info["customer_id_number"]
						))
			
			# Validate customer NITKU format (3 digits) if exists
			if customer_info.get("customers_nitku"):
				nitku_clean = re.sub(r'[.\-]', '', str(customer_info["customers_nitku"]))
				if not re.match(r'^\d{3}$', nitku_clean):
					errors.append(_("Customer NITKU format is invalid. NITKU must be 3 digits. Customer: {0}, Value: {1}").format(
						customer, customer_info["customers_nitku"]
					))
	
	# Validate kode transaksi (01-09 sesuai standar)
	transaction_code = invoice_doc.get("transaction_code")
	if transaction_code:
		if not re.match(r'^0[1-9]$', str(transaction_code)):
			errors.append(_("Transaction Code is invalid. Must be between 01-09. Invoice: {0}, Value: {1}").format(
				invoice_doc.get("name", ""), transaction_code
			))
	else:
		warnings.append(_("Transaction Code is missing. Invoice: {0}").format(invoice_doc.get("name", "")))
	
	# Validate kode objek pajak (check against master data if available)
	# This is a placeholder - actual validation would check against CoreTax Barang Jasa Ref
	# For now, we'll just check if it exists
	items = invoice_doc.get("items", [])
	for item in items:
		if item.get("kode_barang_jasa_ref"):
			# Check if kode exists in master data
			exists = frappe.db.exists("CoreTax Barang Jasa Ref", item["kode_barang_jasa_ref"])
			if not exists:
				warnings.append(_("Barang Jasa Code not found in master data. Invoice: {0}, Item: {1}, Code: {2}").format(
					invoice_doc.get("name", ""), item.get("item_name", ""), item["kode_barang_jasa_ref"]
				))
	
	# Validate tax rate (should be standard rates: 0, 1.1, 11, 12, etc.)
	# This validation is optional and can be enhanced based on business rules
	
	# Validate tanggal faktur consistency
	posting_date = invoice_doc.get("posting_date")
	if posting_date:
		# Check if posting date is reasonable (not too far in past/future)
		from frappe.utils import today, add_days
		if posting_date > today():
			warnings.append(_("Posting date is in the future. Invoice: {0}, Date: {1}").format(
				invoice_doc.get("name", ""), posting_date
			))
	
	return {
		"is_valid": len(errors) == 0,
		"errors": errors,
		"warnings": warnings
	}


def validate_before_export(invoice_docs: List[Dict[str, Any]], company_doc: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Batch validation for multiple invoices before export.
	
	Args:
		invoice_docs: List of invoice dictionaries
		company_doc: Dictionary containing company data
		
	Returns:
		Dictionary with validation summary:
		{
			"total": int,
			"valid": int,
			"invalid": int,
			"results": List[Dict] - each with invoice name, is_valid, errors, warnings
		}
	"""
	results = []
	valid_count = 0
	invalid_count = 0
	
	for invoice in invoice_docs:
		# Get full invoice document for validation
		invoice_name = invoice.get("name")
		if not invoice_name:
			continue
		
		# Get full invoice data including items
		full_invoice = frappe.get_doc("Sales Invoice", invoice_name)
		invoice_dict = full_invoice.as_dict()
		
		# Get items for validation
		items = frappe.get_all(
			"Sales Invoice Item",
			filters={"parent": invoice_name},
			fields=["item_name", "kode_barang_jasa_ref", "kode_barang_jasa_opt"]
		)
		invoice_dict["items"] = items
		
		# Validate
		validation_result = validate_coretax_data(invoice_dict, company_doc)
		
		results.append({
			"invoice_name": invoice_name,
			"is_valid": validation_result["is_valid"],
			"errors": validation_result["errors"],
			"warnings": validation_result["warnings"]
		})
		
		if validation_result["is_valid"]:
			valid_count += 1
		else:
			invalid_count += 1
	
	return {
		"total": len(invoice_docs),
		"valid": valid_count,
		"invalid": invalid_count,
		"results": results
	}


@frappe.whitelist()
def validate_single_invoice(invoice_name: str) -> Dict[str, Any]:
	"""
	Validate a single invoice by name.
	Useful for client-side validation.
	
	Args:
		invoice_name: Name of the Sales Invoice
		
	Returns:
		Validation result dictionary
	"""
	if not invoice_name:
		return {
			"is_valid": False,
			"errors": [_("Invoice name is required")],
			"warnings": []
		}
	
	try:
		invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
		company_doc = frappe.get_value("Company", invoice_doc.company, 
			["tax_id", "companys_nitku", "company_name"], as_dict=True)
		
		invoice_dict = invoice_doc.as_dict()
		items = frappe.get_all(
			"Sales Invoice Item",
			filters={"parent": invoice_name},
			fields=["item_name", "kode_barang_jasa_ref", "kode_barang_jasa_opt"]
		)
		invoice_dict["items"] = items
		
		return validate_coretax_data(invoice_dict, company_doc)
	except Exception as e:
		frappe.log_error(f"Error validating invoice {invoice_name}: {str(e)}", "CoreTax Validation Error")
		return {
			"is_valid": False,
			"errors": [_("Error during validation: {0}").format(str(e))],
			"warnings": []
		}
