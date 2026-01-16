# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"fieldname": "certificate", "label": _("Certificate"), "fieldtype": "Link", "options": "Withholding Tax Certificate", "width": 150},
		{"fieldname": "purchase_invoice", "label": _("Purchase Invoice"), "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "transactionid", "label": _("Transaction ID"), "fieldtype": "Data", "width": 150},
		{"fieldname": "certificate_number", "label": _("Certificate Number"), "fieldtype": "Data", "width": 120},
		{"fieldname": "tax_type", "label": _("Tax Type"), "fieldtype": "Data", "width": 100},
		{"fieldname": "tax_amount", "label": _("Tax Amount"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "export_status", "label": _("Export Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "api_response", "label": _("API Response"), "fieldtype": "Small Text", "width": 200},
		{"fieldname": "modified", "label": _("Last Modified"), "fieldtype": "Datetime", "width": 150}
	]
	
	data = frappe.db.sql("""
		SELECT
			wtc.name as certificate,
			wtc.purchase_invoice,
			wtc.status,
			wtc.transactionid,
			wtc.certificate_number,
			wtc.tax_type,
			wtc.tax_amount,
			wtc.xml_export_status as export_status,
			wtc.create_vat_response as api_response,
			wtc.modified
		FROM
			`tabWithholding Tax Certificate` wtc
		WHERE
			wtc.docstatus = 0
		ORDER BY
			wtc.modified DESC
	""", as_dict=True)
	
	return columns, data
