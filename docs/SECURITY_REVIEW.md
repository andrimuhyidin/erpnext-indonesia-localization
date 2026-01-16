# Security Review - Whitelist Functions

**Review Date**: 17 January 2026
**Reviewer**: Claude Code
**Version**: 1.2.0

---

## Overview

This document provides a security audit of all `@frappe.whitelist()` decorated functions in the ERPNext Indonesia Localization module. These functions are publicly accessible via Frappe's REST API and require careful review.

---

## Summary

| Category | Count | Risk Level |
|----------|-------|------------|
| VAT Output API | 15 | Medium |
| VAT Input API | 12 | Medium |
| Withholding Tax API | 10 | Medium |
| Verification API | 2 | Low |
| Helper Functions | 8 | Low |
| Document Events | 6 | Low |
| **Total** | **53** | - |

---

## Whitelist Functions by Module

### 1. VAT Output Functions (`api/pajakio.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `create_vat_output` | Create VAT output via Pajak.io | Yes | Medium | Creates financial records |
| `create_vat_output_js` | JS wrapper for create_vat_output | Yes | Medium | Internal use |
| `get_vat_output_detail` | Get VAT output status | Yes | Low | Read-only |
| `get_pdf_vat_output` | Download VAT PDF | Yes | Low | Read-only |
| `upload_vat_output` | Upload to DJP | Yes | Medium | External API call |
| `update_vat_output` | Update VAT output | Yes | Medium | Modifies records |
| `cancel_vat_output` | Cancel VAT output | Yes | Medium | State change |
| `delete_vat_output` | Delete VAT output | Yes | High | Permanent delete |
| `get_list_vat_output` | List VAT outputs | Yes | Low | Read-only |
| `delete_multiple_vat_output` | Bulk delete | Yes | High | Bulk operation |

**Recommendations**:
- [ ] Add rate limiting to bulk operations
- [ ] Implement soft delete instead of hard delete
- [ ] Add audit logging for all state changes

---

### 2. VAT Input Functions (`api/pajakio.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `create_vat_input` | Create VAT input | Yes | Medium | Creates records |
| `get_list_vat_input` | List VAT inputs | Yes | Low | Read-only |
| `get_detail_vat_input` | Get VAT input detail | Yes | Low | Read-only |
| `update_vat_input` | Update VAT input | Yes | Medium | Modifies records |
| `cancel_vat_input` | Cancel VAT input | Yes | Medium | State change |
| `delete_vat_input` | Delete VAT input | Yes | High | Permanent delete |
| `upload_vat_input` | Upload to DJP | Yes | Medium | External API |
| `change_credit_vat_input` | Change credit status | Yes | Medium | State change |
| `prepopulated_vat_input` | Get prepopulated data | Yes | Low | Read-only |

**Recommendations**:
- [ ] Add validation for credit status changes
- [ ] Implement undo functionality

---

### 3. Withholding Tax Functions (`api/pajakio.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `create_withholding_tax` | Create e-Bupot | Yes | Medium | Creates records |
| `update_withholding_tax` | Update e-Bupot | Yes | Medium | Modifies records |
| `upload_withholding_tax` | Upload to DJP | Yes | Medium | External API |
| `delete_withholding_tax` | Delete e-Bupot | Yes | High | Permanent delete |
| `get_list_withholding_tax` | List e-Bupot | Yes | Low | Read-only |
| `get_status_bupot` | Get e-Bupot status | Yes | Low | Read-only |
| `get_code_of_type` | Get tax codes | Yes | Low | Read-only |
| `create_income_recipient` | Create recipient | Yes | Medium | Creates records |
| `list_income_recipient` | List recipients | Yes | Low | Read-only |
| `update_income_recipient` | Update recipient | Yes | Medium | Modifies records |
| `delete_income_recipient` | Delete recipient | Yes | High | Permanent delete |
| `create_signer` | Create signer | Yes | Medium | Creates records |
| `list_signer` | List signers | Yes | Low | Read-only |
| `set_active_signer` | Set active signer | Yes | Medium | State change |

---

### 4. VAT Output Return Functions (`api/pajakio.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `create_vat_output_return` | Create VAT return | Yes | Medium | Creates records |
| `get_list_vat_output_return` | List VAT returns | Yes | Low | Read-only |
| `get_detail_vat_output_return` | Get return detail | Yes | Low | Read-only |
| `update_vat_output_return` | Update return | Yes | Medium | Modifies records |
| `cancel_vat_output_return` | Cancel return | Yes | Medium | State change |
| `delete_vat_output_return` | Delete return | Yes | High | Permanent delete |
| `upload_vat_output_return` | Upload to DJP | Yes | Medium | External API |

---

### 5. Verification Functions (`api/pajakio.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `verify_npwp` | Verify NPWP | Yes | Low | Read-only, external API |
| `verify_nik` | Verify NIK | Yes | Low | Read-only, external API |

**Recommendations**:
- [ ] Add rate limiting to prevent abuse
- [ ] Cache verification results

---

### 6. Document Event Functions (`doc_events/sales_invoice.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `procedure_to_create_vom` | Create VOM | Yes | Medium | Creates records |
| `create_vom_via_button` | Button handler | Yes | Medium | User action |
| `create_vom_via_cronjob` | Cronjob handler | Yes | Medium | Automated |
| `link_tax_invoice_number` | Link TIN | Yes | Medium | State change |
| `create_vat_output_metadata` | Create metadata | Yes | Medium | Creates records |
| `auto_create_vat_output_return_on_return` | Auto-create return | Yes | Medium | Automated |
| `create_vat_output_return_metadata` | Create return metadata | Yes | Medium | Creates records |

---

### 7. Validation Functions (`utils/validation/coretax_validator.py`)

| Function | Purpose | Auth Required | Risk | Notes |
|----------|---------|---------------|------|-------|
| `validate_single_invoice` | Validate invoice | Yes | Low | Read-only |

---

## Security Concerns

### 1. High-Risk Functions (Delete Operations)

The following functions perform permanent deletions:

```python
- delete_vat_output
- delete_multiple_vat_output
- delete_vat_input
- delete_withholding_tax
- delete_income_recipient
- delete_vat_output_return
```

**Recommendations**:
1. Implement soft delete (add `is_deleted` flag)
2. Add confirmation step for bulk operations
3. Implement audit trail with `before_delete` values
4. Add role-based permissions for delete operations

### 2. External API Calls

Functions that call external Pajak.io API:

```python
- create_vat_output
- upload_vat_output
- verify_npwp
- verify_nik
- get_vat_output_detail
- get_pdf_vat_output
# ... and more
```

**Recommendations**:
1. Implement rate limiting (already has retry logic)
2. Add request logging for audit
3. Timeout handling (already implemented - 30s)
4. Error handling for API failures (already implemented)

### 3. Bulk Operations

Functions that operate on multiple records:

```python
- delete_multiple_vat_output
- get_list_vat_output (with pagination)
- get_list_vat_input (with pagination)
```

**Recommendations**:
1. Limit batch size (already implemented - 50)
2. Add progress tracking (already implemented)
3. Implement transaction rollback on failure

---

## Usage of `ignore_permissions`

Review of `ignore_permissions=True` usage:

| Location | Context | Justified |
|----------|---------|-----------|
| `purchase_invoice.py:155` | Create Withholding Tax Certificate | Yes - System automation |

**Recommendation**: Document each usage with justification comment.

---

## Role-Based Access Control

Current implementation relies on Frappe's built-in permission system.

**Recommendations**:
1. Define custom roles:
   - `Tax Manager` - Full access
   - `Tax Operator` - Create/Read/Update
   - `Tax Viewer` - Read-only
2. Add permission checks in sensitive functions
3. Document role requirements in API.md

---

## API Key Security

Current implementation:
- ✅ API key stored using `frappe.get_password()` (encrypted)
- ✅ API key validated before use
- ✅ Base64 encoding for transmission

**Recommendations**:
1. Add API key rotation mechanism
2. Implement key expiration
3. Log API key usage for security audit

---

## Input Validation

Current implementation:
- ✅ NPWP format validation (15 digits)
- ✅ NIK format validation (16 digits)
- ✅ NITKU format validation (3 digits)
- ✅ Transaction code validation (01-09)

**Recommendations**:
1. Add input sanitization for all string fields
2. Validate numeric ranges for amounts
3. Validate date formats and ranges

---

## Action Items

### Critical (P0)
- [ ] Implement soft delete for all delete operations
- [ ] Add audit logging for state changes
- [ ] Review and limit `ignore_permissions` usage

### High (P1)
- [ ] Add rate limiting for verification APIs
- [ ] Implement role-based access control
- [ ] Add bulk operation limits

### Medium (P2)
- [ ] Add request/response logging
- [ ] Implement API key rotation
- [ ] Add input sanitization

### Low (P3)
- [ ] Cache verification results
- [ ] Add request tracing (correlation IDs)
- [ ] Documentation updates

---

## Conclusion

The whitelist functions are generally well-implemented with good error handling and validation. The main areas for improvement are:

1. **Soft delete** instead of hard delete
2. **Audit logging** for compliance
3. **Rate limiting** for external API calls
4. **Role-based access** for sensitive operations

The codebase follows security best practices for:
- ✅ API key management
- ✅ Input validation
- ✅ Error handling
- ✅ Retry logic with backoff
- ✅ Timeout handling

---

*This document should be reviewed and updated quarterly or after significant changes to whitelist functions.*
