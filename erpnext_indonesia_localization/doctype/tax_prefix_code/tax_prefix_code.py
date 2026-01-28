# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class TaxPrefixCode(Document):
	"""
	Tax Prefix Code for e-Faktur transaction codes.
	
	Stores the two-digit transaction codes used in Indonesian
	e-Faktur system to identify transaction types (e.g., 01-09).
	"""

	pass
