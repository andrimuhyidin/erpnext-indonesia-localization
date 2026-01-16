// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('SPT Masa PPN', {
	refresh: function(frm) {
		if (frm.doc.status === "Draft" || !frm.doc.status) {
			frm.add_custom_button(__('Generate SPT'), function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.doctype.spt_masa_ppn.spt_masa_ppn.generate_spt',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === "success") {
							frappe.msgprint(__("SPT generated successfully!"), __("Success"));
							frm.reload_doc();
						}
					}
				});
			}, __("Actions"));
		}
		
		if (frm.doc.status === "Generated") {
			frm.add_custom_button(__('Validate Reconciliation'), function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.doctype.spt_masa_ppn.spt_masa_ppn.validate_reconciliation',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let message = "";
							if (r.message.complete) {
								message = __("Reconciliation is complete and valid.");
							} else {
								message = __("Reconciliation validation found issues.");
							}
							
							if (r.message.warnings && r.message.warnings.length > 0) {
								message += "\n\n" + __("Warnings:") + "\n" + r.message.warnings.join("\n");
							}
							
							if (r.message.errors && r.message.errors.length > 0) {
								message += "\n\n" + __("Errors:") + "\n" + r.message.errors.join("\n");
							}
							
							frappe.msgprint(message, __("Reconciliation Validation"));
						}
					}
				});
			}, __("Actions"));
			
			frm.add_custom_button(__('Export to DJP Format'), function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.doctype.spt_masa_ppn.spt_masa_ppn.export_to_djp_format',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === "success") {
							frappe.msgprint(__("SPT exported successfully!"), __("Success"));
							frm.reload_doc();
						}
					}
				});
			}, __("Actions"));
		}
	}
});
