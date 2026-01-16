# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
API Integration Module

This module contains API integration functions, primarily for Pajak.io.
"""

# Re-export main API functions for easier imports
# Import all whitelisted functions from pajakio module
from erpnext_indonesia_localization.api.pajakio import (
	# VAT Output functions
	create_vat_output,
	get_vat_output_detail,
	get_pdf_vat_output,
	upload_vat_output,
	update_vat_output,
	cancel_vat_output,
	delete_vat_output,
	# VAT Input functions
	create_vat_input,
	get_detail_vat_input,
	upload_vat_input,
	cancel_vat_input,
	delete_vat_input,
	# Withholding Tax functions
	create_withholding_tax,
	update_withholding_tax,
	upload_withholding_tax,
	delete_withholding_tax,
	get_status_bupot,
	get_code_of_type,
	# VAT Output Return functions
	create_vat_output_return,
	get_detail_vat_output_return,
	update_vat_output_return,
	cancel_vat_output_return,
	delete_vat_output_return,
	upload_vat_output_return,
	# Verification functions
	verify_npwp,
	verify_nik,
	# Income Recipient functions
	create_income_recipient,
	update_income_recipient,
	delete_income_recipient,
	list_income_recipient,
	# Signer functions
	create_signer,
	list_signer,
	set_active_signer
)

__all__ = [
	# VAT Output
	"create_vat_output",
	"get_vat_output_detail",
	"get_pdf_vat_output",
	"upload_vat_output",
	"update_vat_output",
	"cancel_vat_output",
	"delete_vat_output",
	# VAT Input
	"create_vat_input",
	"get_detail_vat_input",
	"upload_vat_input",
	"cancel_vat_input",
	"delete_vat_input",
	# Withholding Tax
	"create_withholding_tax",
	"update_withholding_tax",
	"upload_withholding_tax",
	"delete_withholding_tax",
	"get_status_bupot",
	"get_code_of_type",
	# VAT Output Return
	"create_vat_output_return",
	"get_detail_vat_output_return",
	"update_vat_output_return",
	"cancel_vat_output_return",
	"delete_vat_output_return",
	"upload_vat_output_return",
	# Verification
	"verify_npwp",
	"verify_nik",
	# Income Recipient
	"create_income_recipient",
	"update_income_recipient",
	"delete_income_recipient",
	"list_income_recipient",
	# Signer
	"create_signer",
	"list_signer",
	"set_active_signer"
]
