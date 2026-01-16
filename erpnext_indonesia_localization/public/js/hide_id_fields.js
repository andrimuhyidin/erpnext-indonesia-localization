// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

/**
 * Hide Indonesia-specific fields if company country is not Indonesia
 * @param {Object} frm - Frappe form object
 * @param {String} doctype - Doctype name
 * @param {String} company - Company name (optional, will be fetched from frm if not provided)
 */
function hide_indonesia_fields_if_needed(frm, doctype, company) {
	if (!frm || !doctype) {
		return;
	}
	
	// Get company from form or parameter
	var company_name = company || frm.doc.company || frappe.defaults.get_default("company");
	
	if (!company_name) {
		// No company found, skip hiding
		return;
	}
	
	// Get company country
	frappe.db.get_value("Company", company_name, "country")
		.then(r => {
			if (r && r.message && r.message.country) {
				var country = r.message.country;
				var country_code = "";
				
				// Get country code if available
				frappe.db.get_value("Country", country, "code")
					.then(country_r => {
						if (country_r && country_r.message && country_r.message.code) {
							country_code = country_r.message.code;
						}
						
						// Check if country is Indonesia
						var is_indonesia = country === "Indonesia" || country_code === "ID" || country_code === "IDN";
						
						if (!is_indonesia) {
							// Hide Indonesia-specific fields
							var fields_to_hide = get_indonesia_fields_for_doctype(doctype);
							fields_to_hide.forEach(function(fieldname) {
								try {
									frm.set_df_property(fieldname, "hidden", 1);
								} catch (e) {
									// Field might not exist, ignore
									console.log("Field not found:", fieldname);
								}
							});
						} else {
							// Show Indonesia-specific fields
							var fields_to_show = get_indonesia_fields_for_doctype(doctype);
							fields_to_show.forEach(function(fieldname) {
								try {
									frm.set_df_property(fieldname, "hidden", 0);
								} catch (e) {
									// Field might not exist, ignore
									console.log("Field not found:", fieldname);
								}
							});
						}
					})
					.catch(err => {
						console.error("Error fetching country code:", err);
					});
			}
		})
		.catch(err => {
			console.error("Error fetching company country:", err);
		});
}

/**
 * Get list of Indonesia-specific fields for a doctype
 * @param {String} doctype - Doctype name
 * @returns {Array} Array of field names to hide
 */
function get_indonesia_fields_for_doctype(doctype) {
	var fields_map = {
		"Customer": [
			"tax_id",
			"customer_id_type",
			"customer_id_number",
			"customers_nitku",
			"coretax_country",
			"tax_country_code",
			"company_address_tax_id",
			"customer_email_as_per_tax_id",
			"nik"
		],
		"Supplier": [
			"tax_id",
			"supplier_id_type",
			"supplier_id_number",
			"suppliers_nitku"
		],
		"Company": [
			"tax_id",
			"nitku",
			"use_company_nitku",
			"companys_nitku"
		],
		"Sales Invoice": [
			"nomor_faktur",
			"nomor_faktur_pajak",
			"transaction_code",
			"tax_additional_info",
			"tax_facility_stamp",
			"tax_custom_document",
			"tax_custom_document_period",
			"tax_invoice_type"
		],
		"Purchase Invoice": [
			"tax_invoice_number",
			"transaction_code",
			"tax_additional_info",
			"custom_tanggal_faktur_pajak"
		],
		"Sales Taxes and Charges Template": [
			"transaction_code",
			"tax_additional_info",
			"tax_facility_stamp",
			"temporary_rate",
			"use_temporary_rate"
		]
	};
	
	return fields_map[doctype] || [];
}
