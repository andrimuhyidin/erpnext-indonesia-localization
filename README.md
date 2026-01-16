<div align="center">

<h1>ERPNext Indonesia Localization</h1>

![logopng](.github/logo.png)

[Website](https://www.agiletechnica.com)
  &nbsp;|&nbsp;
[Demo](https://erpnextindonesia-stg.frappe.cloud/app)
  &nbsp;|&nbsp;
[Documentation](docs/)

</div>

## Introduction

ERPNext Indonesia Localization is a comprehensive custom application that helps businesses comply with Indonesian tax regulations through ERPNext. This app provides seamless integration with Indonesian tax systems including CoreTax, Pajak.io API, and e-Faktur compliance.

It's built on [ERPNext](https://github.com/frappe/erpnext) and the [Frappe Framework](https://github.com/frappe/frappe). Check them out!

**Current Version:** 1.2.0

<br />

## Key Features

### 🚀 Core Features

- **Coretax XML Exporter**: Generate tax-compliant XML files from Sales Invoices following DJP standards for e-Faktur approval
- **Coretax Importer**: Import VAT Output data from DJP (Excel format) back into ERPNext with automatic validation
- **Pajak.io API Integration**: Seamless integration with Pajak.io for VAT Output, VAT Input, and Withholding Tax management
- **Tax Invoice Number Management**: Automated tax invoice number generation and tracking
- **VAT Output/Input Metadata**: Comprehensive tracking and management of VAT transactions
- **Withholding Tax Certificates**: Generate and manage e-Bupot certificates
- **Bulk Operations**: Process multiple invoices and tax documents efficiently
- **Automated Compliance**: Auto-create tax metadata on invoice submission

### 📊 Reports & Dashboards

- PPN Keluaran (VAT Output) Reports
- PPN Masukan (VAT Input) Reports
- PPN Rekonsiliasi (VAT Reconciliation)
- Tax Compliance Status Reports
- Customizable number cards for dashboard

### 🔧 Technical Features

- Clean, organized code structure following Frappe/ERPNext best practices
- Modular architecture with separated concerns (API, validation, export utilities)
- Comprehensive error handling and logging
- Batch processing support for large datasets
- Background task scheduling for automated operations

<https://github.com/user-attachments/assets/4d619612-a160-4c3c-b25b-934a7c85af5e>

<https://github.com/user-attachments/assets/dafae3d7-7f08-4584-9032-25edf23f3e39>

<br />

## Installation

### Quick Install

```bash
bench get-app erpnext_indonesia_localization
bench install-app erpnext_indonesia_localization
bench migrate
```

### Documentation

- 📘 [Installation Guide (English)](docs/manuals/Installation%20Documentation%20-%20ENG.pdf)
- 📘 [Installation Guide (Indonesian)](docs/manuals/Installation%20Documentation%20-%20ID.pdf)
- 👨‍💻 [Developer Guide](docs/DEVELOPER_GUIDE.md)
- 📡 [API Documentation](docs/API.md)
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- 📁 [Project Structure](docs/STRUCTURE.md)

### User Manuals

- 📖 [User Manual (English)](docs/manuals/User%20Manual%20ENG.pdf)
- 📖 [User Manual (Indonesian)](docs/manuals/User%20Manual%20IDN.pdf)
- 📖 [Coretax EIL Manual (English)](docs/manuals/User%20Manual%20Coretax%20EIL%20-%20ENG.pdf)
- 📖 [Coretax EIL Manual (Indonesian)](docs/manuals/User%20Manual%20Coretax%20EIL%20-%20ID.pdf)

<br />

## Quick Start Guide


### 1. Master Data Setup:
Before starting the eFaktur process, make sure the [following reference data](data/coretax_reference_master_data) has been imported into your ERPNext system use [data import tools](https://docs.frappe.io/erpnext/user/manual/en/data-import):
- CoreTax Transaction Code Ref
- CoreTax Barang Jasa Ref
- CoreTax Facility Stamp Ref
- CoreTax Additional Info Ref
- CoreTax Unit Ref

### 2. Initial Setup:
| **Doctype**   | **Field**                      | **Description**                                                       |
| ------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Company**   | `Company’s NITKU`              | Business Activity Location Identification Number (NITKU)              |
|               | `Use Company NITKU` (checkbox) | If checked, all reports use the parent company's NITKU                |
| **Branch**    | `Branch’s NITKU`               | Specific NITKU for each branch                                        |
| **Item**      | `Goods/Services Opt`           | A = Goods, B = Services                                               |
|               | `Goods/Services Ref`           | Linked to the “CoreTax Goods and Services Ref”                        |
| **UOM**       | `Unit Ref`                     | Reference code from Coretax, linked to “CoreTax Unit Ref”             |
| **Country**   | `CoreTax Country Ref`          | 3-letter uppercase country code (e.g., IDN for Indonesia)             |
| **Customer**  | `Customer ID Type`             | Options: TIN (NPWP), National ID (NIK), Passport, Other               |
|               | `Customer ID Number`           | Auto-filled based on selected ID type; from Tax ID if TIN is selected |
|               | `Customer Email as per Tax ID` | Must match the email registered with NPWP                             |
|               | `Customer’s NITKU`             | Customer's business location NITKU                                    |
|               | `Country`                      | Customer’s country code                                               |
| **Sales Taxes and Charges Template** | `Transaction Code`             | Coretax transaction code                                             |
|               | `Tax Additional Info`          | Required only for Transaction Code 07 or 08                           |
|               | `Tax Facility Stamp`           | Stamp details if applicable                                           |
|               | `Temporary Rate`               | Custom tax rate when applicable                                       |
|               | `Use Temporary Rate` (checkbox) | If checked, use Temporary rate



### 3. Transaction Setup:
| **Doctype**   | **Field**                      | **Description**                                                       |
| ------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Sales Invoice** | `Tax Custom Document`      | Filled if there are additional documents                                        |
|               | `Tax Custom Document Period:`  | Date of the additional document                                         |
|               | `Luxury Goods Tax Rate`        | Rate for luxury item taxation                                         |



### 4. Sales Taxes and Charges Template Setup:
| **Template Title**    | **Field**                      | **Value**                                                       |
| --------------------  | ------------------------------ | ----------------------------------------------------------------|
| **PPN Penjualan 11%** | `Company`                      | Select company name                                             |
|                       | `Type`                         | Select "On Net Total"                                           |
|                       | `Account Head`                 | Select Account head for VAT (PPN)                               |
|                       | `Cost Center`                  | Select Cost Center head for VAT (PPN)                           |
|                       | `Tax Rate`                     | 12                                                              |
|                       | `Use Temporary Rate`           | uncheck                                                         |
| **PPN Penjualan 12%** | `Company`                      | Select company name                                             |
|                       | `Type`                         | Select "On Net Total"                                           |
|                       | `Account Head`                 | Select Account head for VAT (PPN)                               |
|                       | `Cost Center`                  | Select Cost Center head for VAT (PPN)                           |
|                       | `Tax Rate`                     | 11                                                              |
|                       | `Use Temporary Rate`           | check                                                           |
|                       | `Temporary Rate`               | 12                                                              |


## Project Structure

The project follows a clean, organized structure:

```
erpnext-indonesia-localization/
├── erpnext_indonesia_localization/    # Main application
│   ├── api/                           # API integrations (Pajak.io)
│   ├── doc_events/                    # Document event handlers
│   ├── doctype/                       # Custom doctypes
│   ├── utils/                         # Utility functions
│   │   ├── api/                       # API utilities
│   │   ├── validation/                # Validation utilities
│   │   └── export/                    # Export utilities
│   ├── report/                        # Custom reports
│   ├── tasks/                         # Scheduled tasks
│   └── tests/                         # Test files
├── docs/                              # Documentation
│   ├── manuals/                       # User manuals (PDF)
│   └── *.md                          # Technical documentation
└── data/                              # Reference data
    └── coretax_reference_master_data/ # Master data files
```

For detailed structure information, see [STRUCTURE.md](docs/STRUCTURE.md).

## Development

### For Developers

- 📚 [Developer Guide](docs/DEVELOPER_GUIDE.md) - Comprehensive guide for developers
- 🏗️ [Project Structure](docs/STRUCTURE.md) - Detailed project structure documentation
- 🔄 [Structure Improvement Notes](docs/PROJECT_STRUCTURE_IMPROVEMENT.md) - Recent improvements

### Contributing

We welcome contributions! Please ensure:
- Code follows Frappe/ERPNext conventions
- All tests pass
- Documentation is updated
- Code is properly formatted

### Requirements

- ERPNext v15 or v16
- Python 3.10+
- Frappe Framework

## Support & Contact

#### Need assistance? Get in [touch with us.](mailto:info@agiletechnica.com)

- 🌐 Website: [www.agiletechnica.com](https://www.agiletechnica.com)
- 📧 Email: info@agiletechnica.com
- 🐛 Issues: Please report issues through GitHub Issues

<br />
<br />
<div align="center" style="padding-top: 0.75rem;">

 <a href="https://www.agiletechnica.com/" target="_blank">
  <img src=".github/logo_v3_light.png" style="height: 100px;">
 </a>
<br />
<br />

**Made with ❤️ by Agile Technica**

</div>
