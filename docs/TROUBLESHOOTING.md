# ERPNext Indonesia Localization - Troubleshooting Guide

## Common Issues and Solutions

### 1. VAT Output Metadata Not Created Automatically

**Problem**: VAT Output Metadata is not created when Sales Invoice is submitted.

**Solutions**:
- Check if `auto_create_vat_output_metadata` is enabled in Indonesia Localization Settings
- Verify Sales Invoice has `taxes_and_charges` set
- Check error logs for any validation errors
- Ensure customer has complete address and contact information

### 2. Pajak.io API Errors

**Problem**: API calls to Pajak.io are failing.

**Solutions**:
- Verify API key is correctly set in Indonesia Localization Settings
- Check network connectivity
- Verify API URLs are correct
- Check API response in error logs
- Ensure API key has proper permissions

### 3. Tax Invoice Number Not Linked

**Problem**: Tax Invoice Number is not automatically linked to Sales Invoice.

**Solutions**:
- Check if Tax Invoice Number source is set correctly (PAJAK.IO or TAX INVOICE NUMBER DOCTYPE)
- Verify Tax Invoice Numbers are available in the system
- Check if customer is PKP (Pengusaha Kena Pajak)
- Review error logs for specific issues

### 4. XML Export Fails

**Problem**: Coretax XML Exporter fails to generate XML file.

**Solutions**:
- Verify Sales Invoices are in submitted state
- Check if invoices have required tax information
- Ensure company tax information is complete
- Check file permissions for XML generation
- Review error logs for specific errors

### 5. Data Validation Errors

**Problem**: NPWP, NIK, or NITKU format validation fails.

**Solutions**:
- NPWP must be 15 digits (can include dots/dashes)
- NIK must be 16 digits
- NITKU must be 3 digits
- Remove any special characters before validation
- Check customer/supplier master data

### 6. Scheduled Tasks Not Running

**Problem**: Scheduled tasks (sync, auto-upload) are not executing.

**Solutions**:
- Verify scheduler is enabled: `bench --site [site] scheduler status`
- Check if tasks are defined in `hooks.py`
- Review scheduler logs
- Ensure tasks are not failing silently
- Check task execution permissions

### 7. Import Errors from Excel

**Problem**: Coretax Importer fails to import Excel file.

**Solutions**:
- Verify Excel file format matches expected structure
- Check column names match exactly
- Ensure data types are correct
- Review import error log in the document
- Verify file is not corrupted

### 8. Background Jobs Not Executing

**Problem**: Background jobs (enqueue) are not running.

**Solutions**:
- Check if background job workers are running
- Verify queue configuration
- Check job status in Frappe
- Review job logs
- Ensure sufficient system resources

## Error Log Locations

- Frappe Error Log: `/app/error-log`
- Application Logs: Check `frappe.log_error()` entries
- Scheduler Logs: `bench --site [site] scheduler logs`
- Background Job Logs: Check job queue status

## Getting Help

1. Check error logs for detailed error messages
2. Review this troubleshooting guide
3. Check API documentation
4. Contact support with error logs and context

## Diagnostic Commands

```bash
# Check scheduler status
bench --site [site] scheduler status

# Check background jobs
bench --site [site] enqueue list

# Clear cache
bench --site [site] clear-cache

# Check Frappe version
bench --site [site] console
>>> frappe.__version__
```
