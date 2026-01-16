// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier', {
	tax_id: function(frm) {
		// Auto-verify NPWP if enabled
		if (frm.doc.tax_id) {
			verify_tax_id(frm, 'npwp', frm.doc.tax_id);
		}
	},
	
	setup: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Supplier");
	},
	
	refresh: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Supplier");
	}
});

function verify_tax_id(frm, type, value) {
	// Check if auto-verify is enabled
	frappe.db.get_value('Indonesia Localization Settings', 'Indonesia Localization Settings', 'auto_verify_tax_id')
		.then(r => {
			if (!r || !r.message || !r.message.auto_verify_tax_id) {
				return; // Auto-verify is disabled
			}
			
			if (!value) {
				return; // No value to verify
			}
			
			// Show loading indicator
			frm.dashboard.add_indicator(__('Verifying...'), 'orange');
			
			var method = type === 'npwp' ? 'verify_npwp' : 'verify_nik';
			
			frappe.call({
				method: `erpnext_indonesia_localization.api.pajakio.${method}`,
				args: {
					[type]: value
				},
				callback: function(r) {
					frm.dashboard.clear_indicator();
					
					if (r.message && r.message.valid) {
						frm.dashboard.add_indicator(__('✓ Verified'), 'green');
						frappe.show_alert({
							message: __('Tax ID verified successfully'),
							indicator: 'green'
						}, 3);
					} else {
						frm.dashboard.add_indicator(__('✗ Verification Failed'), 'red');
						var error_msg = r.message && r.message.message ? r.message.message : __('Tax ID verification failed');
						frappe.show_alert({
							message: error_msg,
							indicator: 'red'
						}, 5);
					}
				},
				error: function(r) {
					frm.dashboard.clear_indicator();
					frm.dashboard.add_indicator(__('Verification Error'), 'red');
					console.error('Error verifying tax ID:', r);
				}
			});
		})
		.catch(err => {
			console.error('Error checking auto_verify_tax_id setting:', err);
		});
}
