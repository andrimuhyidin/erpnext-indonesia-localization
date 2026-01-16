# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"fieldname": "vat_output", "label": _("VAT Output"), "fieldtype": "Link", "options": "VAT Output Metadata", "width": 150},
		{"fieldname": "sales_invoice", "label": _("Sales Invoice"), "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "transactionid", "label": _("Transaction ID"), "fieldtype": "Data", "width": 150},
		{"fieldname": "nofa", "label": _("No Faktur"), "fieldtype": "Data", "width": 120},
		{"fieldname": "api_response", "label": _("API Response"), "fieldtype": "Small Text", "width": 200},
		{"fieldname": "upload_success", "label": _("Upload Success"), "fieldtype": "Check", "width": 100},
		{"fieldname": "modified", "label": _("Last Modified"), "fieldtype": "Datetime", "width": 150}
	]
	
	data = frappe.db.sql("""
		SELECT
			vom.name as vat_output,
			vom.noinvoice as sales_invoice,
			vom.status,
			vom.transactionid,
			vom.nofa,
			vom.create_vat_response as api_response,
			vom.vat_upload_success as upload_success,
			vom.modified
		FROM
			`tabVAT Output Metadata` vom
		WHERE
			vom.docstatus = 0
		ORDER BY
			vom.modified DESC
	""", as_dict=True)
	
	return columns, data
