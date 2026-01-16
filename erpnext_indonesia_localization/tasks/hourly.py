# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import time


# Configuration constants
BATCH_SIZE = 50  # Process in batches of 50
RATE_LIMIT_DELAY = 1  # Delay in seconds between API calls


def auto_upload_to_djp():
	"""
	Hourly task to auto-upload approved VAT Output to DJP if enabled.
	Only uploads VAT Output that are approved but not yet uploaded.
	Includes rate limiting and batch processing.
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		
		# Only upload if autouploaddjp is enabled
		if not indonesia_localization_settings.autouploaddjp:
			return
		
		# Get all approved VAT Output that haven't been uploaded
		vom_list = frappe.get_all(
			"VAT Output Metadata",
			filters={
				"status": "Approved",
				"vat_upload_success": ["!=", 1],
				"transactionid": ["!=", ""]
			},
			fields=["name", "transactionid"],
			limit=200  # Limit to prevent timeout
		)
		
		if not vom_list:
			frappe.logger().info("No VAT Output Metadata records to upload")
			return
		
		from erpnext_indonesia_localization.api import upload_vat_output
		
		success_count = 0
		failure_count = 0
		
		# Process in batches
		for batch_start in range(0, len(vom_list), BATCH_SIZE):
			batch = vom_list[batch_start:batch_start + BATCH_SIZE]
			
			for idx, vom in enumerate(batch):
				try:
					# Rate limiting: delay between API calls
					if idx > 0:
						time.sleep(RATE_LIMIT_DELAY)
					
					vom_doc = frappe.get_doc("VAT Output Metadata", vom.name)
					upload_vat_output(vom_doc.name)
					success_count += 1
					
				except frappe.ValidationError as e:
					frappe.log_error(
						f"Validation error uploading VAT Output Metadata {vom.name} to DJP: {str(e)}",
						"Auto Upload DJP Error"
					)
					failure_count += 1
					continue
				except Exception as e:
					frappe.log_error(
						f"Error uploading VAT Output Metadata {vom.name} to DJP: {str(e)}",
						"Auto Upload DJP Error"
					)
					failure_count += 1
					continue
			
			# Commit batch to prevent long transactions
			frappe.db.commit()
			
			# Log batch progress
			frappe.logger().info(f"Processed VAT Output upload batch {batch_start // BATCH_SIZE + 1}: {success_count} success, {failure_count} failures")
				
		frappe.logger().info(f"Auto-uploaded VAT Output Metadata: {success_count} success, {failure_count} failures out of {len(vom_list)} total")
		
	except Exception as e:
		frappe.log_error(f"Error in auto_upload_to_djp: {str(e)}", "Auto Upload DJP Error")
		frappe.db.rollback()


def auto_upload_pending_documents():
	"""
	Hourly task to auto-upload pending documents (VAT Output, VAT Input, Withholding Tax) to DJP.
	Includes rate limiting and batch processing.
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		
		# Auto-upload VAT Output if enabled
		if indonesia_localization_settings.autouploaddjp:
			auto_upload_to_djp()
		
		# Auto-upload VAT Input if enabled
		if hasattr(indonesia_localization_settings, 'auto_upload_vat_input') and indonesia_localization_settings.auto_upload_vat_input:
			# Get all approved VAT Input that haven't been uploaded
			vim_list = frappe.get_all(
				"VAT Input Metadata",
				filters={
					"status": "Approved",
					"vat_upload_success": ["!=", 1],
					"transactionid": ["!=", ""]
				},
				fields=["name", "transactionid"],
				limit=200  # Limit to prevent timeout
			)
			
			if vim_list:
				from erpnext_indonesia_localization.api.pajakio import upload_vat_input
				
				success_count = 0
				failure_count = 0
				
				# Process in batches
				for batch_start in range(0, len(vim_list), BATCH_SIZE):
					batch = vim_list[batch_start:batch_start + BATCH_SIZE]
					
					for idx, vim in enumerate(batch):
						try:
							# Rate limiting: delay between API calls
							if idx > 0:
								time.sleep(RATE_LIMIT_DELAY)
							
							upload_vat_input(vim.name)
							success_count += 1
							
						except frappe.ValidationError as e:
							frappe.log_error(
								f"Validation error uploading VAT Input Metadata {vim.name} to DJP: {str(e)}",
								"Auto Upload VAT Input Error"
							)
							failure_count += 1
							continue
						except Exception as e:
							frappe.log_error(
								f"Error uploading VAT Input Metadata {vim.name} to DJP: {str(e)}",
								"Auto Upload VAT Input Error"
							)
							failure_count += 1
							continue
					
					# Commit batch to prevent long transactions
					frappe.db.commit()
				
				frappe.logger().info(f"Auto-uploaded VAT Input Metadata: {success_count} success, {failure_count} failures out of {len(vim_list)} total")
		
		# Auto-upload Withholding Tax if enabled
		if hasattr(indonesia_localization_settings, 'auto_upload_withholding_tax') and indonesia_localization_settings.auto_upload_withholding_tax:
			# Get all submitted Withholding Tax that haven't been uploaded
			wtc_list = frappe.get_all(
				"Withholding Tax Certificate",
				filters={
					"status": "Submitted",
					"xml_export_status": ["!=", "Exported"],
					"transactionid": ["!=", ""]
				},
				fields=["name", "transactionid"],
				limit=200  # Limit to prevent timeout
			)
			
			if wtc_list:
				from erpnext_indonesia_localization.api.pajakio import upload_withholding_tax
				
				success_count = 0
				failure_count = 0
				
				# Process in batches
				for batch_start in range(0, len(wtc_list), BATCH_SIZE):
					batch = wtc_list[batch_start:batch_start + BATCH_SIZE]
					
					for idx, wtc in enumerate(batch):
						try:
							# Rate limiting: delay between API calls
							if idx > 0:
								time.sleep(RATE_LIMIT_DELAY)
							
							upload_withholding_tax(wtc.name)
							success_count += 1
							
						except frappe.ValidationError as e:
							frappe.log_error(
								f"Validation error uploading Withholding Tax Certificate {wtc.name} to DJP: {str(e)}",
								"Auto Upload Withholding Tax Error"
							)
							failure_count += 1
							continue
						except Exception as e:
							frappe.log_error(
								f"Error uploading Withholding Tax Certificate {wtc.name} to DJP: {str(e)}",
								"Auto Upload Withholding Tax Error"
							)
							failure_count += 1
							continue
					
					# Commit batch to prevent long transactions
					frappe.db.commit()
				
				frappe.logger().info(f"Auto-uploaded Withholding Tax Certificates: {success_count} success, {failure_count} failures out of {len(wtc_list)} total")
		
	except Exception as e:
		frappe.log_error(f"Error in auto_upload_pending_documents: {str(e)}", "Auto Upload Pending Documents Error")
		frappe.db.rollback()


def run_hourly_tasks():
	"""
	Main function to run all hourly scheduled tasks
	"""
	frappe.log_simple("Hourly tasks started", "erpnext_indonesia_localization_hourly_tasks")
	
	# Auto-upload pending documents
	auto_upload_pending_documents()
	
	frappe.log_simple("Hourly tasks completed", "erpnext_indonesia_localization_hourly_tasks")
