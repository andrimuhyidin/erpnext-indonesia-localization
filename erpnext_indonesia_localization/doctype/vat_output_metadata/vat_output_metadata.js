// Copyright (c) 2023, Agile Technica and contributors
// For license information, please see license.txt
function append_call_pajakio_api_button(frm){
    frm.add_custom_button(__('Call Pajak.io API'), function() {
        frappe.confirm(
            'Proceed to create a VAT Output?',
            function(){
                frappe.call({
                    method: 'erpnext_indonesia_localization.api.pajakio.create_vat_output_js',
                    args: {
                        name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.show_alert(r.message, 5);
                        }
                    }
                });
            },
            function(){
            }
        )
    });
}

function append_download_pdf_button(frm){
    frm.add_custom_button(__('Download PDF'), function() {
        frappe.confirm(
            'Proceed to download PDF?',
            function(){
                window.open('/api/method/erpnext_indonesia_localization.doctype.vat_output_metadata.vat_output_metadata.convert_base64_to_pdf?docname=' + frm.doc.name, '_blank');
            },
            function(){
            }
        )
    });
}

function append_upload_vat_button(frm){
    frm.add_custom_button(__('Upload VAT'), function() {
        frappe.confirm(
            'Proceed to upload VAT?',
            function(){
                frappe.call({
                    method: 'erpnext_indonesia_localization.api.pajakio.upload_vat_output',
                    args: {
                        doc: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.show_alert(r.message, 5);
                        }
                    }
                });
            },
            function(){
            }
        )
    });
}

frappe.ui.form.on('VAT Output Metadata', {
	 refresh: function(frm) {
	    if (frm.doc.docstatus === 0){
	        append_call_pajakio_api_button(frm);
	        
	        // Enhanced VAT Output buttons
	        if (frm.doc.transactionid) {
	            if (frm.doc.status === "Draft" || frm.doc.status === "To Be Reviewed") {
	                append_update_vat_output_button(frm);
	            }
	            if (frm.doc.status === "Approved") {
	                append_cancel_vat_output_button(frm);
	            }
	            if (frm.doc.status === "Draft") {
	                append_delete_vat_output_button(frm);
	            }
	            append_sync_from_pajakio_button(frm);
	        }
	    }
        if (frm.doc.transactionid && frm.doc.vat_upload_success === 0) {
            append_upload_vat_button(frm);
        }
        if (frm.doc.base64) {
            append_download_pdf_button(frm);
        }
	 }
});

// Bulk operations for list view
frappe.listview_settings['VAT Output Metadata'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Approved": "green",
			"To Be Reviewed": "orange",
			"Draft": "gray",
			"Rejected": "red",
			"Received PDF": "blue"
		};
		return [__(doc.status), status_colors[doc.status] || "gray", "status,=," + doc.status];
	},
	onload: function(listview) {
		listview.page.add_menu_item(__("Bulk Approve"), function() {
			const selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__("Please select at least one document"));
				return;
			}
			
			frappe.confirm(
				__("Are you sure you want to approve {0} documents?", [selected.length]),
				function() {
					frappe.call({
						method: 'erpnext_indonesia_localization.utils.bulk_operations.bulk_approve_vat_output',
						args: {
							metadata_names: selected.map(item => item.name)
						},
						callback: function(r) {
							if (r.message) {
								frappe.msgprint(__("Approved: {0}, Failed: {1}", [r.message.success_count, r.message.failure_count]));
								listview.refresh();
							}
						}
					});
				}
			);
		});
		
		listview.page.add_menu_item(__("Bulk Reject"), function() {
			const selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__("Please select at least one document"));
				return;
			}
			
			frappe.confirm(
				__("Are you sure you want to reject {0} documents?", [selected.length]),
				function() {
					frappe.call({
						method: 'erpnext_indonesia_localization.utils.bulk_operations.bulk_reject_vat_output',
						args: {
							metadata_names: selected.map(item => item.name)
						},
						callback: function(r) {
							if (r.message) {
								frappe.msgprint(__("Rejected: {0}, Failed: {1}", [r.message.success_count, r.message.failure_count]));
								listview.refresh();
							}
						}
					});
				}
			);
		});
		
		listview.page.add_menu_item(__("Bulk Delete via API"), function() {
			const selected = listview.get_checked_items();
			if (selected.length === 0) {
				frappe.msgprint(__("Please select at least one document"));
				return;
			}
			
			frappe.confirm(
				__("Are you sure you want to delete {0} documents via API?", [selected.length]),
				function() {
					// Get transaction IDs
					frappe.call({
						method: 'frappe.client.get_list',
						args: {
							doctype: 'VAT Output Metadata',
							filters: {name: ['in', selected.map(item => item.name)]},
							fields: ['transactionid']
						},
						callback: function(r) {
							if (r.message) {
								const transaction_ids = r.message
									.filter(item => item.transactionid)
									.map(item => item.transactionid);
								
								if (transaction_ids.length === 0) {
									frappe.msgprint(__("No documents with transaction ID found"));
									return;
								}
								
								frappe.call({
									method: 'erpnext_indonesia_localization.api.pajakio.delete_multiple_vat_output',
									args: {
										transaction_ids: transaction_ids
									},
									callback: function(result) {
										if (result.message && result.message.code === 200) {
											frappe.msgprint(__("Successfully deleted {0} documents", [transaction_ids.length]));
											listview.refresh();
										} else {
											frappe.msgprint(__("Error: {0}", [result.message ? result.message.message : "Unknown error"]));
										}
									}
								});
							}
						}
					});
				}
			);
		});
	}
};

function append_update_vat_output_button(frm) {
	frm.add_custom_button(__('Update VAT Output'), function() {
		frappe.prompt([
			{
				fieldname: 'update_fields',
				fieldtype: 'Small Text',
				label: __('Fields to Update (JSON format)'),
				description: __('Enter JSON object with fields to update, e.g. {"nofa": "123456789012345"}')
			}
		], function(values) {
			try {
				const update_data = JSON.parse(values.update_fields);
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.update_vat_output',
					args: {
						doc: frm.doc.name,
						update_data: update_data
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Output updated successfully'),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			} catch (e) {
				frappe.msgprint(__('Invalid JSON format: {0}', [e.message]));
			}
		}, __('Update VAT Output'));
	}).css({"color":"white", "background-color": "#5e64ff"});
}

function append_cancel_vat_output_button(frm) {
	frm.add_custom_button(__('Cancel VAT Output'), function() {
		frappe.confirm(
			__('Are you sure you want to cancel this VAT Output?'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.cancel_vat_output',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Output cancelled successfully'),
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

function append_delete_vat_output_button(frm) {
	frm.add_custom_button(__('Delete VAT Output'), function() {
		frappe.confirm(
			__('Are you sure you want to delete this VAT Output? This action cannot be undone.'),
			function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.api.pajakio.delete_vat_output',
					args: {
						doc: frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('VAT Output deleted successfully'),
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

function append_sync_from_pajakio_button(frm) {
	frm.add_custom_button(__('Sync from Pajak.io'), function() {
		frappe.call({
			method: 'erpnext_indonesia_localization.api.pajakio.get_list_vat_output',
			args: {
				filters: {
					transactionId: frm.doc.transactionid
				},
				page: 1,
				per_page: 1
			},
			callback: function(r) {
				if (!r.exc && r.message && r.message.data) {
					const data = r.message.data[0];
					if (data) {
						// Update document with synced data
						frappe.msgprint({
							title: __('Sync Result'),
							message: __('Found {0} record(s) from Pajak.io', [r.message.data.length]),
							indicator: 'green'
						});
						// Optionally update fields from synced data
						frm.reload_doc();
					} else {
						frappe.msgprint(__('No data found in Pajak.io'));
					}
				}
			}
		});
	}).css({"color":"white", "background-color": "#10b981"});
}
