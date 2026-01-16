// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	setup: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Purchase Invoice", frm.doc.company);
	},
	refresh: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Purchase Invoice", frm.doc.company);
	},
	company: function (frm) {
		hide_indonesia_fields_if_needed(frm, "Purchase Invoice", frm.doc.company);
	}
});
