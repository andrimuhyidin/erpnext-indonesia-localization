# Copyright (c) 2024, Agile Technica and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ListofSalesInvoice(Document):
	"""
	List of Sales Invoice child table entry.
	
	Stores references to sales invoices for batch processing
	in tax invoice exporters and SPT generation.
	"""

	pass
