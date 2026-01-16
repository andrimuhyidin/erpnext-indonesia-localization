# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"fieldname": "vat_input", "label": _("VAT Input"), "fieldtype": "Link", "options": "VAT Input Metadata", "width": 150},
		{"fieldname": "purchase_invoice", "label": _("Purchase Invoice"), "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
		{"fieldname": "transactionid", "label": _("Transaction ID"), "fieldtype": "Data", "width": 150},
		{"fieldname": "nofa", "label": _("No Faktur"), "fieldtype": "Data", "width": 120},
		{"fieldname": "api_response", "label": _("API Response"), "fieldtype": "Small Text", "width": 200},
		{"fieldname": "upload_success", "label": _("Upload Success"), "fieldtype": "Check", "width": 100},
		{"fieldname": "modified", "label": _("Last Modified"), "fieldtype": "Datetime", "width": 150}
	]
	
	data = frappe.db.sql("""
		SELECT
			vim.name as vat_input,
			vim.noinvoice as purchase_invoice,
			vim.status,
			vim.transactionid,
			vim.nofa,
			vim.create_vat_response as api_response,
			vim.vat_upload_success as upload_success,
			vim.modified
		FROM
			`tabVAT Input Metadata` vim
		WHERE
			vim.docstatus = 0
		ORDER BY
			vim.modified DESC
	""", as_dict=True)
	
	return columns, data
