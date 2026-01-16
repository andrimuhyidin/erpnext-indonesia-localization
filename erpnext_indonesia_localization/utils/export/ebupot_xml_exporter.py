# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


def generate_ebupot_xml(certificate_doc):
	"""
	Generate e-Bupot XML file in format compatible with e-Bupot Unifikasi DJP.
	
	Args:
		certificate_doc: Withholding Tax Certificate document
		
	Returns:
		File URL of generated XML file
	"""
	try:
		# Get company information
		company = frappe.get_doc("Company", certificate_doc.company if hasattr(certificate_doc, 'company') else frappe.defaults.get_default("company"))
		
		# Create XML root element
		root = ET.Element("eBupotUnifikasi")
		root.set("xmlns", "http://www.djponline.go.id/eBupotUnifikasi")
		
		# Header information
		header = ET.SubElement(root, "Header")
		ET.SubElement(header, "NPWP").text = clean_npwp(company.tax_id) if company.tax_id else ""
		ET.SubElement(header, "Nama").text = company.company_name or ""
		ET.SubElement(header, "TahunPajak").text = str(certificate_doc.certificate_date.year) if certificate_doc.certificate_date else str(datetime.now().year)
		ET.SubElement(header, "MasaPajak").text = str(certificate_doc.certificate_date.month).zfill(2) if certificate_doc.certificate_date else str(datetime.now().month).zfill(2)
		
		# Certificate data
		certificate = ET.SubElement(root, "BuktiPotong")
		
		# Certificate number
		ET.SubElement(certificate, "NomorBuktiPotong").text = certificate_doc.certificate_number or certificate_doc.name
		ET.SubElement(certificate, "TanggalBuktiPotong").text = format_date(certificate_doc.certificate_date) if certificate_doc.certificate_date else format_date(datetime.now().date())
		
		# Supplier information
		penerima = ET.SubElement(certificate, "Penerima")
		ET.SubElement(penerima, "NPWP").text = clean_npwp(certificate_doc.supplier_npwp) if certificate_doc.supplier_npwp else ""
		ET.SubElement(penerima, "Nama").text = certificate_doc.supplier_name or ""
		
		# Tax information
		pajak = ET.SubElement(certificate, "Pajak")
		ET.SubElement(pajak, "JenisPajak").text = map_tax_type_to_code(certificate_doc.tax_type)
		ET.SubElement(pajak, "JenisSetoran").text = "1"  # Default: Setoran sendiri
		ET.SubElement(pajak, "JumlahBruto").text = format_currency(certificate_doc.tax_base)
		ET.SubElement(pajak, "Tarif").text = format_percent(certificate_doc.tax_rate)
		ET.SubElement(pajak, "JumlahPajak").text = format_currency(certificate_doc.tax_amount)
		
		# Items (if any)
		if certificate_doc.ebupot_items:
			items = ET.SubElement(certificate, "Detail")
			for item in certificate_doc.ebupot_items:
				item_elem = ET.SubElement(items, "Item")
				ET.SubElement(item_elem, "KodeObjekPajak").text = item.tax_code or ""
				ET.SubElement(item_elem, "JumlahBruto").text = format_currency(item.tax_base)
				ET.SubElement(item_elem, "Tarif").text = format_percent(item.tax_rate)
				ET.SubElement(item_elem, "JumlahPajak").text = format_currency(item.tax_amount)
		
		# Convert to pretty XML string
		xml_string = prettify_xml(root)
		
		# Save XML file
		file_name = f"EBUPOT-{certificate_doc.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
		file_path = frappe.get_site_path('private', 'files', file_name)
		
		with open(file_path, "w", encoding="utf-8") as file:
			file.write(xml_string)
		
		# Create File document
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_url": f"/private/files/{file_name}",
			"file_name": file_name,
			"attached_to_doctype": certificate_doc.doctype,
			"attached_to_name": certificate_doc.name,
		})
		file_doc.save(ignore_permissions=True)
		
		return file_doc.file_url
		
	except Exception as e:
		frappe.log_error(f"Error generating e-Bupot XML: {str(e)}", "e-Bupot XML Export Error")
		raise frappe.ValidationError(_("Error generating e-Bupot XML: {0}").format(str(e)))


def clean_npwp(npwp):
	"""Clean NPWP format (remove dots and dashes)"""
	if not npwp:
		return ""
	return str(npwp).replace(".", "").replace("-", "").strip()


def format_date(date_obj):
	"""Format date to DD/MM/YYYY"""
	if not date_obj:
		return ""
	if isinstance(date_obj, str):
		return date_obj
	return date_obj.strftime("%d/%m/%Y")


def format_currency(amount):
	"""Format currency to string with 2 decimal places"""
	if not amount:
		return "0.00"
	return f"{float(amount):.2f}"


def format_percent(percent):
	"""Format percent to string with 2 decimal places"""
	if not percent:
		return "0.00"
	return f"{float(percent):.2f}"


def map_tax_type_to_code(tax_type):
	"""Map tax type to e-Bupot code"""
	tax_type_map = {
		"PPh 23": "23",
		"PPh 4(2)": "4(2)",
		"PPh 15": "15",
		"PPh 26": "26"
	}
	return tax_type_map.get(tax_type, "23")  # Default to PPh 23


def prettify_xml(elem):
	"""Return a pretty-printed XML string for the Element"""
	rough_string = ET.tostring(elem, encoding='unicode')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")
