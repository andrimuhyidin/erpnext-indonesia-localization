# ERPNext Indonesia Localization - API Documentation

## Overview

This document provides API documentation for the ERPNext Indonesia Localization module.

## VAT Output Metadata APIs

### create_vat_output_metadata

Creates VAT Output Metadata from Sales Invoice.

**Method**: `erpnext_indonesia_localization.doc_events.sales_invoice.create_vat_output_metadata`

**Parameters**:
- `doc`: Sales Invoice document
- `indonesia_localization_settings`: Indonesia Localization Settings document

**Returns**: Tuple (success_status, message)

### procedure_to_create_vom

Procedure to generate VOM doctype.

**Method**: `erpnext_indonesia_localization.doc_events.sales_invoice.procedure_to_create_vom`

**Parameters**:
- `name`: Document name
- `doctype`: Document type

**Returns**: Tuple (message, title)

## Pajak.io API Integration

### create_vat_output

Creates VAT output via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.create_vat_output`

**Parameters**:
- `doc`: VAT Output Metadata document

**Returns**: API response dictionary

### get_vat_output_detail

Gets VAT output details from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_vat_output_detail`

**Parameters**:
- `doc`: VAT Output Metadata document or document name

**Returns**: API response dictionary

## Verification API

### verify_npwp

Verify NPWP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.verify_npwp`

**Parameters**:
- `npwp`: NPWP number to verify (15 digits, can include dots/dashes)

**Returns**: Dictionary with verification result (valid, message, data)

### verify_nik

Verify NIK via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.verify_nik`

**Parameters**:
- `nik`: NIK number to verify (16 digits, can include dots/dashes)

**Returns**: Dictionary with verification result (valid, message, data)

## Enhanced VAT Output APIs

### update_vat_output

Update VAT Output via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.update_vat_output`

**Parameters**:
- `doc`: VAT Output Metadata document or document name
- `update_data`: Dictionary with fields to update

**Returns**: API response dictionary

### cancel_vat_output

Cancel VAT Output via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.cancel_vat_output`

**Parameters**:
- `doc`: VAT Output Metadata document or document name

**Returns**: API response dictionary

### delete_vat_output

Delete VAT Output via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.delete_vat_output`

**Parameters**:
- `doc`: VAT Output Metadata document or document name

**Returns**: API response dictionary

### get_list_vat_output

Get list of VAT Outputs from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_list_vat_output`

**Parameters**:
- `filters`: Dictionary with filter parameters (optional)
- `page`: Page number for pagination (default: 1)
- `per_page`: Number of items per page (default: 100)

**Returns**: API response dictionary with list of VAT Outputs

### delete_multiple_vat_output

Delete multiple VAT Outputs via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.delete_multiple_vat_output`

**Parameters**:
- `transaction_ids`: List of transaction IDs to delete

**Returns**: API response dictionary

## VAT Input API

### create_vat_input

Create VAT Input via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.create_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name

**Returns**: API response dictionary

### get_list_vat_input

Get list of VAT Inputs from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_list_vat_input`

**Parameters**:
- `filters`: Dictionary with filter parameters (optional)
- `page`: Page number for pagination (default: 1)
- `per_page`: Number of items per page (default: 100)

**Returns**: API response dictionary with list of VAT Inputs

### get_detail_vat_input

Get VAT Input detail from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_detail_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name

**Returns**: API response dictionary

### update_vat_input

Update VAT Input via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.update_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name
- `update_data`: Dictionary with fields to update

**Returns**: API response dictionary

### cancel_vat_input

Cancel VAT Input via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.cancel_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name

**Returns**: API response dictionary

### delete_vat_input

Delete VAT Input via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.delete_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name

**Returns**: API response dictionary

### upload_vat_input

Upload VAT Input to DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.upload_vat_input`

**Parameters**:
- `doc`: VAT Input Metadata document or document name

**Returns**: API response dictionary

### prepopulated_vat_input

Get prepopulated VAT Input data from DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.prepopulated_vat_input`

**Parameters**:
- `supplier_npwp`: Supplier NPWP to fetch faktur for
- `filters`: Additional filters (optional)

**Returns**: API response dictionary with list of available faktur

## Withholding Tax API

### create_withholding_tax

Create Withholding Tax (e-Bupot) via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.create_withholding_tax`

**Parameters**:
- `doc`: Withholding Tax Certificate document or document name

**Returns**: API response dictionary

### update_withholding_tax

Update Withholding Tax via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.update_withholding_tax`

**Parameters**:
- `doc`: Withholding Tax Certificate document or document name
- `update_data`: Dictionary with fields to update

**Returns**: API response dictionary

### upload_withholding_tax

Upload Withholding Tax to DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.upload_withholding_tax`

**Parameters**:
- `doc`: Withholding Tax Certificate document or document name

**Returns**: API response dictionary

### delete_withholding_tax

Delete Withholding Tax via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.delete_withholding_tax`

**Parameters**:
- `doc`: Withholding Tax Certificate document or document name

**Returns**: API response dictionary

### get_list_withholding_tax

Get list of Withholding Taxes from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_list_withholding_tax`

**Parameters**:
- `filters`: Dictionary with filter parameters (optional)
- `page`: Page number for pagination (default: 1)
- `per_page`: Number of items per page (default: 100)

**Returns**: API response dictionary with list of Withholding Taxes

### get_status_bupot

Get status of e-Bupot from DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_status_bupot`

**Parameters**:
- `transaction_id`: Transaction ID of the Withholding Tax

**Returns**: API response dictionary with status

### get_code_of_type

Get master data for kode objek pajak from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_code_of_type`

**Returns**: API response dictionary with list of tax codes

## VAT Output Return API

### create_vat_output_return

Create VAT Output Return via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.create_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name

**Returns**: API response dictionary

### get_list_vat_output_return

Get list of VAT Output Returns from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_list_vat_output_return`

**Parameters**:
- `filters`: Dictionary with filter parameters (optional)
- `page`: Page number for pagination (default: 1)
- `per_page`: Number of items per page (default: 100)

**Returns**: API response dictionary with list of VAT Output Returns

### get_detail_vat_output_return

Get VAT Output Return detail from Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.get_detail_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name

**Returns**: API response dictionary

### update_vat_output_return

Update VAT Output Return via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.update_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name
- `update_data`: Dictionary with fields to update

**Returns**: API response dictionary

### cancel_vat_output_return

Cancel VAT Output Return via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.cancel_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name

**Returns**: API response dictionary

### delete_vat_output_return

Delete VAT Output Return via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.delete_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name

**Returns**: API response dictionary

### upload_vat_output_return

Upload VAT Output Return to DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.upload_vat_output_return`

**Parameters**:
- `doc`: VAT Output Return document or document name

**Returns**: API response dictionary

## Bulk Operations API

### bulk_upload_vat_output

Bulk upload VAT Output to DJP via API.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_upload_vat_output`

**Parameters**:
- `metadata_names`: List of VAT Output Metadata names

**Returns**: Dictionary with upload status (success_count, failure_count, errors)

### bulk_upload_vat_input

Bulk upload VAT Input to DJP via API.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_upload_vat_input`

**Parameters**:
- `metadata_names`: List of VAT Input Metadata names

**Returns**: Dictionary with upload status (success_count, failure_count, errors)

### bulk_upload_withholding_tax

Bulk upload Withholding Tax to DJP via API.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_upload_withholding_tax`

**Parameters**:
- `certificate_names`: List of Withholding Tax Certificate names

**Returns**: Dictionary with upload status (success_count, failure_count, errors)

### bulk_sync_status

Bulk sync status from Pajak.io API.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_sync_status`

**Parameters**:
- `doctype`: Document type (VAT Output Metadata, VAT Input Metadata, or Withholding Tax Certificate)
- `names`: List of document names

**Returns**: Dictionary with sync status (success_count, failure_count, errors)

### bulk_delete_via_api

Bulk delete documents via Pajak.io API.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_delete_via_api`

**Parameters**:
- `doctype`: Document type (VAT Output Metadata, VAT Input Metadata, or Withholding Tax Certificate)
- `names`: List of document names

**Returns**: Dictionary with delete status (success_count, failure_count, errors)

## API Helper Utilities

### get_pajakio_headers

Get standardized API headers with authentication.

**Method**: `erpnext_indonesia_localization.utils.api.pajakio_helper.get_pajakio_headers`

**Returns**: Dictionary with API headers including Authorization

### make_pajakio_request

Generic request handler with retry logic for Pajak.io API.

**Method**: `erpnext_indonesia_localization.utils.api.pajakio_helper.make_pajakio_request`

**Parameters**:
- `method`: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
- `url`: API endpoint URL
- `headers`: Request headers (defaults to get_pajakio_headers())
- `json_data`: JSON payload for POST/PUT requests
- `params`: URL parameters for GET requests
- `max_retries`: Maximum number of retry attempts (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 2)
- `timeout_seconds`: Request timeout in seconds (default: 30)
- `context`: Additional context for error logging

**Returns**: Response data as dictionary

### validate_api_response

Validate API response structure.

**Method**: `erpnext_indonesia_localization.utils.pajakio_helper.validate_api_response`

**Parameters**:
- `response_data`: Response data from API
- `required_fields`: List of required field names (optional)

**Returns**: Tuple (is_valid, error_message)

### handle_pajakio_error

Centralized error handling for Pajak.io API errors.

**Method**: `erpnext_indonesia_localization.utils.pajakio_helper.handle_pajakio_error`

**Parameters**:
- `error`: Exception object
- `context`: Additional context string for logging

**Returns**: User-friendly error message

### get_pajakio_url

Get Pajak.io API URL from Indonesia Localization Settings.

**Method**: `erpnext_indonesia_localization.utils.pajakio_helper.get_pajakio_url`

**Parameters**:
- `setting_field`: Field name in Indonesia Localization Settings

**Returns**: API URL string

**Parameters**:
- `doc`: VAT Output Metadata document

**Returns**: API response dictionary

### upload_vat_output

Uploads VAT output to DJP via Pajak.io API.

**Method**: `erpnext_indonesia_localization.api.pajakio.upload_vat_output`

**Parameters**:
- `doc`: VAT Output Metadata document name

**Returns**: API response dictionary

## Bulk Operations APIs

### bulk_create_vat_output_metadata

Bulk create VAT Output Metadata for multiple Sales Invoices.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_create_vat_output_metadata`

**Parameters**:
- `invoice_names`: List of Sales Invoice names

**Returns**: Dictionary with success_count, failure_count, and errors

### bulk_approve_vat_output

Bulk approve VAT Output Metadata.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_approve_vat_output`

**Parameters**:
- `metadata_names`: List of VAT Output Metadata names

**Returns**: Dictionary with success_count, failure_count, and errors

### bulk_reject_vat_output

Bulk reject VAT Output Metadata.

**Method**: `erpnext_indonesia_localization.utils.bulk_operations.bulk_reject_vat_output`

**Parameters**:
- `metadata_names`: List of VAT Output Metadata names

**Returns**: Dictionary with success_count, failure_count, and errors

## Error Handling

All API calls include:
- Retry mechanism (3 attempts)
- Timeout handling (30 seconds)
- Response validation
- Proper error logging

## Authentication

Pajak.io API requires API key stored in Indonesia Localization Settings (password field).
