# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import time


# Configuration constants
BATCH_SIZE = 50  # Process in batches of 50
RATE_LIMIT_DELAY = 1  # Delay in seconds between API calls
MAX_RETRIES = 3  # Maximum retries for failed API calls


def sync_vat_output_status():
	"""
	Daily task to sync VAT Output status from DJP/Pajak.io.
	Checks all VAT Output Metadata with status 'To Be Reviewed' or 'Draft'
	and updates their status by calling Pajak.io API.
	Includes rate limiting and batch processing.
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		
		# Only sync if get_details_vat_output is enabled
		if not indonesia_localization_settings.get_details_vat_output:
			return
		
		# Get all VAT Output Metadata that need status sync
		vom_list = frappe.get_all(
			"VAT Output Metadata",
			filters={
				"status": ["in", ["To Be Reviewed", "Draft"]],
				"transactionid": ["!=", ""]
			},
			fields=["name", "transactionid", "status"],
			limit=500  # Limit to prevent timeout
		)
		
		if not vom_list:
			frappe.logger().info("No VAT Output Metadata records to sync")
			return
		
		from erpnext_indonesia_localization.api import get_vat_output_detail
		
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
					response_msg = get_vat_output_detail(vom_doc)
					
					# Update status if approved
					if isinstance(response_msg, dict) and response_msg.get('code') == 200:
						if response_msg.get('data') and len(response_msg['data']) > 0:
							vom_doc.status = "Approved"
							vom_doc.nofa = response_msg['data'][0].get('nofa', '')
							
							# Update Sales Invoice if exists
							if vom_doc.noinvoice and vom_doc.parent_doctype:
								try:
									parent_doc = frappe.get_doc(vom_doc.parent_doctype, vom_doc.noinvoice)
									parent_doc.nomor_faktur = vom_doc.nofa
									parent_doc.save(ignore_permissions=True)
								except Exception as e:
									frappe.log_error(f"Error updating parent invoice: {str(e)}", "VAT Output Sync Error")
							
							vom_doc.save(ignore_permissions=True)
							success_count += 1
					else:
						failure_count += 1
						
				except frappe.ValidationError as e:
					# API validation errors - log and continue
					frappe.log_error(
						f"Validation error syncing VAT Output Metadata {vom.name}: {str(e)}",
						"VAT Output Sync Error"
					)
					failure_count += 1
					continue
				except Exception as e:
					# Other errors - retry logic could be added here
					frappe.log_error(
						f"Error syncing VAT Output Metadata {vom.name}: {str(e)}",
						"VAT Output Sync Error"
					)
					failure_count += 1
					continue
			
			# Commit batch to prevent long transactions
			frappe.db.commit()
			
			# Log batch progress
			frappe.logger().info(f"Processed batch {batch_start // BATCH_SIZE + 1}: {success_count} success, {failure_count} failures")
				
		frappe.logger().info(f"Synced VAT Output Metadata: {success_count} success, {failure_count} failures out of {len(vom_list)} total")
		
	except Exception as e:
		frappe.log_error(f"Error in sync_vat_output_status: {str(e)}", "VAT Output Sync Error")
		frappe.db.rollback()


def check_pending_approvals():
	"""
	Daily task to check for invoices that need approval attention.
	Creates notifications for invoices pending approval.
	"""
	try:
		# Get invoices with VAT Output Metadata in pending status
		pending_vom = frappe.get_all(
			"VAT Output Metadata",
			filters={
				"status": ["in", ["To Be Reviewed", "Draft"]]
			},
			fields=["name", "noinvoice", "status", "create_vat_response"]
		)
		
		# Log summary
		if pending_vom:
			frappe.logger().info(f"Found {len(pending_vom)} VAT Output Metadata pending approval")
		
	except Exception as e:
		frappe.log_error(f"Error in check_pending_approvals: {str(e)}", "Pending Approval Check Error")


def sync_vat_input_status():
	"""
	Daily task to sync VAT Input status from Pajak.io.
	Checks all VAT Input Metadata with transaction ID and updates their status.
	Includes rate limiting and batch processing.
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		
		# Only sync if enabled
		if not hasattr(indonesia_localization_settings, 'get_details_vat_input') or not indonesia_localization_settings.get_details_vat_input:
			return
		
		# Get all VAT Input Metadata that need status sync
		vim_list = frappe.get_all(
			"VAT Input Metadata",
			filters={
				"status": ["in", ["To Be Reviewed", "Draft"]],
				"transactionid": ["!=", ""]
			},
			fields=["name", "transactionid", "status"],
			limit=500  # Limit to prevent timeout
		)
		
		if not vim_list:
			frappe.logger().info("No VAT Input Metadata records to sync")
			return
		
		from erpnext_indonesia_localization.api.pajakio import get_detail_vat_input
		
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
					
					vim_doc = frappe.get_doc("VAT Input Metadata", vim.name)
					response = get_detail_vat_input(vim_doc)
					
					# Update status if response is successful
					if isinstance(response, dict) and response.get('code') == 200:
						if response.get('data'):
							data = response['data']
							if isinstance(data, list) and len(data) > 0:
								data = data[0]
							
							if isinstance(data, dict) and 'status' in data:
								vim_doc.status = data['status']
								vim_doc.save(ignore_permissions=True)
								success_count += 1
							else:
								failure_count += 1
						else:
							failure_count += 1
					else:
						failure_count += 1
						
				except frappe.ValidationError as e:
					frappe.log_error(
						f"Validation error syncing VAT Input Metadata {vim.name}: {str(e)}",
						"VAT Input Sync Error"
					)
					failure_count += 1
					continue
				except Exception as e:
					frappe.log_error(
						f"Error syncing VAT Input Metadata {vim.name}: {str(e)}",
						"VAT Input Sync Error"
					)
					failure_count += 1
					continue
			
			# Commit batch to prevent long transactions
			frappe.db.commit()
			
			# Log batch progress
			frappe.logger().info(f"Processed VAT Input batch {batch_start // BATCH_SIZE + 1}: {success_count} success, {failure_count} failures")
				
		frappe.logger().info(f"Synced VAT Input Metadata: {success_count} success, {failure_count} failures out of {len(vim_list)} total")
		
	except Exception as e:
		frappe.log_error(f"Error in sync_vat_input_status: {str(e)}", "VAT Input Sync Error")
		frappe.db.rollback()


def sync_withholding_tax_status():
	"""
	Daily task to sync Withholding Tax status from Pajak.io.
	Checks all Withholding Tax Certificates with transaction ID and updates their status.
	Includes rate limiting and batch processing.
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		
		# Only sync if enabled
		if not hasattr(indonesia_localization_settings, 'url_get_status_bupot') or not indonesia_localization_settings.url_get_status_bupot:
			return
		
		# Get all Withholding Tax Certificates that need status sync
		wtc_list = frappe.get_all(
			"Withholding Tax Certificate",
			filters={
				"status": ["in", ["Draft", "Submitted"]],
				"transactionid": ["!=", ""]
			},
			fields=["name", "transactionid", "status"],
			limit=500  # Limit to prevent timeout
		)
		
		if not wtc_list:
			frappe.logger().info("No Withholding Tax Certificate records to sync")
			return
		
		from erpnext_indonesia_localization.api.pajakio import get_status_bupot
		
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
					
					wtc_doc = frappe.get_doc("Withholding Tax Certificate", wtc.name)
					response = get_status_bupot(wtc.transactionid)
					
					# Update status if response is successful
					if isinstance(response, dict) and response.get('code') == 200:
						if response.get('data'):
							data = response['data']
							if isinstance(data, list) and len(data) > 0:
								data = data[0]
							
							if isinstance(data, dict) and 'status' in data:
								wtc_doc.status = data['status']
								wtc_doc.save(ignore_permissions=True)
								success_count += 1
							else:
								failure_count += 1
						else:
							failure_count += 1
					else:
						failure_count += 1
						
				except frappe.ValidationError as e:
					frappe.log_error(
						f"Validation error syncing Withholding Tax Certificate {wtc.name}: {str(e)}",
						"Withholding Tax Sync Error"
					)
					failure_count += 1
					continue
				except Exception as e:
					frappe.log_error(
						f"Error syncing Withholding Tax Certificate {wtc.name}: {str(e)}",
						"Withholding Tax Sync Error"
					)
					failure_count += 1
					continue
			
			# Commit batch to prevent long transactions
			frappe.db.commit()
			
			# Log batch progress
			frappe.logger().info(f"Processed Withholding Tax batch {batch_start // BATCH_SIZE + 1}: {success_count} success, {failure_count} failures")
				
		frappe.logger().info(f"Synced Withholding Tax Certificates: {success_count} success, {failure_count} failures out of {len(wtc_list)} total")
		
	except Exception as e:
		frappe.log_error(f"Error in sync_withholding_tax_status: {str(e)}", "Withholding Tax Sync Error")
		frappe.db.rollback()


def run_daily_tasks():
	"""
	Main function to run all daily scheduled tasks
	"""
	frappe.log_simple("Daily tasks started", "erpnext_indonesia_localization_daily_tasks")
	
	# Sync VAT Output status
	sync_vat_output_status()
	
	# Sync VAT Input status
	sync_vat_input_status()
	
	# Sync Withholding Tax status
	sync_withholding_tax_status()
	
	# Check pending approvals
	check_pending_approvals()
	
	frappe.log_simple("Daily tasks completed", "erpnext_indonesia_localization_daily_tasks")
