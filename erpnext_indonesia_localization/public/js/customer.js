frappe.ui.form.on('Customer', {
    tax_id: function(frm) {
        frm.set_df_property('company_address_tax_id', 'reqd', frm.doc.tax_id ? 1 : 0);
        
        // Auto-verify NPWP if enabled
        if (frm.doc.tax_id && frm.doc.customer_id_type === "TIN") {
            verify_tax_id(frm, 'npwp', frm.doc.tax_id);
        }
    },
    
    customer_id_number: function(frm) {
        // Auto-verify NIK if customer_id_type is National ID
        if (frm.doc.customer_id_number && frm.doc.customer_id_type === "National ID") {
            verify_tax_id(frm, 'nik', frm.doc.customer_id_number);
        }
    },

	customer_id_type: function (frm) {
		set_customer_id_number_visibility(frm);
	},

	setup: function (frm) {
		auto_fill_tax_country_code_when_setup(frm);
		hide_indonesia_fields_if_needed(frm, "Customer");
	},
	
	refresh: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Customer");
	}
});

function auto_fill_tax_country_code_when_setup(frm) {
	if (frm.doc.coretax_country) {
			frappe.db.get_value("Country", frm.doc.coretax_country, "custom_coretax_countryref")
				.then(r => {
					if (r && r.message && r.message.custom_coretax_countryref) {
						frm.set_value("tax_country_code", r.message.custom_coretax_countryref);
					}
				})
				.catch(err => {
					// Error handling for v16 compatibility
					console.error('Error fetching Country CoreTax reference:', err);
				});
		}
}

function set_customer_id_number_visibility(frm) {
	if (frm.doc.customer_id_type == "TIN" || frm.doc.customer_id_type == "National ID") {
		frm.set_df_property("customer_id_number", "hidden", 1);
	} else {
		frm.set_df_property("customer_id_number", "hidden", 0);
	}
}

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
						
						// Optionally prevent save if verification fails
						// frm.set_value('tax_id', ''); // Clear invalid value
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
