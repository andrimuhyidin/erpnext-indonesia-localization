# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SetupWizard(Document):
	@frappe.whitelist()
	def complete_setup(self):
		"""
		Complete the setup wizard and update Indonesia Localization Settings
		"""
		try:
			# Get or create Indonesia Localization Settings
			if not frappe.db.exists("Indonesia Localization Settings", "Indonesia Localization Settings"):
				settings = frappe.new_doc("Indonesia Localization Settings")
			else:
				settings = frappe.get_doc("Indonesia Localization Settings", "Indonesia Localization Settings")
			
			# Update company information
			if self.step_1_company:
				company_doc = frappe.get_doc("Company", self.step_1_company)
				if self.step_1_tax_id:
					company_doc.tax_id = self.step_1_tax_id
				if self.step_1_nitku:
					company_doc.companys_nitku = self.step_1_nitku
				company_doc.save()
			
			# Update Pajak.io API settings
			if self.step_2_pajakio_api_key:
				settings.pajakio_api_key = self.step_2_pajakio_api_key
			
			# Update tax invoice number source
			if self.step_3_tax_invoice_source:
				settings.tax_invoice_number_source = self.step_3_tax_invoice_source
			
			# Update auto-create setting
			settings.auto_create_vat_output_metadata = self.step_3_auto_create_vom or 0
			
			settings.save()
			
			# Mark setup as completed
			self.setup_status = "Completed"
			self.save()
			
			frappe.msgprint(_("Setup completed successfully!"), indicator="green")
			
			return {
				"status": "success",
				"message": "Setup completed successfully"
			}
			
		except Exception as e:
			frappe.log_error(f"Error completing setup: {str(e)}", "Setup Wizard Error")
			frappe.throw(_("Error completing setup: {0}").format(str(e)))


@frappe.whitelist()
def validate_setup_completeness():
	"""
	Validate if Indonesia Localization setup is complete
	"""
	settings = frappe.get_single("Indonesia Localization Settings")
	
	missing_fields = []
	
	if not settings.tax_invoice_number_source:
		missing_fields.append("Tax Invoice Number Source")
	
	if not settings.pajakio_api_key:
		missing_fields.append("Pajak.io API Key")
	
	if missing_fields:
		return {
			"complete": False,
			"missing_fields": missing_fields
		}
	
	return {
		"complete": True,
		"message": "Setup is complete"
	}
