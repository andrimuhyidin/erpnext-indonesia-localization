# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re


class Signer(Document):
	def validate(self):
		errors = []
		
		# Validate required fields
		if not self.signer_name:
			errors.append(_("Signer Name is required"))
		
		if not self.signer_npwp:
			errors.append(_("Signer NPWP is required"))
		
		if not self.signer_position:
			errors.append(_("Signer Position is required"))
		
		# Validate NPWP format (15 digits)
		if self.signer_npwp:
			npwp_clean = re.sub(r'[.\-]', '', str(self.signer_npwp))
			if not re.match(r'^\d{15}$', npwp_clean):
				errors.append(_("Invalid NPWP format. NPWP must be 15 digits. Current value: {0}").format(self.signer_npwp))
		
		# Validate email format if provided
		if self.signer_email:
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.signer_email):
				errors.append(_("Invalid email format: {0}").format(self.signer_email))
		
		# Validate phone format if provided (Indonesian phone format)
		if self.signer_phone:
			phone_clean = re.sub(r'[.\-\s\(\)]', '', str(self.signer_phone))
			# Indonesian phone: starts with 0 or +62, followed by 9-12 digits
			if not re.match(r'^(\+62|0)[0-9]{9,12}$', phone_clean):
				errors.append(_("Invalid phone format. Must be a valid Indonesian phone number. Current value: {0}").format(self.signer_phone))
		
		# Business logic: Only one active signer should exist
		if self.is_active:
			existing_active = frappe.get_all(
				"Signer",
				filters={
					"is_active": 1,
					"name": ["!=", self.name]
				},
				limit=1
			)
			if existing_active:
				errors.append(_("Another signer is already set as active. Please deactivate it first."))
		
		# Raise errors if any
		if errors:
			frappe.throw("<br>".join(errors), title=_("Validation Error"))
	
	def on_update(self):
		# Auto-set as active signer in Pajak.io if is_active is checked
		if self.is_active and self.signer_id:
			try:
				from erpnext_indonesia_localization.api import set_active_signer
				set_active_signer(self.signer_id)
				frappe.msgprint(_("Signer set as active in Pajak.io"))
			except Exception as e:
				frappe.log_error(f"Error setting active signer: {str(e)}", "Signer Error")
