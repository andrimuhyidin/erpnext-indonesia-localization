# Project Structure Documentation

Dokumentasi ini menjelaskan struktur folder dan file dalam project ERPNext Indonesia Localization.

## Root Directory Structure

```
erpnext-indonesia-localization/
├── erpnext_indonesia_localization/    # Main application directory
├── docs/                               # Documentation
│   ├── API.md                          # API documentation
│   ├── DEVELOPER_GUIDE.md             # Developer guide
│   ├── TROUBLESHOOTING.md             # Troubleshooting guide
│   ├── PROJECT_STRUCTURE_IMPROVEMENT.md # Structure improvement notes
│   └── manuals/                        # User manuals and installation docs
│       ├── Installation Documentation - ENG.pdf
│       ├── Installation Documentation - ID.pdf
│       ├── User Manual Coretax EIL - ENG.pdf
│       ├── User Manual Coretax EIL - ID.pdf
│       ├── User Manual ENG.pdf
│       └── User Manual IDN.pdf
├── data/                               # Reference data and resources
│   └── coretax_reference_master_data/ # CoreTax master data files (Excel)
│       ├── CoreTax Additional Info Ref.xlsx
│       ├── CoreTax Barang Jasa Ref.xlsx
│       ├── CoreTax Facility Stamp Ref.xlsx
│       ├── CoreTax Transaction Code Ref.xlsx
│       └── CoreTax Unit Ref.xlsx
├── README.md                           # Main project README
├── LICENSE                             # License file
└── pyproject.toml                      # Python project configuration
```

## Main Application Directory

Struktur lengkap dari `erpnext_indonesia_localization/` dapat dilihat di [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

## Folder Descriptions

### `/docs/`
Berisi semua dokumentasi project:
- **API.md**: Dokumentasi API endpoints dan functions
- **DEVELOPER_GUIDE.md**: Panduan untuk developer
- **TROUBLESHOOTING.md**: Panduan troubleshooting
- **PROJECT_STRUCTURE_IMPROVEMENT.md**: Catatan improvement struktur project
- **manuals/**: Folder untuk user manuals dan installation documentation dalam format PDF

### `/data/`
Berisi data referensi dan resources:
- **coretax_reference_master_data/**: File Excel untuk master data CoreTax yang dapat diimport ke ERPNext

### `/erpnext_indonesia_localization/`
Main application directory yang berisi semua kode aplikasi, doctypes, reports, dan komponen lainnya.

## File Locations

### Installation Documentation
- English: `docs/manuals/Installation Documentation - ENG.pdf`
- Indonesian: `docs/manuals/Installation Documentation - ID.pdf`

### User Manuals
- Coretax EIL English: `docs/manuals/User Manual Coretax EIL - ENG.pdf`
- Coretax EIL Indonesian: `docs/manuals/User Manual Coretax EIL - ID.pdf`
- General English: `docs/manuals/User Manual ENG.pdf`
- General Indonesian: `docs/manuals/User Manual IDN.pdf`

### Master Data Files
Semua file master data CoreTax berada di: `data/coretax_reference_master_data/`

## Best Practices

1. **Dokumentasi**: Semua dokumentasi harus berada di folder `docs/`
2. **Data Referensi**: Semua data referensi dan resources harus berada di folder `data/`
3. **Code**: Semua kode aplikasi berada di `erpnext_indonesia_localization/`
4. **PDF Files**: Semua file PDF (manuals, documentation) harus berada di `docs/manuals/`

## Migration Notes

Jika Anda menggunakan versi lama dari project ini, perhatikan perubahan path berikut:

- **Installation Documentation**: Dari root → `docs/manuals/`
- **User Manuals**: Dari root → `docs/manuals/`
- **Master Data**: Dari `coretax_reference_master_data/` → `data/coretax_reference_master_data/`
- **Project Structure Docs**: Dari root → `docs/PROJECT_STRUCTURE_IMPROVEMENT.md`
