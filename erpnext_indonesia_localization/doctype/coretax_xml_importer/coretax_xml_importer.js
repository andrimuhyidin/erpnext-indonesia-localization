// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coretax XML Importer', {
	refresh: function(frm) {
		if (frm.doc.company && frm.doc.start_invoice_date && frm.doc.end_invoice_date) {
			frm.add_custom_button(__('Get Purchase Invoice'), function() {
				frappe.call({
					method: 'erpnext_indonesia_localization.doctype.coretax_xml_importer.coretax_xml_importer.get_preview_purchase_invoice',
					args: {
						company: frm.doc.company,
						start_invoice_date: frm.doc.start_invoice_date,
						end_invoice_date: frm.doc.end_invoice_date,
						branch: frm.doc.branch
					},
					callback: function(r) {
						if (r.message) {
							frm.set_value('purchase_invoice_list', r.message);
						}
					}
				});
			});
		}
	}
});
