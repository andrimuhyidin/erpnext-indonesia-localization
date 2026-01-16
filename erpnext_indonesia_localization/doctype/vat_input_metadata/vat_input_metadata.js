// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('VAT Input Metadata', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 0) {
			// Call Pajak.io API button
			if (!frm.doc.transactionid) {
				append_call_pajakio_api_button(frm);
			}
			
			// Prepopulated from DJP button
			if (frm.doc.npwp) {
				append_prepopulated_button(frm);
			}
			
			// Update, Cancel, Delete buttons if transactionid exists
			if (frm.doc.transactionid) {
				if (frm.doc.status === "Draft" || frm.doc.status === "To Be Reviewed") {
					append_update_vat_input_button(frm);
				}
				if (frm.doc.status === "Approved") {
					append_cancel_vat_input_button(frm);
				}
				if (frm.doc.status === "Draft") {
					append_delete_vat_input_button(frm);
				}
				append_sync_status_button(frm);
			}
		}
		
		// Upload to DJP button
		if (frm.doc.transactionid && !frm.doc.vat_upload_success) {
			append_upload_vat_input_button(frm);
		}
	}
});

function append_call_pajakio_api_button(frm) {
	frm.add_custom_button(__('Call Pajak.io API'), function() {
		frappe.confirm(
			__('Proceed to create a VAT Input?'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.create_vat_input',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: r.message && r.message.message ? r.message.message : __('VAT Input created successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			}
		);
	}).css({"color":"white", "background-color": "#5e64ff"});
}

function append_upload_vat_input_button(frm) {
	frm.add_custom_button(__('Upload to DJP'), function() {
		frappe.confirm(
			__('Proceed to upload VAT Input to DJP?'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.upload_vat_input',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: r.message && r.message.message ? r.message.message : __('VAT Input uploaded successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			}
		);
	}).css({"color":"white", "background-color": "#10b981"});
}

function append_sync_status_button(frm) {
	frm.add_custom_button(__('Sync Status'), function() {
		frappe.call({
			method: 'erpnext_indonesia_localization.api.pajakio.get_detail_vat_input',
			args: {
				doc: frm.doc.name
			},
			callback: function(r) {
				if (!r.exc) {
					frappe.show_alert({
						message: __('Status synced successfully'),
						indicator: 'green'
					}, 3);
					frm.reload_doc();
				}
			}
		});
	}).css({"color":"white", "background-color": "#6366f1"});
}

function append_prepopulated_button(frm) {
	frm.add_custom_button(__('Prepopulated from DJP'), function() {
		if (!frm.doc.npwp) {
			frappe.msgprint(__('Please enter Supplier NPWP first'));
			return;
		}
		
		frappe.call({
			method: 'erpnext_indonesia_localization.api.pajakio.prepopulated_vat_input',
			args: {
				supplier_npwp: frm.doc.npwp
			},
			callback: function(r) {
				if (!r.exc && r.message && r.message.data) {
					show_prepopulated_dialog(frm, r.message.data);
				} else {
					frappe.msgprint(__('No prepopulated data found'));
				}
			}
		});
	}).css({"color":"white", "background-color": "#8b5cf6"});
}

function show_prepopulated_dialog(frm, faktur_list) {
	let dialog = new frappe.ui.Dialog({
		title: __('Select Faktur from DJP'),
		fields: [
			{
				fieldtype: 'HTML',
				options: '<div id="prepopulated-list"></div>'
			}
		],
		primary_action_label: __('Select'),
		primary_action: function() {
			const selected = dialog.selected_faktur;
			if (selected) {
				populate_from_faktur(frm, selected);
				dialog.hide();
			}
		}
	});
	
	// Build list HTML
	let html = '<table class="table table-bordered"><thead><tr><th>No Faktur</th><th>Tanggal</th><th>Supplier</th><th>Total</th></tr></thead><tbody>';
	faktur_list.forEach(faktur => {
		html += `<tr onclick="dialog.selected_faktur = ${JSON.stringify(faktur).replace(/"/g, '&quot;')}; this.style.backgroundColor='#e0e7ff';">
			<td>${faktur.nofa || ''}</td>
			<td>${faktur.tanggalFaktur || ''}</td>
			<td>${faktur.nama || ''}</td>
			<td>${faktur.total || 0}</td>
		</tr>`;
	});
	html += '</tbody></table>';
	
	dialog.fields_dict[0].$wrapper.html(html);
	dialog.selected_faktur = null;
	dialog.show();
}

function populate_from_faktur(frm, faktur) {
	// Populate fields from selected faktur
	if (faktur.nofa) frm.set_value('nofa', faktur.nofa);
	if (faktur.tanggalFaktur) frm.set_value('tanggalfaktur', faktur.tanggalFaktur);
	if (faktur.masaPajak) frm.set_value('masapajak', faktur.masaPajak);
	if (faktur.tahunPajak) frm.set_value('tahunpajak', faktur.tahunPajak);
	if (faktur.kdJenisTransaksi) frm.set_value('kdjenistransaksi', faktur.kdJenisTransaksi);
	
	// Populate barangjasa if available
	if (faktur.barangJasa && Array.isArray(faktur.barangJasa)) {
		frm.clear_table('barangjasa');
		faktur.barangJasa.forEach(item => {
			frm.add_child('barangjasa', {
				nama: item.nama || '',
				jumlah: item.jumlah || 0,
				harga: item.harga || 0,
				dpp: item.dpp || 0,
				ppn: item.ppn || 0,
				diskon: item.diskon || 0,
				tarifppnbm: item.tarifppnbm || 0
			});
		});
		frm.refresh_field('barangjasa');
	}
	
	frappe.show_alert({
		message: __('Data populated from DJP'),
		indicator: 'green'
	}, 3);
}

function append_update_vat_input_button(frm) {
	frm.add_custom_button(__('Update VAT Input'), function() {
		frappe.prompt([
			{
				fieldname: 'update_fields',
				fieldtype: 'Small Text',
				label: __('Fields to Update (JSON format)'),
				description: __('Enter JSON object with fields to update')
			}
		], function(values) {
			try {
				const update_data = JSON.parse(values.update_fields);
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.update_vat_input',
					args: {
						doc: frm.doc.name,
						update_data: update_data
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Input updated successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			} catch (e) {
				frappe.msgprint(__('Invalid JSON format: {0}', [e.message]));
			}
		}, __('Update VAT Input'));
	}).css({"color":"white", "background-color": "#5e64ff"});
}

function append_cancel_vat_input_button(frm) {
	frm.add_custom_button(__('Cancel VAT Input'), function() {
		frappe.confirm(
			__('Are you sure you want to cancel this VAT Input?'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.cancel_vat_input',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Input cancelled successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			}
		);
	}).css({"color":"white", "background-color": "#f59e0b"});
}

function append_delete_vat_input_button(frm) {
	frm.add_custom_button(__('Delete VAT Input'), function() {
		frappe.confirm(
			__('Are you sure you want to delete this VAT Input? This action cannot be undone.'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.delete_vat_input',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Input deleted successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			}
		);
	}).css({"color":"white", "background-color": "#ef4444"});
}
