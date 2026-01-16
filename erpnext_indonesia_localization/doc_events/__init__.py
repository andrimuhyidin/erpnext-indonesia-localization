# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
Document Event Handlers

This module contains document event handlers for Sales Invoice, Purchase Invoice, etc.
"""

# Re-export main functions for easier imports
from erpnext_indonesia_localization.doc_events.sales_invoice import (
	create_vat_output_metadata,
	create_vat_output_return_metadata,
	auto_create_vom_on_submit,
	validate_tax_data_formats
)

from erpnext_indonesia_localization.doc_events.purchase_invoice import (
	auto_create_vim_on_submit,
	auto_create_ebupot_on_payment,
	validate_purchase_invoice_tax_data
)

__all__ = [
	"create_vat_output_metadata",
	"create_vat_output_return_metadata",
	"auto_create_vom_on_submit",
	"validate_tax_data_formats",
	"auto_create_vim_on_submit",
	"auto_create_ebupot_on_payment",
	"validate_purchase_invoice_tax_data"
]
