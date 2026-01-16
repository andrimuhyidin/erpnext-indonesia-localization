# Project Structure Improvement Plan

## Status: ✅ COMPLETED

Semua improvement struktur project telah selesai dilakukan.

## Issues yang Sudah Diperbaiki

1. ✅ **Nested Directory Structure**: Nested `erpnext_indonesia_localization/erpnext_indonesia_localization/` telah dihapus
2. ✅ **Duplicate Utils Folders**: Utils folder telah dikonsolidasi ke root level
3. ✅ **Long Import Paths**: Semua import paths telah diupdate ke path yang lebih pendek
4. ✅ **Inconsistent Organization**: Semua modules telah dipindahkan ke root level dengan struktur yang konsisten
5. ⚠️ **Missing Type Hints**: Beberapa files belum menggunakan type hints (akan dilakukan di phase berikutnya)
6. ⚠️ **Documentation**: Dokumentasi perlu diupdate untuk refleksi struktur baru (akan dilakukan di phase berikutnya)

## Proposed Structure (Best Practices)

```
erpnext_indonesia_localization/
├── erpnext_indonesia_localization/
│   ├── __init__.py
│   ├── api/                          # API integrations
│   │   ├── __init__.py
│   │   └── pajakio.py
│   ├── doc_events/                   # Document event handlers
│   │   ├── __init__.py
│   │   ├── sales_invoice.py
│   │   └── purchase_invoice.py
│   ├── doctype/                      # Custom doctypes
│   │   ├── __init__.py
│   │   └── [doctype folders]/
│   ├── utils/                        # Utility functions (consolidated)
│   │   ├── __init__.py
│   │   ├── api/                      # API utilities
│   │   │   ├── __init__.py
│   │   │   └── pajakio_helper.py
│   │   ├── validation/               # Validation utilities
│   │   │   ├── __init__.py
│   │   │   └── coretax_validator.py
│   │   ├── export/                   # Export utilities
│   │   │   ├── __init__.py
│   │   │   └── ebupot_xml_exporter.py
│   │   ├── audit.py
│   │   ├── bulk_operations.py
│   │   ├── constants.py
│   │   ├── data.py
│   │   ├── install.py
│   │   └── template_tax.py
│   ├── tasks/                        # Scheduled tasks
│   │   ├── __init__.py
│   │   ├── daily.py
│   │   └── hourly.py
│   ├── notifications/                # Notification handlers
│   │   ├── __init__.py
│   │   └── vat_output_status.py
│   ├── report/                       # Custom reports
│   │   ├── __init__.py
│   │   └── [report folders]/
│   ├── number_card/                  # Number cards
│   │   └── [number card folders]/
│   ├── workspace/                    # Workspace configs
│   │   └── [workspace files]/
│   └── tests/                        # Test files
│       ├── __init__.py
│       ├── test_api/
│       │   ├── __init__.py
│       │   └── test_pajakio_api.py
│       ├── test_doctypes/
│       │   ├── __init__.py
│       │   └── test_sales_invoice.py
│       └── test_utils/
│           ├── __init__.py
│           └── test_utils.py
├── fixtures/                         # Fixtures
│   ├── custom_field.json
│   ├── indonesia_localization_settings.json
│   ├── property_setter.json
│   └── role.json
├── public/                           # Client-side assets
│   └── js/
│       ├── sales_invoice.js
│       ├── customer.js
│       └── ...
├── templates/                        # Jinja templates
│   ├── __init__.py
│   ├── pages/
│   │   └── __init__.py
│   └── tax_invoice_bulk.jinja
├── hooks.py                          # Frappe hooks
├── modules.txt                       # Module definitions
├── patches.txt                       # Migration patches
└── config/                           # Configuration
    └── __init__.py
```

## Implementation Steps

### Phase 1: Consolidate Utils ✅ COMPLETED
1. ✅ Move all utils from nested structure to root utils
2. ✅ Organize utils into subdirectories (api, validation, export)
3. ✅ Update all import paths

### Phase 2: Fix Import Paths ✅ COMPLETED
1. ✅ Update all imports to use shorter paths
2. ✅ Ensure all __init__.py files exist
3. ✅ Add proper exports in __init__.py files

### Phase 3: Organize Tests ✅ COMPLETED
1. ✅ Test subdirectories sudah ada dan terorganisir
2. ✅ Test files sudah berada di direktori yang tepat
3. ✅ Test imports telah diupdate

### Phase 4: Move Modules to Root Level ✅ COMPLETED
1. ✅ Memindahkan api, doc_events, doctype ke root level
2. ✅ Memindahkan number_card, report, workspace ke root level
3. ✅ Menghapus nested erpnext_indonesia_localization folder

### Phase 5: Documentation (TODO)
1. ⚠️ Update DEVELOPER_GUIDE.md dengan struktur baru
2. ⚠️ Update API.md dengan import paths baru
3. ⚠️ Add type hints where missing
4. ⚠️ Improve code documentation

## Benefits

1. **Shorter Import Paths**: `from erpnext_indonesia_localization.utils.api.pajakio_helper import ...` instead of nested paths
2. **Better Organization**: Related utilities grouped together
3. **Easier Maintenance**: Clear structure makes it easier to find files
4. **Best Practices**: Follows Frappe/ERPNext conventions
5. **Scalability**: Structure supports future growth
