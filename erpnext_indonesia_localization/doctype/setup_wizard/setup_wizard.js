// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Setup Wizard', {
	refresh: function(frm) {
		if (frm.doc.step_4_complete) {
			frm.add_custom_button(__('Complete Setup'), function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.doctype.setup_wizard.setup_wizard.complete_setup',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === "success") {
							frappe.msgprint(__("Setup completed successfully!"), __("Success"));
							frm.reload_doc();
						}
					}
				});
			}, __("Actions"));
		}
	}
});
