// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('VAT Output Return', {
	original_vat_output: function(frm) {
		if (frm.doc.original_vat_output) {
			// Load data from original VAT Output
			frappe.db.get_doc('VAT Output Metadata', frm.doc.original_vat_output)
				.then(doc => {
					if (doc) {
						// Copy relevant fields
						if (doc.npwp) frm.set_value('npwp', doc.npwp);
						if (doc.nama) frm.set_value('nama', doc.nama);
						if (doc.alamatjalan) frm.set_value('alamatjalan', doc.alamatjalan);
						if (doc.kota) frm.set_value('kota', doc.kota);
						if (doc.telp) frm.set_value('telp', doc.telp);
						if (doc.kdjenistransaksi) frm.set_value('kdjenistransaksi', doc.kdjenistransaksi);
					}
				});
		}
	},
	
	sales_invoice_return: function(frm) {
		if (frm.doc.sales_invoice_return) {
			frm.set_value('noinvoice', frm.doc.sales_invoice_return);
			frm.set_value('parent_doctype', 'Sales Invoice');
		}
	},
	
	refresh: function(frm) {
		if (frm.doc.docstatus === 0) {
			// Call Pajak.io API button
			if (!frm.doc.transactionid) {
				frm.add_custom_button(__('Call Pajak.io API'), function() {
					frappe.confirm(
						__('Proceed to create a VAT Output Return?'),
						function() {
							// Show loading indicator
							frappe.show_progress(__('Creating VAT Output Return...'), 0, 100);
							
							frappe.call({
								method: 'erpnext_indonesia_localization.api.pajakio.create_vat_output_return',
								args: {
									doc: frm.doc.name
								},
								freeze: true,
								freeze_message: __('Creating VAT Output Return...'),
								callback: function(r) {
									frappe.hide_progress();
									
									if (r.exc) {
										let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating VAT Output Return');
										frappe.msgprint({
											title: __('Error'),
											message: error_msg,
											indicator: 'red'
										});
									} else if (r.message) {
										let response = r.message;
										if (response.code && response.code === 200) {
											frappe.show_alert({
												message: response.message || __('VAT Output Return created successfully'),
												indicator: 'green'
											}, 5);
											frm.reload_doc();
										} else {
											frappe.msgprint({
												title: __('Warning'),
												message: response.message || __('VAT Output Return creation completed with warnings'),
												indicator: 'orange'
											});
											frm.reload_doc();
										}
									} else {
										frappe.show_alert({
											message: __('VAT Output Return created successfully'),
											indicator: 'green'
										}, 5);
										frm.reload_doc();
									}
								},
								error: function(r) {
									frappe.hide_progress();
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating VAT Output Return');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								}
							});
						}
					);
				}).css({"color":"white", "background-color": "#5e64ff"});
			}
			
			// Upload to DJP button
			if (frm.doc.transactionid && !frm.doc.vat_upload_success) {
				frm.add_custom_button(__('Upload to DJP'), function() {
					frappe.confirm(
						__('Proceed to upload VAT Output Return to DJP?'),
						function() {
							// Show loading indicator
							frappe.show_progress(__('Uploading VAT Output Return...'), 0, 100);
							
							frappe.call({
								method: 'erpnext_indonesia_localization.api.pajakio.upload_vat_output_return',
								args: {
									doc: frm.doc.name
								},
								freeze: true,
								freeze_message: __('Uploading VAT Output Return to DJP...'),
								callback: function(r) {
									frappe.hide_progress();
									
									if (r.exc) {
										let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while uploading VAT Output Return');
										frappe.msgprint({
											title: __('Error'),
											message: error_msg,
											indicator: 'red'
										});
									} else if (r.message) {
										let response = r.message;
										if (response.code && response.code === 200) {
											frappe.show_alert({
												message: response.message || __('VAT Output Return uploaded successfully'),
												indicator: 'green'
											}, 5);
											frm.reload_doc();
										} else {
											frappe.msgprint({
												title: __('Warning'),
												message: response.message || __('VAT Output Return upload completed with warnings'),
												indicator: 'orange'
											});
											frm.reload_doc();
										}
									} else {
										frappe.show_alert({
											message: __('VAT Output Return uploaded successfully'),
											indicator: 'green'
										}, 5);
										frm.reload_doc();
									}
								},
								error: function(r) {
									frappe.hide_progress();
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while uploading VAT Output Return');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								}
							});
						}
					);
				}).css({"color":"white", "background-color": "#10b981"});
			}
		}
	}
});
