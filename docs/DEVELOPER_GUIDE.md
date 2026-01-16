# ERPNext Indonesia Localization - Developer Guide

## Overview

This guide provides information for developers working on the ERPNext Indonesia Localization module.

## Project Structure

```
erpnext-indonesia-localization/          # Root project directory
├── erpnext_indonesia_localization/      # Main app directory
│   ├── __init__.py
│   ├── api/                            # API integrations (Pajak.io)
│   │   ├── __init__.py                 # Re-exports for easier imports
│   │   └── pajakio.py                  # Pajak.io API functions
│   ├── doc_events/                     # Document event handlers
│   │   ├── __init__.py                 # Re-exports for easier imports
│   │   ├── sales_invoice.py
│   │   └── purchase_invoice.py
│   ├── doctype/                        # Custom doctypes
│   │   ├── __init__.py
│   │   └── [doctype_name]/             # Each doctype in its own folder
│   ├── utils/                          # Utility functions (consolidated)
│   │   ├── __init__.py
│   │   ├── api/                        # API utilities
│   │   │   └── pajakio_helper.py
│   │   ├── validation/                 # Validation utilities
│   │   │   └── coretax_validator.py
│   │   ├── export/                     # Export utilities
│   │   │   └── ebupot_xml_exporter.py
│   │   ├── audit.py
│   │   ├── bulk_operations.py
│   │   ├── constants.py
│   │   ├── data.py
│   │   ├── install.py
│   │   └── template_tax.py
│   ├── report/                         # Custom reports
│   ├── number_card/                    # Number cards for dashboard
│   ├── workspace/                     # Workspace configurations
│   ├── tasks/                          # Scheduled tasks
│   ├── notifications/                  # Notification handlers
│   ├── tests/                          # Test files
│   ├── fixtures/                       # Fixtures
│   ├── public/                         # Client-side assets
│   └── templates/                      # Jinja templates
├── docs/                               # Documentation
│   ├── API.md
│   ├── DEVELOPER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   ├── PROJECT_STRUCTURE_IMPROVEMENT.md
│   └── manuals/                        # User manuals and installation docs
│       ├── Installation Documentation - ENG.pdf
│       ├── Installation Documentation - ID.pdf
│       └── [other PDF files]
├── data/                               # Reference data and resources
│   └── coretax_reference_master_data/  # CoreTax master data files
├── README.md
├── LICENSE
└── pyproject.toml
│   ├── utils/                     # Utility functions (consolidated)
│   │   ├── __init__.py
│   │   ├── api/                   # API utilities
│   │   │   ├── __init__.py
│   │   │   └── pajakio_helper.py  # Pajak.io API helper functions
│   │   ├── validation/            # Validation utilities
│   │   │   ├── __init__.py
│   │   │   └── coretax_validator.py
│   │   ├── export/                # Export utilities
│   │   │   ├── __init__.py
│   │   │   └── ebupot_xml_exporter.py
│   │   ├── audit.py               # Audit logging
│   │   ├── bulk_operations.py    # Bulk operation functions
│   │   ├── constants.py           # Constants and enums
│   │   ├── data.py               # Data helper functions
│   │   ├── install.py            # Installation utilities
│   │   └── template_tax.py       # Tax template utilities
│   ├── tasks/                     # Scheduled tasks
│   │   ├── __init__.py
│   │   ├── daily.py              # Daily scheduled tasks
│   │   └── hourly.py             # Hourly scheduled tasks
│   ├── notifications/            # Notification handlers
│   │   ├── __init__.py
│   │   └── vat_output_status.py
│   ├── tests/                     # Test files (organized)
│   │   ├── __init__.py
│   │   ├── test_api/             # API integration tests
│   │   │   ├── __init__.py
│   │   │   └── test_pajakio_api.py
│   │   ├── test_doctypes/        # DocType functionality tests
│   │   │   ├── __init__.py
│   │   │   ├── test_sales_invoice.py
│   │   │   └── test_vat_input.py
│   │   └── test_utils/           # Utility function tests
│   │       ├── __init__.py
│   │       ├── test_utils.py
│   │       └── test_error_scenarios.py
│   ├── fixtures/                  # Fixtures (custom fields, roles)
│   │   ├── custom_field.json
│   │   ├── indonesia_localization_settings.json
│   │   ├── property_setter.json
│   │   └── role.json
│   ├── public/                    # Client-side JavaScript
│   │   └── js/
│   │       ├── sales_invoice.js
│   │       ├── customer.js
│   │       ├── supplier.js
│   │       └── ...
│   ├── templates/                 # Jinja templates
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   └── __init__.py
│   │   └── tax_invoice_bulk.jinja
│   ├── hooks.py                   # Frappe hooks configuration
│   ├── modules.txt               # Module definitions
│   └── patches.txt               # Migration patches
└── docs/                          # Documentation
    ├── API.md
    ├── DEVELOPER_GUIDE.md
    └── TROUBLESHOOTING.md
```

### Import Paths

With the improved structure, imports are now more organized:

**Before (nested):**
```python
from erpnext_indonesia_localization.utils.pajakio_helper import get_pajakio_headers
```

**After (organized):**
```python
from erpnext_indonesia_localization.utils.api.pajakio_helper import get_pajakio_headers
# Or use the module import:
from erpnext_indonesia_localization.api import create_vat_output
```

**Utils Organization:**
- `utils/api/` - API-related utilities (pajakio_helper)
- `utils/validation/` - Validation utilities (coretax_validator)
- `utils/export/` - Export utilities (ebupot_xml_exporter)
- Root utils - General utilities (audit, bulk_operations, constants, data, install, template_tax)

## Key Components

### Document Events

Document events are defined in `hooks.py` and implemented in `doc_events/`:

- **Sales Invoice**: 
  - Auto-create VOM on submit
  - Auto-create VAT Output Return for return invoices
  - Validation (NPWP, NIK, NITKU formats)
  - Tax calculations
  - Tax ID verification (if enabled)
- **Purchase Invoice**: 
  - Auto-create VIM on submit
  - Auto-create e-Bupot on payment
  - Validation
- **Payment Entry**: 
  - Auto-create e-Bupot on payment submission

### Scheduled Tasks

Scheduled tasks are defined in `hooks.py` and implemented in `tasks/`:

- **Daily**: 
  - Sync VAT Output status from Pajak.io
  - Sync VAT Input status from Pajak.io
  - Sync Withholding Tax status from Pajak.io
  - Check pending approvals
- **Hourly**: 
  - Auto-upload VAT Output to DJP
  - Auto-upload VAT Input to DJP
  - Auto-upload Withholding Tax to DJP

### Custom Doctypes

- **VAT Output Metadata**: Stores VAT output information for Sales Invoice
- **VAT Input Metadata**: Stores VAT input information for Purchase Invoice
- **VAT Output Return**: Handles VAT output returns for Sales Invoice Returns
- **Withholding Tax Certificate**: Manages e-Bupot certificates for withholding tax
- **Coretax XML Exporter**: Exports Sales Invoices to XML format
- **Coretax XML Importer**: Exports Purchase Invoices to XML format

### API Integration

The module integrates with Pajak.io OpenAPI for comprehensive tax compliance:

- **Verification API**: Verify NPWP and NIK in real-time
- **VAT Output API**: Full CRUD operations for VAT Output
- **VAT Input API**: Full CRUD operations for VAT Input
- **Withholding Tax API**: Full CRUD operations for e-Bupot
- **VAT Output Return API**: Handle return faktur
- **Bulk Operations**: Bulk upload, sync, and delete via API

### API Helper Utilities

All API calls use centralized helper functions in `utils/api/pajakio_helper.py`:

- `get_pajakio_headers()`: Standardized authentication headers with validation
- `get_pajakio_url()`: Get API URL from settings with validation
- `make_pajakio_request()`: Generic request handler with retry logic, rate limiting, and error handling
- `validate_api_response()`: Response validation
- `handle_pajakio_error()`: Centralized error handling

**Import Example:**
```python
from erpnext_indonesia_localization.utils.api.pajakio_helper import (
    get_pajakio_headers,
    make_pajakio_request,
    get_pajakio_url
)
```

### Validation Utilities

Validation functions are organized in `utils/validation/`:

- `coretax_validator.py`: CoreTax data validation functions
  - `validate_coretax_data()`: Validate CoreTax data structure
  - `validate_before_export()`: Pre-export validation
  - `validate_single_invoice()`: Single invoice validation

**Import Example:**
```python
from erpnext_indonesia_localization.utils.validation.coretax_validator import validate_before_export
```

### Export Utilities

Export functions are organized in `utils/export/`:

- `ebupot_xml_exporter.py`: e-Bupot XML export functions
  - `generate_ebupot_xml()`: Generate XML for withholding tax certificates

**Import Example:**
```python
from erpnext_indonesia_localization.utils.export.ebupot_xml_exporter import generate_ebupot_xml
```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to functions
- Handle errors gracefully with proper logging

### Testing

Tests are organized into subdirectories:

- `tests/test_api/`: API integration tests
- `tests/test_doctypes/`: DocType functionality tests
- `tests/test_utils/`: Utility function tests

**Best Practices:**
- Write unit tests for new functions
- Test error scenarios
- Test edge cases
- Use mock objects for API calls
- Test both success and failure paths

**Running Tests:**
```bash
bench --site [site_name] run-tests --app erpnext_indonesia_localization
```

### Code Organization Best Practices

1. **Use Module Imports**: Import from `__init__.py` when possible for cleaner imports
   ```python
   # Good
   from erpnext_indonesia_localization.api import create_vat_output
   
   # Also acceptable (direct import)
   from erpnext_indonesia_localization.api.pajakio import create_vat_output
   ```

2. **Organize Utils by Category**: Group related utilities in subdirectories
   - API utilities → `utils/api/`
   - Validation utilities → `utils/validation/`
   - Export utilities → `utils/export/`

3. **Add __init__.py Files**: All packages should have `__init__.py` with proper exports

4. **Documentation**: Add docstrings to all public functions and classes

5. **Type Hints**: Use type hints where appropriate (Python 3.6+)
- Run tests before committing

### Error Handling

- Use specific exception types
- Log errors with context
- Provide user-friendly error messages
- Implement retry mechanisms for API calls

## Frappe v16 Compatibility

### Database API

Use `frappe.get_all()` instead of `frappe.get_value()` with dict filters:

```python
# ❌ Old (v15)
frappe.get_value("Doctype", {"field": "value"}, "name")

# ✅ New (v16)
result = frappe.get_all("Doctype", filters={"field": "value"}, fields=["name"], limit=1)
name = result[0].name if result else None
```

### Background Jobs

Use `frappe.enqueue()` directly instead of importing:

```python
# ✅ Correct
frappe.enqueue(
    method=my_function,
    queue="long",
    arg1=value1
)
```

### File Handling

Handle import errors gracefully:

```python
try:
    from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file
except ImportError:
    # Fallback implementation
    pass
```

## Adding New Features

1. Create doctype if needed
2. Add document events in `hooks.py`
3. Implement business logic
4. Add client-side JavaScript if needed
5. Write tests
6. Update documentation

## Common Patterns

### Creating VAT Output Metadata

```python
from erpnext_indonesia_localization.doc_events import create_vat_output_metadata

success, message = create_vat_output_metadata(si_doc, settings)
```

### Logging Tax Data Changes

```python
from erpnext_indonesia_localization.utils.audit import log_tax_data_change

log_tax_data_change("VAT Output Metadata", doc.name, "status", old_value, new_value)
```

## Troubleshooting

### Common Issues

1. **Import errors**: Check if all dependencies are installed
2. **API errors**: Verify API key and network connectivity
3. **Database errors**: Check Frappe version compatibility

### Debugging

- Enable debug logging: `frappe.utils.logger.set_log_level("DEBUG")`
- Check error logs: `frappe.log_error()`
- Use Frappe console for testing
