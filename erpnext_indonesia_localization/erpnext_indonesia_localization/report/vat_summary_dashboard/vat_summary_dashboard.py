# Copyright (c) 2026, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary

def get_columns():
	return [
		{"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
		{"label": _("VAT Output (Keluaran)"), "fieldname": "vat_output", "fieldtype": "Currency", "width": 180},
		{"label": _("VAT Input (Masukan)"), "fieldname": "vat_input", "fieldtype": "Currency", "width": 180},
		{"label": _("Net Tax Payable"), "fieldname": "net_payable", "fieldtype": "Currency", "width": 180}
	]

def get_data(filters):
	company = filters.get("company")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	# Fetch Sales Invoices (VAT Output)
	si_data = frappe.db.get_all("Sales Invoice",
		filters={"docstatus": 1, "company": company, "posting_date": ["between", [from_date, to_date]]},
		fields=["SUM(total_taxes_and_charges) as total_tax", "MONTHNAME(posting_date) as month", "MONTH(posting_date) as month_num"],
		group_by="month",
		order_by="month_num asc"
	)

	# Fetch Purchase Invoices (VAT Input)
	pi_data = frappe.db.get_all("Purchase Invoice",
		filters={"docstatus": 1, "company": company, "bill_date": ["between", [from_date, to_date]]},
		fields=["SUM(total_taxes_and_charges) as total_tax", "MONTHNAME(bill_date) as month", "MONTH(bill_date) as month_num"],
		group_by="month",
		order_by="month_num asc"
	)

	# Merge data
	months = sorted(list(set([d.month for d in si_data] + [d.month for d in pi_data])))
	data = []
	for month in months:
		vat_output = next((d.total_tax for d in si_data if d.month == month), 0)
		vat_input = next((d.total_tax for d in pi_data if d.month == month), 0)
		data.append({
			"month": month,
			"vat_output": vat_output,
			"vat_input": vat_input,
			"net_payable": vat_output - vat_input
		})
	
	return data

def get_chart(data):
	return {
		"data": {
			"labels": [d["month"] for d in data],
			"datasets": [
				{"name": _("VAT Output"), "values": [d["vat_output"] for d in data]},
				{"name": _("VAT Input"), "values": [d["vat_input"] for d in data]}
			]
		},
		"type": "bar",
		"colors": ["#ff5858", "#5e64ff"]
	}

def get_report_summary(data):
	total_output = sum(d["vat_output"] for d in data)
	total_input = sum(d["vat_input"] for d in data)
	net_payable = total_output - total_input

	return [
		{"value": total_output, "label": _("Total VAT Output"), "datatype": "Currency"},
		{"value": total_input, "label": _("Total VAT Input"), "datatype": "Currency"},
		{"value": net_payable, "label": _("Net Tax Payable"), "datatype": "Currency", "indicator": "Red" if net_payable > 0 else "Green"}
	]
