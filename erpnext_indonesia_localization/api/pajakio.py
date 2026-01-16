import json
import requests
import frappe
import base64
import re
import time
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from frappe import _
from erpnext_indonesia_localization.utils.api.pajakio_helper import get_pajakio_headers, make_pajakio_request, get_pajakio_url

@frappe.whitelist()
def create_vat_output(doc):
	"""
	Create VAT Output via Pajak.io API.
	Refactored to use make_pajakio_request helper for consistency.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	try:
		url = get_pajakio_url('url_create_vat')
		headers = get_pajakio_headers()
		
		# Populate barangjasa
		barangjasa = []
		for item in doc.barangjasa:
			barangjasa.append({
				"nama": re.sub('<[^<]+?>', '', str(item.nama or '')),
				"jumlah": item.jumlah or 0,
				"harga": item.harga or 0,
				"dpp": item.dpp or 0,
				"diskon": item.diskon or 0,
				"ppn": item.ppn or 0,
				"tarifppnbm": item.tarifppnbm or 0
			})
		
		# Prepare payload
		payload = {
			"autoUploadDjp": doc.autouploaddjp or 0,
			"pengganti": doc.pengganti or 0,
			"nofa": doc.nofa or "",
			"noInvoice": doc.noinvoice or "",
			"kdJenisTransaksi": doc.kdjenistransaksi or "",
			"idKeteranganTambahan": doc.idketerangantambahan or "",
			"barangJasa": barangjasa,
			"lawanTransaksi": {
				"npwp": doc.npwp or "",
				"nikPassport": doc.nikpassport or "",
				"nama": doc.customername or "",
				"alamatJalan": doc.alamatjalan or "",
				"kota": doc.kota or "",
				"telp": doc.telp or ""
			},
			"tanggalFaktur": doc.tanggalfaktur or "",
			"masaPajak": doc.masapajak or "",
			"tahunPajak": doc.tahunpajak or "",
			"tarifPpn": doc.tarifppn or "",
			"terminPembayaran": doc.terminpembayaran or "",
			"terminDpp": doc.termindpp or "",
			"terminPpn": doc.terminppn or "",
			"terminPpnbm": doc.terminppnbm or ""
		}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"create_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') in [200, 201]:
			if 'data' in response_data and 'transactionId' in response_data['data']:
				doc.transactionid = response_data['data']['transactionId']
			doc.status = "To Be Reviewed"
			doc.create_vat_response = response_data.get('message', 'VAT Output created successfully')
			doc.save()
		
		# Log for debugging
		logger = frappe.logger("pajak_io", with_more_info=True, allow_site=True, file_count=10)
		logger.info("----------------------------------")
		logger.debug(f"Request: {payload}")
		logger.debug(f"Response: {response_data}")
		logger.info("##################################")
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def create_vat_output_js(name):
	doc = frappe.get_doc("VAT Output Metadata", name)
	indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")

	class AllowedTo:
		create_vat = indonesia_localization_settings.create_vat_output
		check_detail = indonesia_localization_settings.get_details_vat_output
		create_pdf = indonesia_localization_settings.get_pdf_vat_output

	class RequestStatus:
		uploaded_but_not_processed = doc.transactionid and (doc.status == "To Be Reviewed" or doc.status == "Draft")
		approved_but_no_pdf = doc.status == "Approved" and not doc.vat_output_pdf_response
		pdf_has_been_generated = doc.status == "Received PDF" and doc.vat_output_pdf_response

	if RequestStatus.pdf_has_been_generated:
		message = "PDF has already been generated"
	elif RequestStatus.approved_but_no_pdf:
		message = proceed_to_get_pdf(doc, AllowedTo)
	elif RequestStatus.uploaded_but_not_processed:
		message = proceed_to_get_vat_output_details(doc, AllowedTo)
	elif AllowedTo.create_vat:
		message = create_vat(doc, AllowedTo)
	else:
		message = "Create VAT is turned off in Indonesia Localization Settings"

	return message


def proceed_to_get_pdf(doc, allowed_to):
	if not allowed_to.create_pdf:
		return "Get VAT Output PDF is turned off in Indonesia Localization Settings"

	response_msg = get_pdf_vat_output(doc)
	
	# Validate response structure
	if not isinstance(response_msg, dict):
		doc.status = "Draft"
		doc.vat_output_pdf_response = str(response_msg)
		doc.save()
		return f"Invalid response format: {str(response_msg)}"
	
	doc.vat_output_pdf_response = response_msg.get('message', 'Unknown error')
	try:
		request_code = str(response_msg.get('code', ''))
		pdf_successfully_generated = request_code == "200" and response_msg.get('message') == 'SUCCESS GET PDF VAT OUTPUT'
	except (KeyError, AttributeError, TypeError) as e:
		doc.status = "Draft"
		doc.vat_output_pdf_response = f"Error parsing response: {str(e)}"
		doc.save()
		frappe.log_error(f"Error parsing PDF response: {str(e)}, Response: {response_msg}", "Pajak.io API Error")
		return f"Error parsing response: {str(e)}"

	if not pdf_successfully_generated:
		return "Failed to generate PDF"

	doc.status = "Received PDF"
	message = "PDF has been generated"
	doc.base64 = response_msg['data']['filePdf']
	doc.save()

	return message


def proceed_to_get_vat_output_details(doc, allowed_to):
	if not allowed_to.check_detail:
		return "Get VAT Output Details is turned off in Indonesia Localization Settings"

	response_msg = get_vat_output_detail(doc)
	
	# Validate response structure
	if not isinstance(response_msg, dict):
		doc.status = "Draft"
		doc.save()
		frappe.log_error(f"Invalid response format: {response_msg}", "Pajak.io API Error")
		return f"Invalid response format: {str(response_msg)}"
	
	try:
		request_code = str(response_msg.get('code', ''))
	except (KeyError, AttributeError, TypeError) as e:
		doc.status = "Draft"
		doc.save()
		frappe.log_error(f"Error parsing response: {str(e)}, Response: {response_msg}", "Pajak.io API Error")
		return f"Error parsing response: {str(e)}"

	if request_code != "200":
		doc.status = "Draft"
		message = response_msg.get('message', 'Unknown error')
		doc.save()
		return message

	# Validate data structure
	if 'data' not in response_msg or not response_msg['data'] or not isinstance(response_msg['data'], list):
		doc.status = "Draft"
		doc.save()
		frappe.log_error(f"Invalid data structure in response: {response_msg}", "Pajak.io API Error")
		return "Invalid data structure in API response"
	
	if 'nofa' not in response_msg['data'][0]:
		doc.status = "Draft"
		doc.save()
		frappe.log_error(f"Missing 'nofa' in response data: {response_msg['data']}", "Pajak.io API Error")
		return "Missing 'nofa' in API response"

	doc.status = "Approved"
	doc.nofa = response_msg['data'][0]['nofa']
	try:
		parent_invoice_doc = frappe.get_doc(doc.parent_doctype, doc.noinvoice)
	except frappe.DoesNotExistError:
		message = "Couldn't find the original invoice document for this doctype. Please try to recreate VAT Output Metadata for this document"
		frappe.log_error(message, "Pajak.io API Error")
		return message
	except Exception as e:
		frappe.log_error(f"Error getting parent invoice: {str(e)}", "Pajak.io API Error")
		return f"Error getting parent invoice: {str(e)}"

	doc.get_vat_pdf_response = str(response_msg['data'][0]["status"])
	parent_invoice_doc.nomor_faktur = doc.nofa
	parent_invoice_doc.save()
	doc.save()
	message = "VAT Output Approved"

	if allowed_to.create_pdf:
		create_vat_output_js(doc.name)

	return message


def create_vat(doc, allowed_to):
	response_msg = create_vat_output(doc)
	
	# Validate response structure
	if not isinstance(response_msg, dict):
		doc.create_vat_response = str(response_msg)
		doc.status = 'To Be Reviewed'
		doc.save()
		frappe.log_error(f"Invalid response format: {response_msg}", "Pajak.io API Error")
		return f"Invalid response format: {str(response_msg)}"
	
	try:
		response_code = response_msg.get('code')
		response_message = response_msg.get('message', '')
		vat_has_been_requested = response_code in [200, 201] or doc.transactionid
		draft_faktur_existed = response_code == 400 and response_message == 'Draft Faktur already exist'
	except (KeyError, AttributeError, TypeError) as e:
		doc.create_vat_response = f"Error parsing response: {str(e)}"
		doc.status = 'To Be Reviewed'
		doc.save()
		frappe.log_error(f"Error parsing create_vat response: {str(e)}, Response: {response_msg}", "Pajak.io API Error")
		return f"Error parsing response: {str(e)}"

	if vat_has_been_requested:
		doc.create_vat_response = response_msg['message']
		doc.transactionid = response_msg['data']['transactionId']
		message = "VAT Output Requested"
		doc.save()
		if allowed_to.check_detail:
			create_vat_output_js(doc.name)
	elif draft_faktur_existed:
		doc.status = 'Draft'
		doc.create_vat_response = response_msg[
									  'message'] + " .Please go to your Pajak.io account and retrieve Transaction ID for this invoice"
		message = response_msg['message']
		doc.save()
	else:
		doc.status = 'To Be Reviewed'
		doc.create_vat_response = "Error Code: " + str(response_msg['code']) + " | " + response_msg['message']
		message = response_msg['message']
		doc.save()

	return message


@frappe.whitelist()
def get_vat_output_detail(doc):
	"""
	Get VAT Output detail from Pajak.io API.
	Refactored to use make_pajakio_request helper for consistency.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to get VAT Output detail"))
	
	try:
		url = get_pajakio_url('url_get_vat') + "/" + str(doc.transactionid)
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			context=f"get_vat_output_detail({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			if 'data' in response_data:
				data = response_data['data']
				if isinstance(data, list) and len(data) > 0:
					data = data[0]
				
				if isinstance(data, dict):
					if 'nofa' in data:
						doc.nofa = data['nofa']
					if 'status' in data:
						doc.status = data['status']
					doc.get_vat_pdf_response = response_data.get('message', 'VAT Output detail retrieved successfully')
					doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Output detail {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_pdf_vat_output(doc):
	"""
	Get PDF VAT Output via Pajak.io API.
	Refactored to use make_pajakio_request helper for consistency.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary with PDF data
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to get PDF VAT Output"))
	
	try:
		url = get_pajakio_url('url_get_pdf_vat')
		headers = get_pajakio_headers()
		
		payload = [{"transactionId": doc.transactionid}]
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"get_pdf_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			if 'data' in response_data:
				data = response_data['data']
				if isinstance(data, list) and len(data) > 0:
					data = data[0]
				
				if isinstance(data, dict):
					if 'base64' in data:
						doc.base64 = data['base64']
					if 'pdfUrl' in data:
						doc.pdf_file_url = data['pdfUrl']
					doc.vat_output_pdf_response = response_data.get('message', 'PDF retrieved successfully')
					doc.status = "Received PDF"
					doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting PDF VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise

@frappe.whitelist()
def upload_vat_output(doc):
	"""
	Upload VAT Output to DJP via Pajak.io API.
	Refactored to use make_pajakio_request helper for consistency.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to upload VAT Output"))
	
	try:
		url = get_pajakio_url('url_upload_vat')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"upload_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.vat_upload_success = True
			doc.get_vat_pdf_response = str(response_data.get("message", "VAT Output uploaded successfully"))
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error uploading VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


# ============================================================================
# Verification API Functions
# ============================================================================

@frappe.whitelist()
def verify_npwp(npwp: str) -> Dict[str, Any]:
	"""
	Verify NPWP via Pajak.io API.
	
	Args:
		npwp: NPWP number to verify (15 digits, can include dots/dashes)
		
	Returns:
		Dictionary with verification result:
		{
			"valid": bool,
			"message": str,
			"data": dict (if valid)
		}
	"""
	import re
	
	# Clean NPWP format
	npwp_clean = re.sub(r'[.\-]', '', str(npwp))
	
	# Basic format validation
	if not re.match(r'^\d{15}$', npwp_clean):
		return {
			"valid": False,
			"message": _("NPWP format is invalid. Must be 15 digits."),
			"data": None
		}
	
	try:
		url = get_pajakio_url('url_verify_npwp')
		headers = get_pajakio_headers()
		
		payload = {"npwp": npwp_clean}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"verify_npwp({npwp_clean})"
		)
		
		# Check response code
		if response_data.get('code') == 200:
			return {
				"valid": True,
				"message": response_data.get('message', 'NPWP is valid'),
				"data": response_data.get('data', {})
			}
		else:
			return {
				"valid": False,
				"message": response_data.get('message', 'NPWP verification failed'),
				"data": None
			}
			
	except frappe.ValidationError as e:
		return {
			"valid": False,
			"message": str(e),
			"data": None
		}
	except Exception as e:
		frappe.log_error(f"Error verifying NPWP {npwp}: {str(e)}", "Pajak.io Verification Error")
		return {
			"valid": False,
			"message": _("Error during NPWP verification: {0}").format(str(e)),
			"data": None
		}


@frappe.whitelist()
def verify_nik(nik: str) -> Dict[str, Any]:
	"""
	Verify NIK via Pajak.io API.
	
	Args:
		nik: NIK number to verify (16 digits, can include dots/dashes)
		
	Returns:
		Dictionary with verification result:
		{
			"valid": bool,
			"message": str,
			"data": dict (if valid)
		}
	"""
	import re
	
	# Clean NIK format
	nik_clean = re.sub(r'[.\-]', '', str(nik))
	
	# Basic format validation
	if not re.match(r'^\d{16}$', nik_clean):
		return {
			"valid": False,
			"message": _("NIK format is invalid. Must be 16 digits."),
			"data": None
		}
	
	try:
		url = get_pajakio_url('url_verify_nik')
		headers = get_pajakio_headers()
		
		payload = {"nik": nik_clean}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"verify_nik({nik_clean})"
		)
		
		# Check response code
		if response_data.get('code') == 200:
			return {
				"valid": True,
				"message": response_data.get('message', 'NIK is valid'),
				"data": response_data.get('data', {})
			}
		else:
			return {
				"valid": False,
				"message": response_data.get('message', 'NIK verification failed'),
				"data": None
			}
			
	except frappe.ValidationError as e:
		return {
			"valid": False,
			"message": str(e),
			"data": None
		}
	except Exception as e:
		frappe.log_error(f"Error verifying NIK {nik}: {str(e)}", "Pajak.io Verification Error")
		return {
			"valid": False,
			"message": _("Error during NIK verification: {0}").format(str(e)),
			"data": None
		}


# ============================================================================
# Enhanced VAT Output API Functions
# ============================================================================

@frappe.whitelist()
def update_vat_output(doc, update_data):
	"""
	Update VAT Output via Pajak.io API.
	
	Args:
		doc: VAT Output Metadata document or document name
		update_data: Dictionary with fields to update
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to update VAT Output"))
	
	try:
		url = get_pajakio_url('url_update_vat')
		headers = get_pajakio_headers()
		
		# Prepare update payload
		payload = {
			"transactionId": doc.transactionid,
			**update_data
		}
		
		response_data = make_pajakio_request(
			method="PUT",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"update_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.create_vat_response = response_data.get('message', 'VAT Output updated successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error updating VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def cancel_vat_output(doc):
	"""
	Cancel VAT Output via Pajak.io API.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to cancel VAT Output"))
	
	try:
		url = get_pajakio_url('url_cancel_vat')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"cancel_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Cancelled"
			doc.create_vat_response = response_data.get('message', 'VAT Output cancelled successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error cancelling VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_vat_output(doc):
	"""
	Delete VAT Output via Pajak.io API.
	
	Args:
		doc: VAT Output Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to delete VAT Output"))
	
	try:
		url = get_pajakio_url('url_delete_vat')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"delete_vat_output({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Deleted"
			doc.create_vat_response = response_data.get('message', 'VAT Output deleted successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting VAT Output {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_list_vat_output(filters=None, page=1, per_page=100):
	"""
	Get list of VAT Outputs from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of VAT Outputs
	"""
	try:
		url = get_pajakio_url('url_list_vat')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="get_list_vat_output"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Output list: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_multiple_vat_output(transaction_ids):
	"""
	Delete multiple VAT Outputs via Pajak.io API.
	
	Args:
		transaction_ids: List of transaction IDs to delete
		
	Returns:
		API response dictionary
	"""
	if not transaction_ids or not isinstance(transaction_ids, list):
		raise frappe.ValidationError(_("Transaction IDs list is required"))
	
	try:
		url = get_pajakio_url('url_delete_vat')
		headers = get_pajakio_headers()
		
		payload = {"transactionIds": transaction_ids}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"delete_multiple_vat_output({len(transaction_ids)} items)"
		)
		
		# Update documents if successful
		if response_data.get('code') == 200:
			for transaction_id in transaction_ids:
				vom_list = frappe.get_all(
					"VAT Output Metadata",
					filters={"transactionid": transaction_id},
					pluck="name"
				)
				for vom_name in vom_list:
					frappe.set_value("VAT Output Metadata", vom_name, {
						"status": "Deleted",
						"create_vat_response": response_data.get('message', 'VAT Output deleted successfully')
					})
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting multiple VAT Outputs: {str(e)}", "Pajak.io API Error")
		raise


# ============================================================================
# VAT Input API Functions
# ============================================================================

@frappe.whitelist()
def create_vat_input(doc):
	"""
	Create VAT Input via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	try:
		url = get_pajakio_url('url_create_vat_input')
		headers = get_pajakio_headers()
		
		# Prepare barangjasa
		barangjasa = []
		for item in doc.barangjasa:
			barangjasa.append({
				"nama": re.sub('<[^<]+?>', '', str(item.nama or '')),
				"jumlah": item.jumlah or 0,
				"harga": item.harga or 0,
				"dpp": item.dpp or 0,
				"diskon": item.diskon or 0,
				"ppn": item.ppn or 0,
				"tarifppnbm": item.tarifppnbm or 0
			})
		
		# Prepare payload
		payload = {
			"nofa": doc.nofa or "",
			"noInvoice": doc.noinvoice or "",
			"kdJenisTransaksi": doc.kdjenistransaksi or "",
			"idKeteranganTambahan": doc.idketerangantambahan or "",
			"barangJasa": barangjasa,
			"lawanTransaksi": {
				"npwp": doc.npwp or "",
				"nikPassport": doc.nikpassport or "",
				"nama": doc.suppliername or "",
				"alamatJalan": doc.alamatjalan or "",
				"kota": doc.kota or "",
				"telp": doc.telp or ""
			},
			"tanggalFaktur": doc.tanggalfaktur or "",
			"masaPajak": doc.masapajak or "",
			"tahunPajak": doc.tahunpajak or "",
			"tarifPpn": doc.tarifppn or "",
			"terminPembayaran": doc.terminpembayaran or "",
			"terminDpp": doc.termindpp or "",
			"terminPpn": doc.terminppn or "",
			"terminPpnbm": doc.terminppnbm or ""
		}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"create_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') in [200, 201]:
			if 'data' in response_data and 'transactionId' in response_data['data']:
				doc.transactionid = response_data['data']['transactionId']
			doc.status = "To Be Reviewed"
			doc.create_vat_response = response_data.get('message', 'VAT Input created successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_list_vat_input(filters=None, page=1, per_page=100):
	"""
	Get list of VAT Inputs from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of VAT Inputs
	"""
	try:
		url = get_pajakio_url('url_list_vat_input')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="get_list_vat_input"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Input list: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_detail_vat_input(doc):
	"""
	Get VAT Input detail from Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to get VAT Input detail"))
	
	try:
		url = get_pajakio_url('url_get_vat_input') + "/" + str(doc.transactionid)
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			context=f"get_detail_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200 and 'data' in response_data:
			data = response_data['data']
			if isinstance(data, list) and len(data) > 0:
				data = data[0]
			
			if isinstance(data, dict):
				if 'nofa' in data:
					doc.nofa = data['nofa']
				if 'status' in data:
					doc.status = data['status']
				doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Input detail {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def update_vat_input(doc, update_data):
	"""
	Update VAT Input via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		update_data: Dictionary with fields to update
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to update VAT Input"))
	
	try:
		url = get_pajakio_url('url_update_vat_input')
		headers = get_pajakio_headers()
		
		payload = {
			"transactionId": doc.transactionid,
			**update_data
		}
		
		response_data = make_pajakio_request(
			method="PUT",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"update_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.create_vat_response = response_data.get('message', 'VAT Input updated successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error updating VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def cancel_vat_input(doc):
	"""
	Cancel VAT Input via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to cancel VAT Input"))
	
	try:
		url = get_pajakio_url('url_cancel_vat_input')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"cancel_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Cancelled"
			doc.create_vat_response = response_data.get('message', 'VAT Input cancelled successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error cancelling VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_vat_input(doc):
	"""
	Delete VAT Input via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to delete VAT Input"))
	
	try:
		url = get_pajakio_url('url_delete_vat_input')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"delete_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Deleted"
			doc.create_vat_response = response_data.get('message', 'VAT Input deleted successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def upload_vat_input(doc):
	"""
	Upload VAT Input to DJP via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to upload VAT Input"))
	
	try:
		url = get_pajakio_url('url_upload_vat_input')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"upload_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.vat_upload_success = True
			doc.create_vat_response = response_data.get('message', 'VAT Input uploaded successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error uploading VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def change_credit_vat_input(doc, credit_status):
	"""
	Change credit status of VAT Input via Pajak.io API.
	
	Args:
		doc: VAT Input Metadata document or document name
		credit_status: New credit status
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Input Metadata", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to change credit status"))
	
	try:
		url = get_pajakio_url('url_change_credit_vat_input')
		headers = get_pajakio_headers()
		
		payload = {
			"transactionId": doc.transactionid,
			"creditStatus": credit_status
		}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"change_credit_vat_input({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.create_vat_response = response_data.get('message', 'Credit status changed successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error changing credit status for VAT Input {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def prepopulated_vat_input(supplier_npwp, filters=None):
	"""
	Get prepopulated VAT Input data from DJP via Pajak.io API.
	
	Args:
		supplier_npwp: Supplier NPWP to fetch faktur for
		filters: Additional filters (optional)
		
	Returns:
		API response dictionary with list of available faktur
	"""
	try:
		url = get_pajakio_url('url_prepopulated_vat_input')
		headers = get_pajakio_headers()
		
		params = {
			"npwp": supplier_npwp
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context=f"prepopulated_vat_input({supplier_npwp})"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting prepopulated VAT Input for NPWP {supplier_npwp}: {str(e)}", "Pajak.io API Error")
		raise


# ============================================================================
# Withholding Tax API Functions
# ============================================================================

@frappe.whitelist()
def create_withholding_tax(doc):
	"""
	Create Withholding Tax (e-Bupot) via Pajak.io API.
	
	Args:
		doc: Withholding Tax Certificate document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Withholding Tax Certificate", doc)
	
	try:
		url = get_pajakio_url('url_create_withholding_tax')
		headers = get_pajakio_headers()
		
		# Prepare items
		items = []
		for item in doc.ebupot_items:
			items.append({
				"itemCode": item.item_code or "",
				"itemName": item.item_name or "",
				"taxCode": item.tax_code or "",
				"taxBase": item.tax_base or 0,
				"taxRate": item.tax_rate or 0,
				"taxAmount": item.tax_amount or 0
			})
		
		# Prepare payload
		payload = {
			"certificateNumber": doc.certificate_number or "",
			"certificateDate": str(doc.certificate_date) if doc.certificate_date else "",
			"supplierNpwp": doc.supplier_npwp or "",
			"supplierName": doc.supplier_name or "",
			"taxType": doc.tax_type or "",
			"taxRate": doc.tax_rate or 0,
			"taxBase": doc.tax_base or 0,
			"taxAmount": doc.tax_amount or 0,
			"items": items
		}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"create_withholding_tax({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') in [200, 201]:
			if 'data' in response_data and 'transactionId' in response_data['data']:
				doc.transactionid = response_data['data']['transactionId']
			doc.status = "Submitted"
			doc.xml_export_status = "Exported"
			doc.create_vat_response = response_data.get('message', 'Withholding Tax created successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating Withholding Tax {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def update_withholding_tax(doc, update_data):
	"""
	Update Withholding Tax via Pajak.io API.
	
	Args:
		doc: Withholding Tax Certificate document or document name
		update_data: Dictionary with fields to update
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Withholding Tax Certificate", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to update Withholding Tax"))
	
	try:
		url = get_pajakio_url('url_update_withholding_tax')
		headers = get_pajakio_headers()
		
		payload = {
			"transactionId": doc.transactionid,
			**update_data
		}
		
		response_data = make_pajakio_request(
			method="PUT",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"update_withholding_tax({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.create_vat_response = response_data.get('message', 'Withholding Tax updated successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error updating Withholding Tax {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def upload_withholding_tax(doc):
	"""
	Upload Withholding Tax to DJP via Pajak.io API.
	
	Args:
		doc: Withholding Tax Certificate document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Withholding Tax Certificate", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to upload Withholding Tax"))
	
	try:
		url = get_pajakio_url('url_upload_withholding_tax')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"upload_withholding_tax({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.xml_export_status = "Exported"
			doc.create_vat_response = response_data.get('message', 'Withholding Tax uploaded successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error uploading Withholding Tax {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_withholding_tax(doc):
	"""
	Delete Withholding Tax via Pajak.io API.
	
	Args:
		doc: Withholding Tax Certificate document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("Withholding Tax Certificate", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to delete Withholding Tax"))
	
	try:
		url = get_pajakio_url('url_delete_withholding_tax')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"delete_withholding_tax({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Deleted"
			doc.xml_export_status = "Failed"
			doc.create_vat_response = response_data.get('message', 'Withholding Tax deleted successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting Withholding Tax {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_list_withholding_tax(filters=None, page=1, per_page=100):
	"""
	Get list of Withholding Taxes from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of Withholding Taxes
	"""
	try:
		url = get_pajakio_url('url_list_withholding_tax')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="get_list_withholding_tax"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting Withholding Tax list: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_status_bupot(transaction_id):
	"""
	Get status of e-Bupot from DJP via Pajak.io API.
	
	Args:
		transaction_id: Transaction ID of the Withholding Tax
		
	Returns:
		API response dictionary with status
	"""
	try:
		url = get_pajakio_url('url_get_status_bupot')
		headers = get_pajakio_headers()
		
		params = {"transactionId": transaction_id}
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context=f"get_status_bupot({transaction_id})"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting e-Bupot status for transaction {transaction_id}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_code_of_type():
	"""
	Get master data for kode objek pajak from Pajak.io API.
	
	Returns:
		API response dictionary with list of tax codes
	"""
	try:
		url = get_pajakio_url('url_get_code_of_type')
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			context="get_code_of_type"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting code of type: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def create_income_recipient(recipient_data):
	"""
	Create Income Recipient via Pajak.io API.
	
	Args:
		recipient_data: Dictionary with income recipient data
		
	Returns:
		API response dictionary
	"""
	try:
		url = get_pajakio_url('url_create_income_recipient')
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=recipient_data,
			context="create_income_recipient"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating income recipient: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def list_income_recipient(filters=None, page=1, per_page=100):
	"""
	List Income Recipients from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of income recipients
	"""
	try:
		url = get_pajakio_url('url_list_income_recipient')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="list_income_recipient"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error listing income recipients: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def update_income_recipient(recipient_id, update_data):
	"""
	Update Income Recipient via Pajak.io API.
	
	Args:
		recipient_id: Income Recipient ID
		update_data: Dictionary with fields to update
		
	Returns:
		API response dictionary
	"""
	try:
		url = get_pajakio_url('url_update_income_recipient') + "/" + str(recipient_id)
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="PUT",
			url=url,
			headers=headers,
			json_data=update_data,
			context=f"update_income_recipient({recipient_id})"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error updating income recipient {recipient_id}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_income_recipient(recipient_id):
	"""
	Delete Income Recipient via Pajak.io API.
	
	Args:
		recipient_id: Income Recipient ID
		
	Returns:
		API response dictionary
	"""
	try:
		url = get_pajakio_url('url_delete_income_recipient') + "/" + str(recipient_id)
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="DELETE",
			url=url,
			headers=headers,
			context=f"delete_income_recipient({recipient_id})"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting income recipient {recipient_id}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def create_signer(signer_data):
	"""
	Create Signer via Pajak.io API.
	
	Args:
		signer_data: Dictionary with signer data
		
	Returns:
		API response dictionary
	"""
	try:
		url = get_pajakio_url('url_create_signer')
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=signer_data,
			context="create_signer"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating signer: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def list_signer(filters=None, page=1, per_page=100):
	"""
	List Signers from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of signers
	"""
	try:
		url = get_pajakio_url('url_list_signer')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="list_signer"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error listing signers: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def set_active_signer(signer_id):
	"""
	Set active signer via Pajak.io API.
	
	Args:
		signer_id: Signer ID to set as active
		
	Returns:
		API response dictionary
	"""
	try:
		url = get_pajakio_url('url_set_active_signer')
		headers = get_pajakio_headers()
		
		payload = {"signerId": signer_id}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"set_active_signer({signer_id})"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error setting active signer {signer_id}: {str(e)}", "Pajak.io API Error")
		raise


# ============================================================================
# VAT Output Return API Functions
# ============================================================================

@frappe.whitelist()
def create_vat_output_return(doc):
	"""
	Create VAT Output Return via Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	try:
		url = get_pajakio_url('url_create_vat_output_return')
		headers = get_pajakio_headers()
		
		# Prepare barangjasa
		barangjasa = []
		for item in doc.barangjasa:
			barangjasa.append({
				"nama": re.sub('<[^<]+?>', '', str(item.nama or '')),
				"jumlah": item.jumlah or 0,
				"harga": item.harga or 0,
				"dpp": item.dpp or 0,
				"diskon": item.diskon or 0,
				"ppn": item.ppn or 0,
				"tarifppnbm": item.tarifppnbm or 0
			})
		
		# Prepare payload
		payload = {
			"originalTransactionId": doc.original_vat_output if hasattr(doc, 'original_vat_output') else "",
			"nofa": doc.nofa or "",
			"noInvoice": doc.noinvoice or "",
			"kdJenisTransaksi": doc.kdjenistransaksi or "",
			"idKeteranganTambahan": doc.idketerangantambahan or "",
			"returnReason": doc.return_reason or "",
			"barangJasa": barangjasa,
			"lawanTransaksi": {
				"npwp": doc.npwp or "",
				"nikPassport": doc.nikpassport or "",
				"nama": doc.customername or "",
				"alamatJalan": doc.alamatjalan or "",
				"kota": doc.kota or "",
				"telp": doc.telp or ""
			},
			"tanggalFaktur": doc.tanggalfaktur or "",
			"masaPajak": doc.masapajak or "",
			"tahunPajak": doc.tahunpajak or "",
			"tarifPpn": doc.tarifppn or "",
			"terminPembayaran": doc.terminpembayaran or "",
			"terminDpp": doc.termindpp or "",
			"terminPpn": doc.terminppn or "",
			"terminPpnbm": doc.terminppnbm or ""
		}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"create_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') in [200, 201]:
			if 'data' in response_data and 'transactionId' in response_data['data']:
				doc.transactionid = response_data['data']['transactionId']
			doc.status = "To Be Reviewed"
			doc.create_vat_response = response_data.get('message', 'VAT Output Return created successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error creating VAT Output Return {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_list_vat_output_return(filters=None, page=1, per_page=100):
	"""
	Get list of VAT Output Returns from Pajak.io API.
	
	Args:
		filters: Dictionary with filter parameters (optional)
		page: Page number for pagination
		per_page: Number of items per page
		
	Returns:
		API response dictionary with list of VAT Output Returns
	"""
	try:
		url = get_pajakio_url('url_list_vat_output_return')
		headers = get_pajakio_headers()
		
		params = {
			"page": page,
			"per_page": per_page
		}
		
		if filters:
			params.update(filters)
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			params=params,
			context="get_list_vat_output_return"
		)
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Output Return list: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def get_detail_vat_output_return(doc):
	"""
	Get VAT Output Return detail from Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to get VAT Output Return detail"))
	
	try:
		url = get_pajakio_url('url_get_vat_output_return') + "/" + str(doc.transactionid)
		headers = get_pajakio_headers()
		
		response_data = make_pajakio_request(
			method="GET",
			url=url,
			headers=headers,
			context=f"get_detail_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200 and 'data' in response_data:
			data = response_data['data']
			if isinstance(data, list) and len(data) > 0:
				data = data[0]
			
			if isinstance(data, dict):
				if 'nofa' in data:
					doc.nofa = data['nofa']
				if 'status' in data:
					doc.status = data['status']
				doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error getting VAT Output Return detail {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def update_vat_output_return(doc, update_data):
	"""
	Update VAT Output Return via Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		update_data: Dictionary with fields to update
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to update VAT Output Return"))
	
	try:
		url = get_pajakio_url('url_update_vat_output_return')
		headers = get_pajakio_headers()
		
		payload = {
			"transactionId": doc.transactionid,
			**update_data
		}
		
		response_data = make_pajakio_request(
			method="PUT",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"update_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.create_vat_response = response_data.get('message', 'VAT Output Return updated successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error updating VAT Output Return {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def cancel_vat_output_return(doc):
	"""
	Cancel VAT Output Return via Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to cancel VAT Output Return"))
	
	try:
		url = get_pajakio_url('url_cancel_vat_output_return')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"cancel_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Cancelled"
			doc.create_vat_response = response_data.get('message', 'VAT Output Return cancelled successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error cancelling VAT Output Return {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def delete_vat_output_return(doc):
	"""
	Delete VAT Output Return via Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to delete VAT Output Return"))
	
	try:
		url = get_pajakio_url('url_delete_vat_output_return')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"delete_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.status = "Deleted"
			doc.create_vat_response = response_data.get('message', 'VAT Output Return deleted successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error deleting VAT Output Return {doc.name}: {str(e)}", "Pajak.io API Error")
		raise


@frappe.whitelist()
def upload_vat_output_return(doc):
	"""
	Upload VAT Output Return to DJP via Pajak.io API.
	
	Args:
		doc: VAT Output Return document or document name
		
	Returns:
		API response dictionary
	"""
	if isinstance(doc, str):
		doc = frappe.get_doc("VAT Output Return", doc)
	
	if not doc.transactionid:
		raise frappe.ValidationError(_("Transaction ID is required to upload VAT Output Return"))
	
	try:
		url = get_pajakio_url('url_upload_vat_output_return')
		headers = get_pajakio_headers()
		
		payload = {"transactionId": doc.transactionid}
		
		response_data = make_pajakio_request(
			method="POST",
			url=url,
			headers=headers,
			json_data=payload,
			context=f"upload_vat_output_return({doc.name})"
		)
		
		# Update document if successful
		if response_data.get('code') == 200:
			doc.vat_upload_success = True
			doc.create_vat_response = response_data.get('message', 'VAT Output Return uploaded successfully')
			doc.save()
		
		return response_data
		
	except Exception as e:
		frappe.log_error(f"Error uploading VAT Output Return {doc.name}: {str(e)}", "Pajak.io API Error")
		raise
