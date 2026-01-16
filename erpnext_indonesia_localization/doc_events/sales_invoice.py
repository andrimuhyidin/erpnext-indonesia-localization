import frappe
from frappe.utils import cint
from frappe import _
import re
from erpnext_indonesia_localization.api import create_vat_output, verify_npwp, verify_nik
from erpnext_indonesia_localization.utils.data import get_tax_prefix_code


# Procedures to generate VOM doctype
@frappe.whitelist()
def procedure_to_create_vom(name, doctype):
	doc = frappe.get_doc(doctype, name)
	indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
	NOFA_SOURCE = indonesia_localization_settings.tax_invoice_number_source.upper()
	PAJAKIO_NOFA = 'PAJAK.IO'
	INHOUSE_NOFA = 'TAX INVOICE NUMBER DOCTYPE'

	title = 'Error Registering Tax Invoice Number'
	message = "Please check Indonesia Localization Settings configurations"

	if NOFA_SOURCE == PAJAKIO_NOFA:
		success_status, message = create_vat_output_metadata(doc, indonesia_localization_settings)
		if success_status:
			title = 'VAT Output Metadata Created'
		else:
			title = 'Error Registering Tax Invoice Number'
	elif NOFA_SOURCE == INHOUSE_NOFA:
		success_status, message = link_tax_invoice_number(doc)
		if success_status:
			title = 'Succesfully Registered Tax Invoice Number'
			create_vat_output_metadata(doc, indonesia_localization_settings)
	return message, title


@frappe.whitelist()
def create_vom_via_button(name, doctype):
	message, title = procedure_to_create_vom(name, doctype)
	frappe.msgprint(
		msg=message,
		title=title
	)

	return


@frappe.whitelist()
def create_vom_via_cronjob(name, doctype):
	procedure_to_create_vom(name, doctype)

	return


@frappe.whitelist()
def link_tax_invoice_number(doc):
	if doc.nomor_faktur:
		incorrectly_linked = frappe.db.get_value('Tax Invoice Number', doc.nomor_faktur, 'sales_invoice') != doc.name
		if incorrectly_linked:
			message = 'Tax Invoice Number already linked to another SI'
			return False, message
		return True

	available_nofa = frappe.db.get_list('Tax Invoice Number', filters={'status': 'Available'}, pluck='name')
	if not available_nofa:
		message = 'No Tax Invoice Number available'
		return False, message

	nofa = available_nofa[0]

	frappe.db.set_value('Tax Invoice Number', nofa, 'sales_invoice', doc.name)
	frappe.db.set_value('Tax Invoice Number', nofa, 'status', 'Used')
	frappe.db.set_value('Tax Invoice Number', nofa, 'linked_datetime', frappe.utils.now())

	message = 'Successfully linked invoice to tax invoice number'

	return True, message


def check_mandatory_fields(metadata_doc):
	empty_mandatory_fields = []
	mandatory_fields = ['kdjenistransaksi', "nama", "alamatjalan", "tarifppn", "terminpembayaran"]
	mandatory_item_fields = ['nama', 'harga', 'jumlah', 'dpp', 'ppn']

	for field in mandatory_fields:
		if not metadata_doc.get(field):
			empty_mandatory_fields.append(field)

	for item in metadata_doc.barangjasa:
		for field in mandatory_item_fields:
			if not item.get(field):
				empty_mandatory_fields.append(field + ' item')

	safe_to_proceed = True

	if len(empty_mandatory_fields) > 0:
		safe_to_proceed = False

	return safe_to_proceed, empty_mandatory_fields


@frappe.whitelist()
def create_vat_output_metadata(doc, indonesia_localization_settings):
	metadata_doc = frappe.new_doc('VAT Output Metadata')

	NOFA_SOURCE = indonesia_localization_settings.tax_invoice_number_source.upper()
	INHOUSE_NOFA = 'TAX INVOICE NUMBER DOCTYPE'
	METADATA_DRAFT_STATUS = 'To Be Reviewed'
	customer_details = frappe.get_doc("Customer", doc.customer)

	if not customer_details.customer_primary_address:
		message = "Please complete primary address for " + str(customer_details.customer_name)
		return False, message
	customer_address = frappe.get_doc("Address", customer_details.customer_primary_address)

	if not customer_details.mobile_no:
		message = "Please complete primary contact number for " + str(customer_details.customer_name)
		return False, message
	
	# Verify customer tax ID if auto-verify is enabled
	if hasattr(indonesia_localization_settings, 'auto_verify_tax_id') and indonesia_localization_settings.auto_verify_tax_id:
		if customer_details.tax_id and customer_details.customer_id_type == "TIN":
			try:
				verification_result = verify_npwp(customer_details.tax_id)
				if not verification_result.get('valid'):
					message = f"Customer NPWP verification failed: {verification_result.get('message', 'Invalid NPWP')}"
					frappe.log_error(message, "NPWP Verification Failed")
					# Continue with warning instead of failing
					frappe.msgprint(_("Warning: {0}").format(message), indicator="orange", title=_("NPWP Verification Warning"))
			except Exception as e:
				# Log error but don't block creation
				frappe.log_error(f"Error verifying NPWP during VAT Output creation: {str(e)}", "NPWP Verification Error")
		
		if customer_details.customer_id_type == "National ID" and (customer_details.nik or customer_details.customer_id_number):
			nik_value = customer_details.nik or customer_details.customer_id_number
			try:
				verification_result = verify_nik(nik_value)
				if not verification_result.get('valid'):
					message = f"Customer NIK verification failed: {verification_result.get('message', 'Invalid NIK')}"
					frappe.log_error(message, "NIK Verification Failed")
					frappe.msgprint(_("Warning: {0}").format(message), indicator="orange", title=_("NIK Verification Warning"))
			except Exception as e:
				frappe.log_error(f"Error verifying NIK during VAT Output creation: {str(e)}", "NIK Verification Error")

	if doc.nomor_faktur and NOFA_SOURCE == INHOUSE_NOFA:
		metadata_doc.nofa = doc.nomor_faktur

	metadata_doc.autouploaddjp = indonesia_localization_settings.autouploaddjp
	metadata_doc.noinvoice = doc.name

	if doc.kdjenistransaksi:
		metadata_doc.kdjenistransaksi = doc.kdjenistransaksi.strip()
	else:
		kode_pajak = doc.kode_pajak.split("-")
		metadata_doc.kdjenistransaksi = kode_pajak[0].strip()

	if not doc.idketerangantambahan:
		metadata_doc.idketerangantambahan = doc.idketerangantambahan
	else:
		metadata_doc.idketerangantambahan = doc.idketerangantambahan.strip()

	metadata_doc.tanggalfaktur = frappe.utils.formatdate(frappe.utils.today(), "YYYY-mm-dd")
	metadata_doc.masapajak = frappe.utils.formatdate(frappe.utils.today(), "mm").strip()
	metadata_doc.tahunpajak = frappe.utils.formatdate(frappe.utils.today(), "yyyy").strip()
	metadata_doc.parent_doctype = doc.doctype

	tariff = 0
	for account_head in doc.taxes:
		tariff += cint(account_head.rate)

	metadata_doc.tarifppn = tariff
	metadata_doc.termindpp = doc.termin_dpp
	metadata_doc.terminppn = doc.termin_ppn
	metadata_doc.terminppnbm = doc.termin_ppnbm

	if doc.terminpembayaran:
		metadata_doc.terminpembayaran = doc.terminpembayaran.strip()
	else:
		termin = doc.invoice_payment_type.split("-")
		metadata_doc.terminpembayaran = termin[0].strip()

	for item in doc.items:
		metadata_doc.append('barangjasa', {
			"nama": item.description,
			"jumlah": item.qty,
			"harga": item.rate,
			"dpp": item.qty * item.rate,
			"ppn": (item.amount * (tariff / 100)),
			"tarifppnbm": 0
		})

	metadata_doc.npwp = doc.tax_id.replace('.', '')
	metadata_doc.nikpassport = None
	metadata_doc.nama = doc.customer
	metadata_doc.alamatjalan = customer_details.company_address_tax_id
	metadata_doc.kota = customer_address.city
	metadata_doc.telp = customer_details.mobile_no
	metadata_doc.status = METADATA_DRAFT_STATUS

	safe_to_proceed, empty_mandatory_fields = check_mandatory_fields(metadata_doc)

	if not safe_to_proceed:
		message = 'Required Pajak.io API field(s) that are still empty: ' + ', '.join(empty_mandatory_fields)
		return False, message

	metadata_doc.save()

	if indonesia_localization_settings.auto_call_pajakios_api:
		create_vat_output(metadata_doc)
	message = "Successfully Registered Tax Invoice Number"

	return True, message


def set_tin_status_before_cancel_si(si_doc, method=None):
	if si_doc.tax_invoice_number:
		if frappe.get_value("Customer", si_doc.customer, "customer_pkp"):
			# Fix: Use frappe.get_all() instead of frappe.get_value() with dict filter for v16 compatibility
			tin_result = frappe.get_all("Tax Invoice Number", 
				filters={"linked_si": si_doc.name}, 
				fields=["name"], 
				limit=1
			)
			tin_name = tin_result[0].name if tin_result else None

			tin_doc = frappe.get_doc("Tax Invoice Number", tin_name)
			tin_doc.rollback_tin_to_available(si_doc)

			tin_exporter_item = frappe.db.exists("Tax Invoice Exporter Item", {
				"sales_invoice": si_doc.name
			})
			frappe.db.set_value(
				"Tax Invoice Exporter Item",
				tin_exporter_item,
				'is_invoice_cancelled',
				True,
				update_modified=False
			)
		else:
			# Fix: Use frappe.get_all() instead of frappe.get_value() with dict filter for v16 compatibility
			list_result = frappe.get_all("List of Sales Invoice",
				filters={"sales_invoice_id": si_doc.name},
				fields=["parent"],
				limit=1
			)
			tin_name = list_result[0].parent if list_result else None
			tin_doc = frappe.get_doc("Tax Invoice Number", tin_name)

			tin_exporter_item = frappe.db.exists("Tax Invoice Exporter Item", {
				"sales_invoice": si_doc.name
			})

			frappe.db.set_value(
				"Tax Invoice Exporter Item",
				tin_exporter_item,
				'is_invoice_cancelled',
				True,
				update_modified=False
			)

			for invoice in tin_doc.list_of_sales_invoice:
				if invoice.sales_invoice_id == si_doc.name:
					invoice.is_invoice_cancelled = 1

			if check_if_all_invoice_cancelled(tin=tin_doc):
				tin_doc.rollback_tin_to_available(si_doc)
			else:
				tin_doc.tax_invoice_number = "011" + tin_doc.tax_invoice_number[3:]
				tin_doc.save()

		frappe.msgprint(
			msg=f'Tax Invoice Number {si_doc.tax_invoice_number} has been unlinked',
			title='Notification',
			indicator= 'green'
		)


def set_si_had_tin_before(si_doc, _):
	if si_doc.tax_invoice_number:
		si_doc.db_set("custom_si_had_tin_before", 1)


def check_if_all_invoice_cancelled(tin):
	for invoice in tin.list_of_sales_invoice:
		if invoice.is_invoice_cancelled == 0:
			return False

	return True


def calculate_other_tax_base_amount_and_total(doc, method):
	if doc.taxes_and_charges:
		# Fix: Use frappe.get_all() instead of frappe.get_value() with dict filter for v16 compatibility
		tax_template_result = frappe.get_all("Sales Taxes and Charges",
			filters={"parent": doc.taxes_and_charges, "idx": 1},
			fields=["use_temporary_rate", "rate", "temporary_rate"],
			limit=1
		)
		tax_template_doc = tax_template_result[0] if tax_template_result else None
		doc.total_other_tax_base = 0
		doc.total_luxury_goods_tax = 0

		if tax_template_doc and tax_template_doc.use_temporary_rate:
			for item in doc.items:
				item.other_tax_base_amount = item.net_amount * tax_template_doc.rate / tax_template_doc.temporary_rate
				item.vat_amount = item.other_tax_base_amount * tax_template_doc.temporary_rate / 100
				doc.total_other_tax_base += item.other_tax_base_amount
				doc.total_luxury_goods_tax += item.luxury_goods_tax_amount
		else:
			for item in doc.items:
				item.vat_amount = item.net_amount * tax_template_doc.rate / 100
				doc.total_other_tax_base += item.net_amount
				doc.total_luxury_goods_tax += item.luxury_goods_tax_amount


def set_sales_taxes_template_values(doc, method):
	fields_to_sync = ['transaction_code', 'tax_additional_info', 'tax_facility_stamp']

	if doc.taxes_and_charges:
		taxes_template = frappe.db.get_value(
			"Sales Taxes and Charges Template",
			doc.taxes_and_charges,
			['transaction_code', 'tax_additional_info', 'tax_facility_stamp'],
			as_dict=True
		)
	else:
		# Fix: Use frappe.get_all() instead of frappe.db.get_value() with dict filter for v16 compatibility
		taxes_template_result = frappe.get_all(
			"Sales Taxes and Charges Template",
			filters={
				"company": doc.company,
				"is_default": True
			},
			fields=fields_to_sync,
			limit=1
		)
		taxes_template = taxes_template_result[0] if taxes_template_result else None

	if taxes_template:
		for field in fields_to_sync:
			if not doc.get(field):
				doc.set(field, taxes_template.get(field))


def validate_tax_data_formats(doc, method):
	"""
	Validate NPWP, NIK, NITKU formats and date consistency.
	"""
	errors = []
	
	# Validate customer tax data if customer exists
	if doc.customer:
		customer_doc = frappe.get_doc("Customer", doc.customer)
		
		# Validate NPWP format (15 digits, can include dots and dashes)
		if customer_doc.tax_id:
			npwp_clean = re.sub(r'[.\-]', '', customer_doc.tax_id)
			if not re.match(r'^\d{15}$', npwp_clean):
				errors.append(_("NPWP format is invalid. NPWP must be 15 digits. Current value: {0}").format(customer_doc.tax_id))
		
		# Validate NIK format (16 digits) if customer is not PKP
		if not customer_doc.customer_pkp and customer_doc.nik:
			nik_clean = re.sub(r'[.\-]', '', customer_doc.nik)
			if not re.match(r'^\d{16}$', nik_clean):
				errors.append(_("NIK format is invalid. NIK must be 16 digits. Current value: {0}").format(customer_doc.nik))
		
		# Validate NITKU format (3 digits) if customer has NITKU
		if customer_doc.customers_nitku:
			nitku_clean = re.sub(r'[.\-]', '', str(customer_doc.customers_nitku))
			if not re.match(r'^\d{3}$', nitku_clean):
				errors.append(_("Customer NITKU format is invalid. NITKU must be 3 digits. Current value: {0}").format(customer_doc.customers_nitku))
	
	# Validate company NITKU if exists
	if doc.company:
		company_doc = frappe.get_doc("Company", doc.company)
		if company_doc.companys_nitku:
			nitku_clean = re.sub(r'[.\-]', '', str(company_doc.companys_nitku))
			if not re.match(r'^\d{3}$', nitku_clean):
				errors.append(_("Company NITKU format is invalid. NITKU must be 3 digits. Current value: {0}").format(company_doc.companys_nitku))
	
	# Validate branch NITKU if branch exists
	if doc.branch:
		branch_doc = frappe.get_doc("Branch", doc.branch)
		if branch_doc.branchs_nitku:
			nitku_clean = re.sub(r'[.\-]', '', str(branch_doc.branchs_nitku))
			if not re.match(r'^\d{3}$', nitku_clean):
				errors.append(_("Branch NITKU format is invalid. NITKU must be 3 digits. Current value: {0}").format(branch_doc.branchs_nitku))
	
	# Validate date consistency: tanggal faktur should not be before posting date
	if doc.tanggal_faktur_pajak and doc.posting_date:
		if doc.tanggal_faktur_pajak < doc.posting_date:
			errors.append(_("Tanggal Faktur Pajak ({0}) cannot be before Posting Date ({1})").format(
				doc.tanggal_faktur_pajak, doc.posting_date
			))
	
	# Raise errors if any
	if errors:
		frappe.throw("<br>".join(errors), title=_("Data Validation Error"))


def auto_create_vom_on_submit(doc, method):
	"""
	Auto-create VAT Output Metadata when Sales Invoice is submitted.
	This function checks the auto_create_vat_output_metadata setting and
	creates VAT Output Metadata if enabled.
	For return invoices, it creates VAT Output Return instead.
	"""
	try:
		# Handle return invoices separately
		if hasattr(doc, 'is_return') and doc.is_return:
			auto_create_vat_output_return_on_return(doc, method)
			return
		
		indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
		
		# Check if auto-create is enabled
		if not indonesia_localization_settings.auto_create_vat_output_metadata:
			return
		
		# Only create for submitted invoices with taxes
		if doc.docstatus != 1:
			return
		
		if not doc.taxes_and_charges:
			return
		
		# Check if VAT Output Metadata already exists for this invoice
		existing_vom = frappe.db.exists("VAT Output Metadata", {"noinvoice": doc.name})
		if existing_vom:
			return
		
		# Create VAT Output Metadata
		success_status, message = create_vat_output_metadata(doc, indonesia_localization_settings)
		
		if not success_status:
			frappe.log_error(
				f"Failed to auto-create VAT Output Metadata for Sales Invoice {doc.name}: {message}",
				"Auto Create VOM Error"
			)
		else:
			frappe.logger().info(f"Auto-created VAT Output Metadata for Sales Invoice {doc.name}")
			
	except Exception as e:
		frappe.log_error(
			f"Error in auto_create_vom_on_submit for Sales Invoice {doc.name}: {str(e)}",
			"Auto Create VOM Error"
		)


@frappe.whitelist()
def auto_create_vat_output_return_on_return(doc, method):
	"""
	Auto-create VAT Output Return when Sales Invoice Return is submitted.
	This function checks if the original Sales Invoice has VAT Output Metadata
	and creates VAT Output Return if enabled.
	"""
	try:
		indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
		
		# Check if auto-create is enabled (can add setting later)
		# For now, always try to create if original invoice has VOM
		
		# Only create for submitted return invoices
		if doc.docstatus != 1:
			return
		
		# Check if this is a return invoice
		if not doc.is_return:
			return
		
		# Get original Sales Invoice
		original_invoice_name = doc.return_against if hasattr(doc, 'return_against') and doc.return_against else None
		if not original_invoice_name:
			# Try alternative field name
			original_invoice_name = getattr(doc, 'against_sales_invoice', None)
			if not original_invoice_name:
				return
		
		# Check if original invoice has VAT Output Metadata
		original_vom = frappe.get_all(
			"VAT Output Metadata",
			filters={"noinvoice": original_invoice_name},
			fields=["name", "transactionid", "nofa"],
			limit=1
		)
		
		if not original_vom:
			# No VAT Output Metadata found, skip
			return
		
		original_vom_doc = original_vom[0]
		
		# Check if VAT Output Return already exists for this return invoice
		existing_return = frappe.get_all(
			"VAT Output Return",
			filters={"noinvoice": doc.name},
			limit=1
		)
		
		if existing_return:
			# Already exists, skip
			return
		
		# Create VAT Output Return
		from erpnext_indonesia_localization.doc_events import create_vat_output_return_metadata
		
		success, message = create_vat_output_return_metadata(doc, original_vom_doc['name'], indonesia_localization_settings)
		
		if success:
			frappe.log_simple(f"VAT Output Return created for Sales Invoice Return {doc.name}", "VAT Output Return Created")
		else:
			frappe.log_error(f"Failed to create VAT Output Return for {doc.name}: {message}", "VAT Output Return Error")
		
	except Exception as e:
		frappe.log_error(
			f"Error in auto_create_vat_output_return_on_return for Sales Invoice Return {doc.name}: {str(e)}",
			"Auto Create VAT Output Return Error"
		)


@frappe.whitelist()
def create_vat_output_return_metadata(return_invoice_doc, original_vom_name, indonesia_localization_settings=None):
	"""
	Create VAT Output Return Metadata from Sales Invoice Return.
	Similar to create_vat_output_metadata but for returns.
	Includes proper validation and negative amount handling.
	"""
	if not indonesia_localization_settings:
		indonesia_localization_settings = frappe.get_single('Indonesia Localization Settings')
	
	# Validate return invoice
	if not return_invoice_doc.is_return:
		frappe.throw(_("This function can only be used for return invoices"))
	
	if not return_invoice_doc.docstatus == 1:
		frappe.throw(_("Return invoice must be submitted before creating VAT Output Return"))
	
	# Get original VAT Output Metadata
	try:
		original_vom = frappe.get_doc("VAT Output Metadata", original_vom_name)
		if not original_vom.transactionid:
			frappe.throw(_("Original VAT Output Metadata must have a Transaction ID"))
	except frappe.DoesNotExistError:
		frappe.throw(_("Original VAT Output Metadata not found: {0}").format(original_vom_name))
	
	# Create VAT Output Return
	return_metadata_doc = frappe.new_doc('VAT Output Return')
	return_metadata_doc.original_vat_output = original_vom_name
	return_metadata_doc.sales_invoice_return = return_invoice_doc.name
	return_metadata_doc.noinvoice = return_invoice_doc.name
	return_metadata_doc.parent_doctype = return_invoice_doc.doctype
	
	# Copy data from original VOM
	return_metadata_doc.npwp = original_vom.npwp
	return_metadata_doc.nama = original_vom.nama
	return_metadata_doc.alamatjalan = original_vom.alamatjalan
	return_metadata_doc.kota = original_vom.kota
	return_metadata_doc.telp = original_vom.telp
	return_metadata_doc.kdjenistransaksi = original_vom.kdjenistransaksi or "04"  # Default for return
	return_metadata_doc.idketerangantambahan = original_vom.idketerangantambahan
	
	# Set dates from return invoice - use posting date for consistency
	from frappe.utils import getdate, formatdate
	posting_date = getdate(return_invoice_doc.posting_date or frappe.utils.today())
	return_metadata_doc.tanggalfaktur = formatdate(posting_date, "YYYY-mm-dd")
	return_metadata_doc.masapajak = str(posting_date.month).zfill(2)
	return_metadata_doc.tahunpajak = str(posting_date.year)
	
	# Calculate tax rate more accurately from return invoice taxes
	# Find VAT tax rate from taxes and charges
	tariff = 0
	if return_invoice_doc.taxes:
		for tax in return_invoice_doc.taxes:
			# Look for VAT/Pajak Pertambahan Nilai tax
			if tax.charge_type == "On Net Total" and tax.account_head:
				# Check if this is a VAT tax account
				account_head_lower = tax.account_head.lower()
				if "ppn" in account_head_lower or "pajak pertambahan nilai" in account_head_lower or "vat" in account_head_lower:
					if tax.rate:
						tariff = float(tax.rate)
						break
	
	# If no VAT tax found, try to get from original VOM
	if tariff == 0 and original_vom.tarifppn:
		tariff = float(original_vom.tarifppn)
	
	# Default to 11% if still no rate found (standard Indonesian VAT rate)
	if tariff == 0:
		tariff = 11.0
	
	return_metadata_doc.tarifppn = tariff
	return_metadata_doc.autouploaddjp = indonesia_localization_settings.autouploaddjp
	
	# Add items from return invoice
	# For returns, amounts should be negative or handled as returns
	for item in return_invoice_doc.items:
		# Calculate DPP (net amount after discount)
		dpp = abs(item.net_amount)  # Use absolute value for DPP
		
		# Calculate PPN based on tariff
		ppn = (dpp * (tariff / 100)) if tariff > 0 else 0
		
		# For returns, we might need to use negative values depending on API requirements
		# But typically, DPP and PPN should be positive, and the return nature is indicated by kdjenistransaksi
		
		return_metadata_doc.append('barangjasa', {
			"nama": item.description or item.item_name or "",
			"jumlah": abs(item.qty) if item.qty else 0,  # Use absolute value
			"harga": abs(item.rate) if item.rate else 0,  # Use absolute value
			"dpp": dpp,
			"ppn": ppn,
			"tarifppnbm": 0,
			"diskon": abs(item.discount_amount) if item.discount_amount else 0,  # Use absolute value
			"kode": ""
		})
	
	# Validate that we have items
	if not return_metadata_doc.barangjasa or len(return_metadata_doc.barangjasa) == 0:
		frappe.throw(_("Return invoice must have at least one item"))
	
	return_metadata_doc.status = "To Be Reviewed"
	return_metadata_doc.save()
	
	# Auto-call Pajak.io API if enabled
	if hasattr(indonesia_localization_settings, 'auto_call_pajakios_api') and indonesia_localization_settings.auto_call_pajakios_api:
		try:
			from erpnext_indonesia_localization.api import create_vat_output_return
			create_vat_output_return(return_metadata_doc.name)
		except Exception as e:
			frappe.log_error(f"Error auto-calling Pajak.io API for VAT Output Return {return_metadata_doc.name}: {str(e)}", "VAT Output Return API Error")
	
	message = "Successfully Created VAT Output Return"
	return True, message