# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{"fieldname": "type", "label": _("Type"), "fieldtype": "Data", "width": 120},
		{"fieldname": "uploaded", "label": _("Uploaded"), "fieldtype": "Int", "width": 100},
		{"fieldname": "pending_upload", "label": _("Pending Upload"), "fieldtype": "Int", "width": 120},
		{"fieldname": "pending_review", "label": _("Pending Review"), "fieldtype": "Int", "width": 120},
		{"fieldname": "rejected", "label": _("Rejected"), "fieldtype": "Int", "width": 100},
		{"fieldname": "total", "label": _("Total"), "fieldtype": "Int", "width": 100}
	]
	
	data = []
	
	# VAT Output Summary
	vom_data = frappe.db.sql("""
		SELECT
			COUNT(CASE WHEN vom.status = 'Approved' AND vom.vat_upload_success = 1 THEN 1 END) as uploaded,
			COUNT(CASE WHEN vom.status = 'Approved' AND vom.vat_upload_success = 0 AND vom.transactionid != '' THEN 1 END) as pending_upload,
			COUNT(CASE WHEN vom.status = 'To Be Reviewed' THEN 1 END) as pending_review,
			COUNT(CASE WHEN vom.status = 'Rejected' THEN 1 END) as rejected,
			COUNT(*) as total
		FROM
			`tabVAT Output Metadata` vom
		WHERE
			vom.docstatus = 0
	""", as_dict=True)
	
	if vom_data and vom_data[0]:
		data.append({
			"type": "VAT Output",
			"uploaded": vom_data[0].uploaded or 0,
			"pending_upload": vom_data[0].pending_upload or 0,
			"pending_review": vom_data[0].pending_review or 0,
			"rejected": vom_data[0].rejected or 0,
			"total": vom_data[0].total or 0
		})
	
	# VAT Input Summary
	vim_data = frappe.db.sql("""
		SELECT
			COUNT(CASE WHEN vim.status = 'Approved' AND vim.vat_upload_success = 1 THEN 1 END) as uploaded,
			COUNT(CASE WHEN vim.status = 'Approved' AND vim.vat_upload_success = 0 AND vim.transactionid != '' THEN 1 END) as pending_upload,
			COUNT(CASE WHEN vim.status = 'To Be Reviewed' THEN 1 END) as pending_review,
			COUNT(CASE WHEN vim.status = 'Rejected' THEN 1 END) as rejected,
			COUNT(*) as total
		FROM
			`tabVAT Input Metadata` vim
		WHERE
			vim.docstatus = 0
	""", as_dict=True)
	
	if vim_data and vim_data[0]:
		data.append({
			"type": "VAT Input",
			"uploaded": vim_data[0].uploaded or 0,
			"pending_upload": vim_data[0].pending_upload or 0,
			"pending_review": vim_data[0].pending_review or 0,
			"rejected": vim_data[0].rejected or 0,
			"total": vim_data[0].total or 0
		})
	
	# Withholding Tax Summary
	wtc_data = frappe.db.sql("""
		SELECT
			COUNT(CASE WHEN wtc.xml_export_status = 'Exported' THEN 1 END) as uploaded,
			COUNT(CASE WHEN wtc.status = 'Submitted' AND wtc.xml_export_status != 'Exported' AND wtc.transactionid != '' THEN 1 END) as pending_upload,
			COUNT(CASE WHEN wtc.status = 'Draft' THEN 1 END) as pending_review,
			0 as rejected,
			COUNT(*) as total
		FROM
			`tabWithholding Tax Certificate` wtc
		WHERE
			wtc.docstatus = 0
	""", as_dict=True)
	
	if wtc_data and wtc_data[0]:
		data.append({
			"type": "Withholding Tax",
			"uploaded": wtc_data[0].uploaded or 0,
			"pending_upload": wtc_data[0].pending_upload or 0,
			"pending_review": wtc_data[0].pending_review or 0,
			"rejected": 0,
			"total": wtc_data[0].total or 0
		})
	
	return columns, data
