// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Income Recipient', {
	refresh: function(frm) {
		// Create/Sync to Pajak.io button
		if (!frm.doc.recipient_id) {
			frm.add_custom_button(__('Create in Pajak.io'), function() {
				frappe.confirm(
					__('Proceed to create Income Recipient in Pajak.io?'),
					function() {
						frappe.call({
							method: 'erpnext_indonesia_localization.api.pajakio.create_income_recipient',
							args: {
								recipient_data: {
									recipientName: frm.doc.recipient_name,
									recipientNpwp: frm.doc.recipient_npwp,
									recipientNik: frm.doc.recipient_nik || "",
									recipientType: frm.doc.recipient_type,
									address: frm.doc.address || "",
									city: frm.doc.city || "",
									postalCode: frm.doc.postal_code || "",
									phone: frm.doc.phone || "",
									email: frm.doc.email || ""
								}
							},
							freeze: true,
							freeze_message: __('Creating Income Recipient in Pajak.io...'),
							callback: function(r) {
								if (r.exc) {
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating Income Recipient');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								} else if (r.message && r.message.code == 200 && r.message.data) {
									frm.set_value('recipient_id', r.message.data.recipientId || r.message.data.id);
									frm.set_value('api_response', JSON.stringify(r.message));
									frm.set_value('last_synced', new Date());
									frm.save();
									frappe.show_alert({
										message: __('Income Recipient created successfully in Pajak.io'),
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
								let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while creating Income Recipient');
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
		} else {
			// Update button
			frm.add_custom_button(__('Update in Pajak.io'), function() {
				frappe.confirm(
					__('Proceed to update Income Recipient in Pajak.io?'),
					function() {
						frappe.call({
							method: 'erpnext_indonesia_localization.api.pajakio.update_income_recipient',
							args: {
								recipient_id: frm.doc.recipient_id,
								update_data: {
									recipientName: frm.doc.recipient_name,
									recipientNpwp: frm.doc.recipient_npwp,
									recipientNik: frm.doc.recipient_nik || "",
									recipientType: frm.doc.recipient_type,
									address: frm.doc.address || "",
									city: frm.doc.city || "",
									postalCode: frm.doc.postal_code || "",
									phone: frm.doc.phone || "",
									email: frm.doc.email || ""
								}
							},
							freeze: true,
							freeze_message: __('Updating Income Recipient in Pajak.io...'),
							callback: function(r) {
								if (r.exc) {
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while updating Income Recipient');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								} else {
									frm.set_value('api_response', JSON.stringify(r.message));
									frm.set_value('last_synced', new Date());
									frm.save();
									frappe.show_alert({
										message: __('Income Recipient updated successfully'),
										indicator: 'green'
									}, 5);
								}
							},
							error: function(r) {
								let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while updating Income Recipient');
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
			
			// Delete button
			frm.add_custom_button(__('Delete from Pajak.io'), function() {
				frappe.confirm(
					__('Are you sure you want to delete this Income Recipient from Pajak.io? This action cannot be undone.'),
					function() {
						frappe.call({
							method: 'erpnext_indonesia_localization.api.pajakio.delete_income_recipient',
							args: {
								recipient_id: frm.doc.recipient_id
							},
							freeze: true,
							freeze_message: __('Deleting Income Recipient from Pajak.io...'),
							callback: function(r) {
								if (r.exc) {
									let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while deleting Income Recipient');
									frappe.msgprint({
										title: __('Error'),
										message: error_msg,
										indicator: 'red'
									});
								} else {
									frm.set_value('recipient_id', '');
									frm.set_value('api_response', JSON.stringify(r.message));
									frm.set_value('last_synced', new Date());
									frm.save();
									frappe.show_alert({
										message: __('Income Recipient deleted successfully from Pajak.io'),
										indicator: 'green'
									}, 5);
								}
							},
							error: function(r) {
								let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while deleting Income Recipient');
								frappe.msgprint({
									title: __('Error'),
									message: error_msg,
									indicator: 'red'
								});
							}
						});
					}
				);
			}).css({"color":"white", "background-color": "#ef4444"});
		}
		
		// Sync from Pajak.io button
		frm.add_custom_button(__('Sync from Pajak.io'), function() {
			frappe.call({
				method: 'erpnext_indonesia_localization.api.pajakio.list_income_recipient',
				args: {
					filters: frm.doc.recipient_id ? { recipientId: frm.doc.recipient_id } : { recipientNpwp: frm.doc.recipient_npwp },
					page: 1,
					per_page: 1
				},
				freeze: true,
				freeze_message: __('Syncing Income Recipient from Pajak.io...'),
				callback: function(r) {
					if (r.exc) {
						let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while syncing Income Recipient');
						frappe.msgprint({
							title: __('Error'),
							message: error_msg,
							indicator: 'red'
						});
					} else if (r.message && r.message.code == 200 && r.message.data && r.message.data.length > 0) {
						let data = r.message.data[0];
						frm.set_value('recipient_id', data.recipientId || data.id);
						frm.set_value('recipient_name', data.recipientName || data.recipient_name);
						frm.set_value('recipient_npwp', data.recipientNpwp || data.recipient_npwp);
						frm.set_value('recipient_nik', data.recipientNik || data.recipient_nik || '');
						frm.set_value('recipient_type', data.recipientType || data.recipient_type);
						frm.set_value('address', data.address || '');
						frm.set_value('city', data.city || '');
						frm.set_value('postal_code', data.postalCode || data.postal_code || '');
						frm.set_value('phone', data.phone || '');
						frm.set_value('email', data.email || '');
						frm.set_value('api_response', JSON.stringify(r.message));
						frm.set_value('last_synced', new Date());
						frm.save();
						frappe.show_alert({
							message: __('Income Recipient synced successfully'),
							indicator: 'green'
						}, 5);
					} else {
						frappe.msgprint({
							title: __('Not Found'),
							message: __('No matching Income Recipient found in Pajak.io'),
							indicator: 'orange'
						});
					}
				},
				error: function(r) {
					let error_msg = r._server_messages ? JSON.parse(r._server_messages).join('\n') : __('An error occurred while syncing Income Recipient');
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
