# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from jinja2 import Environment, FileSystemLoader


class CoretaxXMLImporter(Document):
	"""
	Coretax XML Importer for VAT Input (PPN Masukan)
	Similar to Coretax XML Exporter but for Purchase Invoice
	"""
	def before_submit(self):
		self.status = "In Process"
		self.export_xml()

	def before_cancel(self):
		purchase_invoices = frappe.get_all("Purchase Invoice", {"coretax_xml_importer": self.name}, pluck="name")

		if len(purchase_invoices) <= 500:
			unlink_purchase_invoices(self.name)
		else:
			frappe.enqueue(
				method=unlink_purchase_invoices,
				queue="long",
				doc_name=self.name
			)

	@frappe.whitelist()
	def export_xml(self):
		invoice_docs, company_doc = fetch_purchase_invoices(doc=self)
		if len(invoice_docs) <= 0:
			frappe.throw("Purchase Invoices is Not Found. Please fetch the latest data")
		elif len(invoice_docs) <= 500:
			result = export_xml(invoice_docs, company_doc, doc=self)
			if result == "Failed":
				self.status = result
				frappe.throw("Exporting XML Failed")
			else:
				self.status = result
				return result
		else:
			frappe.enqueue(
				method=export_xml,
				queue="long",
				invoice_docs=invoice_docs,
				company_doc=company_doc,
				doc=self
			)


def export_xml(invoice_docs, company_doc, doc):
	"""Export Purchase Invoices to XML format"""
	try:
		tax_data = mapping_purchase_invoices(invoice_docs, company_doc, doc)
		generated_xml_file(tax_data, company_doc, doc)
		frappe.set_value("Coretax XML Importer", doc.name, "status", "Succeed")
		return "Succeed"
	except Exception:
		frappe.set_value("Coretax XML Importer", doc.name, "status", "Failed")
		frappe.log_error(title=f"CoreTax XML Importer Error on {doc.name}", message=frappe.get_traceback())
		return "Failed"


@frappe.whitelist()
def get_preview_purchase_invoice(company, start_invoice_date, end_invoice_date, branch=None):
	"""Get preview of Purchase Invoices for selected date range"""
	filters = {
		"docstatus": 1,
		"is_xml_generated": 0,
		"company": company,
		"bill_date": ["between", [start_invoice_date, end_invoice_date]],
		"taxes_and_charges": ["!=", ""]
	}

	if branch:
		filters["branch"] = branch

	invoices = frappe.get_all(
		"Purchase Invoice",
		filters=filters,
		fields=["name", "bill_date", "supplier", "grand_total", "total_taxes_and_charges"],
		order_by='bill_date'
	)

	if not invoices:
		return "<p>No purchase invoices found for the selected date range</p>"

	html = """
		<h3>Preview</h3>
		<table class="table table-bordered text-nowrap table-responsive">
			<tr>
				<th>No.</th>
				<th>Invoice Number</th>
				<th>Bill Date</th>
				<th>Supplier</th>
				<th>Supplier Name</th>
				<th>Grand Total (In Company Currency)</th>
				<th>Total Taxes and Charges (In Company Currency)</th>
			</tr>
	"""

	for idx, row in enumerate(invoices):
		supplier_name = frappe.get_value("Supplier", row.supplier, "supplier_name")
		idx += 1
		if idx > 10:
			break

		html += f"""
			<tr>
				<td>{idx}</td>
				<td>{row.name}</td>
				<td>{row.bill_date}</td>
				<td>{row.supplier}</td>
				<td>{supplier_name}</td>
				<td style="text-align: right;">{"{:,.2f}".format(row.grand_total)}</td>
				<td style="text-align: right;">{"{:,.2f}".format(row.total_taxes_and_charges)}</td>
			</tr>
		"""

	html += f"""
		</table>
		<h5>Showing only first {min(10, len(invoices))} rows out of {len(invoices)} </h5>
	"""

	return html


def fetch_purchase_invoices(doc):
	"""Fetch Purchase Invoices based on filters"""
	filters = {
		"docstatus": 1,
		"is_xml_generated": 0,
		"company": doc.company,
		"bill_date": ["between", [doc.start_invoice_date, doc.end_invoice_date]],
		"taxes_and_charges": ["!=", ""]
	}

	if doc.branch:
		filters["branch"] = doc.branch

	invoice_docs = frappe.get_all(
		"Purchase Invoice",
		filters=filters,
		fields=["name", "bill_date", "supplier", "transaction_code", "tax_additional_info"],
		order_by='bill_date'
	)

	company_doc = frappe.get_value("Company", doc.company, ["tax_id", "companys_nitku", "company_name"], as_dict=True)

	return invoice_docs, company_doc


def mapping_purchase_invoices(invoice_docs, company_doc, doc):
	"""Map Purchase Invoices to tax data structure"""
	tax_data = {
		"tin": company_doc.tax_id,
		"purchase_invoices": []
	}

	for invoice in invoice_docs:
		supplier_info = frappe.get_value("Supplier",
			invoice["supplier"],
			["supplier_name", "tax_id", "tax_country_code"],
			as_dict=True)

		invoice_entry = {
			"bill_date": str(invoice["bill_date"]),
			"kode_transaksi": invoice.get("transaction_code", ""),
			"additional_info": "" if invoice.get("tax_additional_info") in ["", None] else invoice["tax_additional_info"],
			"name": invoice["name"],
			"seller_tin": supplier_info.tax_id if supplier_info.tax_id else "",
			"supplier_name": supplier_info.supplier_name,
			"supplier_country_code": supplier_info.tax_country_code if supplier_info.tax_country_code else "ID",
			"items": []
		}

		pi_items = frappe.db.get_all(
			"Purchase Invoice Item",
			filters={
				"parent": invoice["name"],
				"docstatus": 1
			},
			fields=["item_name", "item_code", "qty", "uom", "discount_amount", "net_amount",
				"vat_amount", "net_rate"]
		)

		# Get tax rate from Purchase Taxes and Charges
		tax_template_result = frappe.get_all("Purchase Taxes and Charges",
			filters={"parent": invoice["name"], "idx": 1},
			fields=["rate"],
			limit=1
		)
		tax_rate = tax_template_result[0].rate if tax_template_result else 0

		for item in pi_items:
			invoice_entry["items"].append({
				"name": item["item_name"],
				"unit": item["uom"],
				"price": item["net_rate"],
				"qty": item["qty"],
				"total_discount": item["discount_amount"] * item["qty"] if item["discount_amount"] else 0,
				"tax_base": item["net_amount"],
				"vat": item["vat_amount"] if item["vat_amount"] else 0,
				"vatrate": int(tax_rate) if tax_rate else 0
			})

		tax_data["purchase_invoices"].append(invoice_entry)
		frappe.set_value("Purchase Invoice", invoice["name"], {
			"is_xml_generated": 1,
			"coretax_xml_importer": doc.name
		})

	return tax_data


def generated_xml_file(tax_data, company_doc, doc):
	"""Generate XML file from tax data"""
	template_dir = frappe.get_app_path('erpnext_indonesia_localization', "templates")
	env = Environment(loader=FileSystemLoader(template_dir))

	# Use same template or create new one for VAT Input
	template = env.get_template('tax_invoice_bulk.jinja')
	output = template.render(customer_sales_invoice_docs=tax_data)

	file_name = f"VAT Input Exporter {company_doc.company_name} {doc.start_invoice_date} to {doc.end_invoice_date}.xml"
	file_path = frappe.get_site_path('private', 'files', file_name)

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(output)

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_url": f"/private/files/{file_name}",
		"file_name": file_name,
		"attached_to_doctype": doc.doctype,
		"attached_to_name": doc.name,
	})

	file_doc.save(True)


def unlink_purchase_invoices(doc_name):
	"""Unlink Purchase Invoices from XML Importer"""
	purchase_invoices = frappe.get_all("Purchase Invoice", {"coretax_xml_importer": doc_name}, pluck="name")

	for purchase_invoice in purchase_invoices:
		frappe.set_value("Purchase Invoice", purchase_invoice, {
			"is_xml_generated": 0,
			"coretax_xml_importer": ""
		})

	file_result = frappe.get_all("File",
		filters={"attached_to_doctype": "Coretax XML Importer", "attached_to_name": doc_name},
		fields=["name"],
		limit=1
	)
	if file_result:
		frappe.delete_doc("File", file_result[0].name)
