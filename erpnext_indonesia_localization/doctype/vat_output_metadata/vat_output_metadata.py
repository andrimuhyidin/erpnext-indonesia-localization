# Copyright (c) 2023, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import base64

class VATOutputMetadata(Document):
	"""
	VAT Output Metadata for tracking e-Faktur status.
	
	Stores metadata about VAT output documents including
	approval status, PDF base64 content, and synchronization
	status with the DJP system.
	"""

	pass

@frappe.whitelist()
def convert_base64_to_pdf(docname):
	"""Convert base64 encoded PDF and download.
	
	Security: Removed allow_guest=True to prevent unauthorized access
	to tax documents. Only authenticated users with read permission
	can download VAT Output Metadata PDFs.
	"""
	# Verify user has permission to access this document
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required to download tax documents"))
	
	if not frappe.has_permission("VAT Output Metadata", "read", docname):
		frappe.throw(_("You do not have permission to access this document"))
	
	doc = frappe.get_doc("VAT Output Metadata", docname)
	base64_string = doc.base64
	
	if not base64_string:
		frappe.throw(_("No PDF data available for this document"))
	
	try:
		output_file = f"/tmp/pajak-io-{docname}.pdf"

		base64_to_pdf(base64_string, output_file)

		with open(output_file, 'rb') as file:
			frappe.local.response.filename = f"{docname}.pdf"
			frappe.local.response.filecontent = file.read()
			frappe.local.response.type = "download"

	except Exception as e:
		frappe.log_error(f"PDF conversion error for {docname}: {str(e)}")
		frappe.throw(_("Something went wrong while downloading the PDF."))

def base64_to_pdf(base64_string, output_file):
	pdf_data = base64.b64decode(base64_string)
	with open(output_file, 'wb') as file:
		file.write(pdf_data)


