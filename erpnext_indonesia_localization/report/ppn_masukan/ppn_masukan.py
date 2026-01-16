# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	"""
	Execute PPN Masukan (VAT Input) Report
	Similar to PPN Keluaran but for Purchase Invoice
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},
		{
			"label": _("Tax ID"),
			"fieldname": "tax_id",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Invoice Name"),
			"fieldname": "invoice_name",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 150
		},
		{
			"label": _("Bill Number"),
			"fieldname": "bill_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Bill Date"),
			"fieldname": "bill_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Total Taxes and Charges"),
			"fieldname": "total_taxes_and_charges",
			"fieldtype": "Currency",
			"width": 150
		}
	]


def get_data(filters):
	"""Get report data based on filters"""
	conditions = "WHERE pi.docstatus = 1"
	
	if filters.get("supplier"):
		conditions += f" AND pi.supplier = '{filters.get('supplier')}'"
	
	if filters.get("from_date"):
		conditions += f" AND pi.bill_date >= '{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		conditions += f" AND pi.bill_date <= '{filters.get('to_date')}'"
	
	if filters.get("company"):
		conditions += f" AND pi.company = '{filters.get('company')}'"
	
	query = f"""
		SELECT
			pi.supplier,
			s.tax_id,
			pi.name AS invoice_name,
			pi.bill_no,
			pi.bill_date,
			pi.total_taxes_and_charges
		FROM
			`tabPurchase Invoice` pi
		LEFT JOIN
			`tabSupplier` s ON pi.supplier = s.name
		{conditions}
		ORDER BY
			pi.bill_date DESC
	"""
	
	data = frappe.db.sql(query, as_dict=True)
	return data
