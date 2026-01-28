# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class IncomeRecipient(Document):
	"""
	Income Recipient for e-Bupot withholding tax documents.
	
	Stores recipient information for withholding tax certificates
	including NPWP, NIK, and contact details for tax reporting.
	"""

	def validate(self):
		errors = []
		
		# Validate required fields
		if not self.recipient_name:
			errors.append(_("Recipient Name is required"))
		
		# At least one of NPWP or NIK must be provided
		if not self.recipient_npwp and not self.recipient_nik:
			errors.append(_("Either Recipient NPWP or Recipient NIK must be provided"))
		
		# Validate NPWP format (15 digits)
		if self.recipient_npwp:
			npwp_clean = re.sub(r'[.\-]', '', str(self.recipient_npwp))
			if not re.match(r'^\d{15}$', npwp_clean):
				errors.append(_("Invalid NPWP format. NPWP must be 15 digits. Current value: {0}").format(self.recipient_npwp))
		
		# Validate NIK format (16 digits) if provided
		if self.recipient_nik:
			nik_clean = re.sub(r'[.\-]', '', str(self.recipient_nik))
			if not re.match(r'^\d{16}$', nik_clean):
				errors.append(_("Invalid NIK format. NIK must be 16 digits. Current value: {0}").format(self.recipient_nik))
		
		# Validate recipient type
		if self.recipient_type and self.recipient_type not in ['Individual', 'Company', 'Government']:
			errors.append(_("Invalid Recipient Type. Must be one of: Individual, Company, Government"))
		
		# Validate email format if provided
		if self.email:
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.email):
				errors.append(_("Invalid email format: {0}").format(self.email))
		
		# Validate postal code format if provided (5 digits for Indonesia)
		if self.postal_code:
			postal_clean = re.sub(r'[.\-]', '', str(self.postal_code))
			if not re.match(r'^\d{5}$', postal_clean):
				errors.append(_("Invalid postal code format. Must be 5 digits. Current value: {0}").format(self.postal_code))
		
		# Raise errors if any
		if errors:
			frappe.throw("<br>".join(errors), title=_("Validation Error"))
