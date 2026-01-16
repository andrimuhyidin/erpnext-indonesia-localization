# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint


# Configuration constants
BATCH_SIZE = 50  # Process in batches of 50
PROGRESS_UPDATE_INTERVAL = 10  # Update progress every N items


@frappe.whitelist()
def bulk_create_vat_output_metadata(invoice_names, progress_key=None):
	"""
	Bulk create VAT Output Metadata for multiple Sales Invoices
	Includes batch processing and progress tracking.
	
	Args:
		invoice_names: List of Sales Invoice names
		progress_key: Optional key for progress tracking
		
	Returns:
		Dictionary with success and failure counts
	"""
	if isinstance(invoice_names, str):
		invoice_names = frappe.parse_json(invoice_names)
	
	if not invoice_names:
		return {
			"success_count": 0,
			"failure_count": 0,
			"errors": ["No invoices provided"]
		}
	
	success_count = 0
	failure_count = 0
	errors = []
	failed_items = []  # Track failed items for rollback if needed
	
	indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
	total = len(invoice_names)
	
	# Process in batches
	for batch_start in range(0, total, BATCH_SIZE):
		batch = invoice_names[batch_start:batch_start + BATCH_SIZE]
		
		for idx, invoice_name in enumerate(batch):
			try:
				# Update progress
				if progress_key and (idx % PROGRESS_UPDATE_INTERVAL == 0 or idx == len(batch) - 1):
					current = batch_start + idx + 1
					frappe.publish_progress(
						current * 100 / total,
						title=_("Processing"),
						description=_("Creating VAT Output Metadata: {0} of {1}").format(current, total)
					)
				
				si_doc = frappe.get_doc("Sales Invoice", invoice_name)
				
				# Check if VAT Output Metadata already exists
				if frappe.db.exists("VAT Output Metadata", {"noinvoice": invoice_name}):
					errors.append(f"VAT Output Metadata already exists for {invoice_name}")
					failure_count += 1
					failed_items.append(invoice_name)
					continue
				
				# Import function
				from erpnext_indonesia_localization.doc_events import create_vat_output_metadata
				
				success_status, message = create_vat_output_metadata(si_doc, indonesia_localization_settings)
				
				if success_status:
					success_count += 1
					# Commit after each successful creation to prevent rollback of all on error
					frappe.db.commit()
				else:
					failure_count += 1
					errors.append(f"{invoice_name}: {message}")
					failed_items.append(invoice_name)
					
			except Exception as e:
				failure_count += 1
				errors.append(f"{invoice_name}: {str(e)}")
				failed_items.append(invoice_name)
				frappe.log_error(f"Error creating VAT Output Metadata for {invoice_name}: {str(e)}", "Bulk Operations Error")
				# Continue processing other items
				continue
		
		# Commit batch to prevent long transactions
		frappe.db.commit()
	
	# Final progress update
	if progress_key:
		frappe.publish_progress(100, title=_("Completed"), description=_("Processed {0} invoices").format(total))
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors[:50],  # Limit errors to first 50
		"total_errors": len(errors),
		"failed_items": failed_items[:50]  # Limit failed items to first 50
	}


@frappe.whitelist()
def bulk_export_to_xml(exporter_name, invoice_names):
	"""
	Bulk export Sales Invoices to XML
	
	Args:
		exporter_name: Coretax XML Exporter document name
		invoice_names: List of Sales Invoice names to export
		
	Returns:
		Dictionary with export status
	"""
	if isinstance(invoice_names, str):
		invoice_names = frappe.parse_json(invoice_names)
	
	try:
		exporter_doc = frappe.get_doc("Coretax XML Exporter", exporter_name)
		
		# Update Sales Invoices to mark as exported
		for invoice_name in invoice_names:
			frappe.set_value("Sales Invoice", invoice_name, {
				"is_xml_generated": 1,
				"coretax_xml_exporter": exporter_name
			})
		
		return {
			"status": "success",
			"message": f"Successfully marked {len(invoice_names)} invoices for export"
		}
	except Exception as e:
		frappe.log_error(f"Error in bulk export: {str(e)}", "Bulk Operations Error")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist()
def bulk_update_status(doctype, names, status_field, new_status):
	"""
	Bulk update status for multiple documents
	
	Args:
		doctype: Document type
		names: List of document names
		status_field: Field name for status
		new_status: New status value
		
	Returns:
		Dictionary with update status
	"""
	if isinstance(names, str):
		names = frappe.parse_json(names)
	
	success_count = 0
	failure_count = 0
	errors = []
	
	for name in names:
		try:
			frappe.set_value(doctype, name, status_field, new_status)
			success_count += 1
		except Exception as e:
			failure_count += 1
			errors.append(f"{name}: {str(e)}")
			frappe.log_error(f"Error updating {doctype} {name}: {str(e)}", "Bulk Operations Error")
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors
	}


@frappe.whitelist()
def bulk_approve_vat_output(metadata_names):
	"""
	Bulk approve VAT Output Metadata
	
	Args:
		metadata_names: List of VAT Output Metadata names
		
	Returns:
		Dictionary with approval status
	"""
	if isinstance(metadata_names, str):
		metadata_names = frappe.parse_json(metadata_names)
	
	return bulk_update_status(
		"VAT Output Metadata",
		metadata_names,
		"status",
		"Approved"
	)


@frappe.whitelist()
def bulk_reject_vat_output(metadata_names):
	"""
	Bulk reject VAT Output Metadata
	
	Args:
		metadata_names: List of VAT Output Metadata names
		
	Returns:
		Dictionary with rejection status
	"""
	if isinstance(metadata_names, str):
		metadata_names = frappe.parse_json(metadata_names)
	
	return bulk_update_status(
		"VAT Output Metadata",
		metadata_names,
		"status",
		"Rejected"
	)


@frappe.whitelist()
def bulk_upload_vat_output(metadata_names, progress_key=None):
	"""
	Bulk upload VAT Output to DJP via API
	Includes batch processing and progress tracking.
	
	Args:
		metadata_names: List of VAT Output Metadata names
		progress_key: Optional key for progress tracking
		
	Returns:
		Dictionary with upload status
	"""
	if isinstance(metadata_names, str):
		metadata_names = frappe.parse_json(metadata_names)
	
	if not metadata_names:
		return {
			"success_count": 0,
			"failure_count": 0,
			"errors": ["No metadata provided"]
		}
	
	from erpnext_indonesia_localization.api import upload_vat_output
	import time
	
	success_count = 0
	failure_count = 0
	errors = []
	total = len(metadata_names)
	RATE_LIMIT_DELAY = 1  # Delay between API calls
	
	# Process in batches
	for batch_start in range(0, total, BATCH_SIZE):
		batch = metadata_names[batch_start:batch_start + BATCH_SIZE]
		
		for idx, name in enumerate(batch):
			try:
				# Rate limiting: delay between API calls
				if idx > 0:
					time.sleep(RATE_LIMIT_DELAY)
				
				# Update progress
				if progress_key and (idx % PROGRESS_UPDATE_INTERVAL == 0 or idx == len(batch) - 1):
					current = batch_start + idx + 1
					frappe.publish_progress(
						current * 100 / total,
						title=_("Processing"),
						description=_("Uploading VAT Output: {0} of {1}").format(current, total)
					)
				
				upload_vat_output(name)
				success_count += 1
				# Commit after each successful upload
				frappe.db.commit()
				
			except Exception as e:
				failure_count += 1
				errors.append(f"{name}: {str(e)}")
				frappe.log_error(f"Error uploading VAT Output {name}: {str(e)}", "Bulk Operations Error")
				# Continue processing other items
				continue
		
		# Commit batch
		frappe.db.commit()
	
	# Final progress update
	if progress_key:
		frappe.publish_progress(100, title=_("Completed"), description=_("Processed {0} metadata").format(total))
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors[:50],  # Limit errors to first 50
		"total_errors": len(errors)
	}


@frappe.whitelist()
def bulk_upload_vat_input(metadata_names):
	"""
	Bulk upload VAT Input to DJP via API
	
	Args:
		metadata_names: List of VAT Input Metadata names
		
	Returns:
		Dictionary with upload status
	"""
	if isinstance(metadata_names, str):
		metadata_names = frappe.parse_json(metadata_names)
	
	from erpnext_indonesia_localization.api import upload_vat_input
	
	success_count = 0
	failure_count = 0
	errors = []
	
	for name in metadata_names:
		try:
			upload_vat_input(name)
			success_count += 1
		except Exception as e:
			failure_count += 1
			errors.append(f"{name}: {str(e)}")
			frappe.log_error(f"Error uploading VAT Input {name}: {str(e)}", "Bulk Operations Error")
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors
	}


@frappe.whitelist()
def bulk_upload_withholding_tax(certificate_names):
	"""
	Bulk upload Withholding Tax to DJP via API
	
	Args:
		certificate_names: List of Withholding Tax Certificate names
		
	Returns:
		Dictionary with upload status
	"""
	if isinstance(certificate_names, str):
		certificate_names = frappe.parse_json(certificate_names)
	
	from erpnext_indonesia_localization.api import upload_withholding_tax
	
	success_count = 0
	failure_count = 0
	errors = []
	
	for name in certificate_names:
		try:
			upload_withholding_tax(name)
			success_count += 1
		except Exception as e:
			failure_count += 1
			errors.append(f"{name}: {str(e)}")
			frappe.log_error(f"Error uploading Withholding Tax {name}: {str(e)}", "Bulk Operations Error")
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors
	}


@frappe.whitelist()
def bulk_sync_status(doctype, names):
	"""
	Bulk sync status from Pajak.io API
	
	Args:
		doctype: Document type (VAT Output Metadata, VAT Input Metadata, or Withholding Tax Certificate)
		names: List of document names
		
	Returns:
		Dictionary with sync status
	"""
	if isinstance(names, str):
		names = frappe.parse_json(names)
	
	success_count = 0
	failure_count = 0
	errors = []
	
	for name in names:
		try:
			if doctype == "VAT Output Metadata":
				from erpnext_indonesia_localization.api import get_vat_output_detail
				get_vat_output_detail(name)
			elif doctype == "VAT Input Metadata":
				from erpnext_indonesia_localization.api.pajakio import get_detail_vat_input
				get_detail_vat_input(name)
			elif doctype == "Withholding Tax Certificate":
				doc = frappe.get_doc(doctype, name)
				doc.sync_status_from_pajakio()
			else:
				raise ValueError(f"Unsupported doctype for sync: {doctype}")
			
			success_count += 1
		except Exception as e:
			failure_count += 1
			errors.append(f"{name}: {str(e)}")
			frappe.log_error(f"Error syncing {doctype} {name}: {str(e)}", "Bulk Operations Error")
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors
	}


@frappe.whitelist()
def bulk_delete_via_api(doctype, names):
	"""
	Bulk delete documents via Pajak.io API
	
	Args:
		doctype: Document type (VAT Output Metadata, VAT Input Metadata, or Withholding Tax Certificate)
		names: List of document names
		
	Returns:
		Dictionary with delete status
	"""
	if isinstance(names, str):
		names = frappe.parse_json(names)
	
	success_count = 0
	failure_count = 0
	errors = []
	
	for name in names:
		try:
			if doctype == "VAT Output Metadata":
				from erpnext_indonesia_localization.api import delete_vat_output
				delete_vat_output(name)
			elif doctype == "VAT Input Metadata":
				from erpnext_indonesia_localization.api.pajakio import delete_vat_input
				delete_vat_input(name)
			elif doctype == "Withholding Tax Certificate":
				from erpnext_indonesia_localization.api.pajakio import delete_withholding_tax
				delete_withholding_tax(name)
			else:
				raise ValueError(f"Unsupported doctype for delete: {doctype}")
			
			success_count += 1
		except Exception as e:
			failure_count += 1
			errors.append(f"{name}: {str(e)}")
			frappe.log_error(f"Error deleting {doctype} {name}: {str(e)}", "Bulk Operations Error")
	
	return {
		"success_count": success_count,
		"failure_count": failure_count,
		"errors": errors
	}
