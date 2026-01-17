# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Order


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


	pi = frappe.qb.DocType("Purchase Invoice")
	s = frappe.qb.DocType("Supplier")
	
	query = (
		frappe.qb.from_(pi)
		.left_join(s).on(pi.supplier == s.name)
		.select(
			pi.supplier,
			s.tax_id,
			pi.name.as_("invoice_name"),
			pi.bill_no,
			pi.bill_date,
			pi.total_taxes_and_charges
		)
		.where(pi.docstatus == 1)
		.orderby(pi.bill_date, order=frappe.query_builder.Order.desc)
	)

	if filters.get("supplier"):
		query = query.where(pi.supplier == filters.get("supplier"))
	
	if filters.get("from_date"):
		query = query.where(pi.bill_date >= filters.get("from_date"))
	
	if filters.get("to_date"):
		query = query.where(pi.bill_date <= filters.get("to_date"))
	
	if filters.get("company"):
		query = query.where(pi.company == filters.get("company"))
	
	data = query.run(as_dict=True)
	return data
