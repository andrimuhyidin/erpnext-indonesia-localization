// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coretax XML Exporter', {
    onload: function(frm) {
        update_sales_invoice_list(frm);
    },

    refresh: function(frm) {
        if (frm.doc.status == "Failed") {
            toggle_retry_button(frm=frm);
        }
        
        // Add Validate Before Export button
        if (frm.doc.company && frm.doc.start_invoice_date && frm.doc.end_invoice_date && frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Validate Before Export"), function() {
                validate_before_export(frm);
            }).css({"color":"white", "background-color": "#5e64ff"});
        }
    },

    get_sales_invoice: function(frm) {
        if (frm.doc.start_invoice_date && frm.doc.end_invoice_date && frm.doc.company) {
            frappe.call(
                "erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter.get_preview_sales_invoice",
                {
                    company: frm.doc.company,
                    start_invoice_date: frm.doc.start_invoice_date,
                    end_invoice_date: frm.doc.end_invoice_date,
                    branch: frm.doc.branch
                }
            ).then(r => {
                frm.set_df_property("sales_invoice_list", "hidden", false);
                frm.set_df_property("sales_invoice_list", "options", r.message);
                frm.set_value("html", r.message);
            });
        } else {
            frappe.msgprint("Please select a Company and set a Date Range before proceeding.");
        }
    }
});


function toggle_retry_button(frm){
	frm.add_custom_button(__("Retry"), function() {
        frm.call("export_xml", {}).then(r => {
            if (r.message) {
                frm.set_value("status", r.message);
                frm.save("Update");
            }
        });
    }).css({"color":"black", "background-color": "#e2e2e2"});
}

function update_sales_invoice_list(frm) {
	if(frm.doc.html) {
		frm.set_df_property("sales_invoice_list", "options", frm.doc.html);
	} else {
		frm.set_df_property("sales_invoice_list", "hidden", true);
	}
}

function validate_before_export(frm) {
	frappe.call({
		method: "erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter.get_validation_results",
		args: {
			company: frm.doc.company,
			start_invoice_date: frm.doc.start_invoice_date,
			end_invoice_date: frm.doc.end_invoice_date,
			branch: frm.doc.branch
		}
	}).then(r => {
		var validation_result = r.message;
		var message = `<h4>Validation Summary</h4>
			<p><strong>Total:</strong> ${validation_result.total} invoices</p>
			<p><strong>Valid:</strong> <span style="color: green;">${validation_result.valid}</span></p>
			<p><strong>Invalid:</strong> <span style="color: red;">${validation_result.invalid}</span></p>`;
		
		if (validation_result.invalid > 0) {
			message += `<h5>Invalid Invoices:</h5><ul>`;
			var invalid_count = 0;
			for (var i = 0; i < validation_result.results.length && invalid_count < 10; i++) {
				var result = validation_result.results[i];
				if (!result.is_valid) {
					message += `<li><strong>${result.invoice_name}</strong>: ${result.errors.join(', ')}</li>`;
					invalid_count++;
				}
			}
			if (validation_result.invalid > 10) {
				message += `<li>... and ${validation_result.invalid - 10} more</li>`;
			}
			message += `</ul>`;
		}
		
		frappe.msgprint({
			title: __("Validation Results"),
			message: message,
			indicator: validation_result.invalid > 0 ? "orange" : "green"
		});
	});
}
