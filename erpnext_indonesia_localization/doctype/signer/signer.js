// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Signer', {
	is_active: function(frm) {
		if (frm.doc.is_active && frm.doc.signer_id) {
			frappe.confirm(
				__('Set this signer as active in Pajak.io?'),
				function() {
					frappe.call({
						method: 'erpnext_indonesia_localization.api.pajakio.set_active_signer',
						args: {
							signer_id: frm.doc.signer_id
						},
						freeze: true,
						freeze_message: __('Setting signer as active...'),
						callback: function(r) {
							if (r.exc) {
								let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while setting signer as active');
								frappe.msgprint({
									title: __('Error'),
									message: error_msg,
									indicator: 'red'
								});
								frm.set_value('is_active', 0);
							} else {
								frappe.show_alert({
									message: __('Signer set as active successfully'),
									indicator: 'green'
								}, 5);
							}
						},
						error: function(r) {
							let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while setting signer as active');
							frappe.msgprint({
								title: __('Error'),
								message: error_msg,
								indicator: 'red'
							});
							frm.set_value('is_active', 0);
						}
					});
				},
				function() {
					frm.set_value('is_active', 0);
				}
			);
		}
	},
	
	refresh: function(frm) {
		// Create/Sync to Pajak.io button
		if (!frm.doc.signer_id) {
			frm.add_custom_button(__('Create in Pajak.io'), function() {
				frappe.confirm(
					__('Proceed to create Signer in Pajak.io?'),
					function() {
						frappe.call({
							method: 'erpnext_indonesia_localization.api.pajakio.create_signer',
							args: {
								signer_data: {
									signerName: frm.doc.signer_name,
									signerNpwp: frm.doc.signer_npwp,
									signerPosition: frm.doc.signer_position,
									signerEmail: frm.doc.signer_email || "",
									signerPhone: frm.doc.signer_phone || ""
								}
							},
							freeze: true,
							freeze_message: __('Creating Signer in Pajak.io...'),
							callback: function(r) {
								if (r.exc) {
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating Signer');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								} else if (r.message && r.message.code == 200 && r.message.data) {
									frm.set_value('signer_id', r.message.data.signerId || r.message.data.id);
									frm.set_value('api_response', JSON.stringify(r.message));
									frm.set_value('last_synced', new Date());
									frm.save();
									frappe.show_alert({
										message: __('Signer created successfully in Pajak.io'),
										indicator: 'green'
									}, 5);
								} else {
									let error_msg = r.message && r.message.message ? r.message.message : __('Unknown error occurred');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								}
							},
							error: function(r) {
								let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating Signer');
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
		
		// Sync from Pajak.io button
		frm.add_custom_button(__('Sync from Pajak.io'), function() {
			frappe.call({
				method: 'erpnext_indonesia_localization.api.pajakio.list_signer',
				args: {
					filters: frm.doc.signer_id ? { signerId: frm.doc.signer_id } : { signerNpwp: frm.doc.signer_npwp },
					page: 1,
					per_page: 1
				},
				freeze: true,
				freeze_message: __('Syncing Signer from Pajak.io...'),
				callback: function(r) {
					if (r.exc) {
						let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while syncing Signer');
						frappe.msgprint({
							title: __('Error'),
							message: error_msg,
							indicator: 'red'
						});
					} else if (r.message && r.message.code == 200 && r.message.data && r.message.data.length > 0) {
						let data = r.message.data[0];
						frm.set_value('signer_id', data.signerId || data.id);
						frm.set_value('signer_name', data.signerName || data.signer_name);
						frm.set_value('signer_npwp', data.signerNpwp || data.signer_npwp);
						frm.set_value('signer_position', data.signerPosition || data.signer_position);
						frm.set_value('signer_email', data.signerEmail || data.signer_email || '');
						frm.set_value('signer_phone', data.signerPhone || data.signer_phone || '');
						frm.set_value('is_active', data.isActive || data.is_active || 0);
						frm.set_value('api_response', JSON.stringify(r.message));
						frm.set_value('last_synced', new Date());
						frm.save();
						frappe.show_alert({
							message: __('Signer synced successfully'),
							indicator: 'green'
						}, 5);
					} else {
						frappe.msgprint({
							title: __('Not Found'),
							message: __('No matching Signer found in Pajak.io'),
							indicator: 'orange'
						});
					}
				},
				error: function(r) {
					let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while syncing Signer');
					frappe.msgprint({
						title: __('Error'),
						message: error_msg,
						indicator: 'red'
					});
				}
			});
		}).css({"color":"black", "background-color": "#e2e2e2"});
	}
});
