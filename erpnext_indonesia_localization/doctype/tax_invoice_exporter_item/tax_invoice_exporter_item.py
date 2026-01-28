# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class TaxInvoiceExporterItem(Document):
	"""
	Tax Invoice Exporter Item child table entry.
	
	Stores individual sales invoice references with their
	tax invoice details for e-Faktur CSV export.
	"""

	pass
