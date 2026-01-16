// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Withholding Tax Certificate', {
	purchase_invoice: function(frm) {
		if (frm.doc.purchase_invoice && !frm.doc.supplier_name) {
			frm.call({
				method: "load_from_purchase_invoice"
			}).then(r => {
				frm.refresh();
			});
		}
	},
	
	tax_base: function(frm) {
		calculate_tax_amount(frm);
	},
	
	tax_rate: function(frm) {
		calculate_tax_amount(frm);
	},
	
	refresh: function(frm) {
		if (frm.doc.docstatus === 0) {
			// Create via Pajak.io API button (preferred method)
			if (!frm.doc.transactionid) {
				frm.add_custom_button(__("Create via Pajak.io API"), function() {
					frappe.confirm(
						__('Proceed to create Withholding Tax via Pajak.io API?'),
						function() {
							frm.call({
								method: "call_pajakio_api"
							}).then(r => {
								if (!r.exc) {
									frappe.show_alert({
										message: __("Withholding Tax created successfully"),
										indicator: "green"
									}, 5);
									frm.reload_doc();
								}
							});
						}
					);
				}).css({"color":"white", "background-color": "#5e64ff"});
			}
			
			// Upload to DJP button
			if (frm.doc.transactionid && frm.doc.xml_export_status !== "Exported") {
				frm.add_custom_button(__("Upload to DJP"), function() {
					frappe.confirm(
						__('Proceed to upload Withholding Tax to DJP?'),
						function() {
							frappe.call({
								method: 'erpnext_indonesia_localization.api.pajakio.upload_withholding_tax',
								args: {
									doc: frm.doc.name
								}
							}).then(r => {
								if (!r.exc) {
									frappe.show_alert({
										message: __("Withholding Tax uploaded successfully"),
										indicator: "green"
									}, 5);
									frm.reload_doc();
								}
							});
						}
					);
				}).css({"color":"white", "background-color": "#10b981"});
			}
			
			// Sync Status button
			if (frm.doc.transactionid) {
				frm.add_custom_button(__("Sync Status"), function() {
					frm.call({
						method: "sync_status_from_pajakio"
					}).then(r => {
						if (!r.exc) {
							frappe.show_alert({
								message: __("Status synced successfully"),
								indicator: "green"
							}, 3);
							frm.reload_doc();
						}
					});
				}).css({"color":"white", "background-color": "#6366f1"});
				
				// Get Tax Codes button
				frm.add_custom_button(__("Get Tax Codes"), function() {
					frm.call({
						method: "get_code_of_type"
					}).then(r => {
						if (!r.exc && r.message && r.message.data) {
							show_tax_codes_dialog(r.message.data);
						}
					});
				}).css({"color":"white", "background-color": "#8b5cf6"});
			}
			
			// Legacy XML Export button (for backward compatibility)
			if (frm.doc.status !== "Draft" && !frm.doc.transactionid) {
				frm.add_custom_button(__("Export to e-Bupot XML (Legacy)"), function() {
					frappe.confirm(
						__('This will export to XML format. For API integration, use "Create via Pajak.io API" instead. Continue?'),
						function() {
							frm.call({
								method: "export_to_ebupot_xml",
								doc: frm.doc
							}).then(r => {
								if (r.message) {
									frappe.msgprint({
										message: __("e-Bupot XML exported successfully"),
										indicator: "green"
									});
									frm.reload_doc();
								}
							});
						}
					);
				}).css({"color":"black", "background-color": "#e2e2e2"});
			}
		}
	}
});

function calculate_tax_amount(frm) {
	if (frm.doc.tax_base && frm.doc.tax_rate) {
		var tax_amount = (frm.doc.tax_base * frm.doc.tax_rate) / 100;
		frm.set_value("tax_amount", tax_amount);
	}
}

function show_tax_codes_dialog(tax_codes) {
	let dialog = new frappe.ui.Dialog({
		title: __('Tax Codes (Kode Objek Pajak)'),
		fields: [
			{
				fieldtype: 'HTML',
				options: '<div id="tax-codes-list"></div>'
			}
		]
	});
	
	// Build list HTML
	let html = '<table class="table table-bordered"><thead><tr><th>Code</th><th>Description</th><th>Rate</th></tr></thead><tbody>';
	if (Array.isArray(tax_codes)) {
		tax_codes.forEach(code => {
			html += `<tr>
				<td>${code.code || ''}</td>
				<td>${code.description || ''}</td>
				<td>${code.rate || ''}%</td>
			</tr>`;
		});
	} else if (typeof tax_codes === 'object') {
		// Handle object format
		Object.keys(tax_codes).forEach(key => {
			html += `<tr>
				<td>${key}</td>
				<td>${tax_codes[key].description || ''}</td>
				<td>${tax_codes[key].rate || ''}%</td>
			</tr>`;
		});
	}
	html += '</tbody></table>';
	
	dialog.fields_dict[0].$wrapper.html(html);
	dialog.show();
}
