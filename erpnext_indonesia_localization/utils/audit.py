# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now


def log_tax_data_change(doctype, docname, field, old_value, new_value, action="Changed"):
	"""
	Log changes to important tax data fields
	
	Args:
		doctype: Document type (e.g., "VAT Output Metadata", "Sales Invoice")
		docname: Document name
		field: Field name that changed
		old_value: Old value
		new_value: New value
		action: Action type (Changed, Approved, Rejected, etc.)
	"""
	try:
		audit_log = frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Info",
			"reference_doctype": doctype,
			"reference_name": docname,
			"content": f"[Tax Audit] {action}: {field} changed from '{old_value}' to '{new_value}' by {frappe.session.user}",
			"comment_by": frappe.session.user
		})
		audit_log.insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Error logging tax data change: {str(e)}", "Tax Audit Logging Error")


def log_vat_output_status_change(doc, method):
	"""
	Hook to log VAT Output Metadata status changes
	"""
	if doc.has_value_changed("status"):
		old_status = doc.get_doc_before_save().status if doc.get_doc_before_save() else None
		log_tax_data_change(
			"VAT Output Metadata",
			doc.name,
			"status",
			old_status,
			doc.status,
			action="Status Changed"
		)


def log_vat_output_approval(doc, method):
	"""
	Log when VAT Output is approved
	"""
	if doc.status == "Approved" and doc.has_value_changed("status"):
		log_tax_data_change(
			"VAT Output Metadata",
			doc.name,
			"status",
			doc.get_doc_before_save().status if doc.get_doc_before_save() else None,
			"Approved",
			action="Approved"
		)


def log_vat_output_rejection(doc, method):
	"""
	Log when VAT Output is rejected
	"""
	if doc.status == "Rejected" and doc.has_value_changed("status"):
		log_tax_data_change(
			"VAT Output Metadata",
			doc.name,
			"status",
			doc.get_doc_before_save().status if doc.get_doc_before_save() else None,
			"Rejected",
			action="Rejected"
		)


def log_tax_invoice_number_link(doc, method):
	"""
	Log when Tax Invoice Number is linked to Sales Invoice
	"""
	if doc.has_value_changed("tax_invoice_number"):
		old_tin = doc.get_doc_before_save().tax_invoice_number if doc.get_doc_before_save() else None
		log_tax_data_change(
			"Sales Invoice",
			doc.name,
			"tax_invoice_number",
			old_tin,
			doc.tax_invoice_number,
			action="Tax Invoice Number Linked"
		)


def log_nofa_assignment(doc, method):
	"""
	Log when NOFA is assigned to VAT Output Metadata
	"""
	if doc.has_value_changed("nofa") and doc.nofa:
		old_nofa = doc.get_doc_before_save().nofa if doc.get_doc_before_save() else None
		log_tax_data_change(
			"VAT Output Metadata",
			doc.name,
			"nofa",
			old_nofa,
			doc.nofa,
			action="NOFA Assigned"
		)


def get_audit_trail(doctype, docname):
	"""
	Get audit trail for a document
	
	Returns:
		List of audit log entries
	"""
	comments = frappe.get_all(
		"Comment",
		filters={
			"reference_doctype": doctype,
			"reference_name": docname,
			"comment_type": "Info",
			"content": ["like", "%[Tax Audit]%"]
		},
		fields=["content", "comment_by", "creation"],
		order_by="creation DESC"
	)
	return comments
