# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SPTMasaPPN(Document):
	@frappe.whitelist()
	def generate_spt(self):
		"""
		Generate SPT Masa PPN from PPN Keluaran and PPN Masukan
		"""
		try:
			# Calculate PPN Keluaran (Output VAT)
			ppn_keluaran = self.calculate_ppn_keluaran()
			
			# Calculate PPN Masukan (Input VAT)
			ppn_masukan = self.calculate_ppn_masukan()
			
			# Calculate reconciliation
			selisih = flt(ppn_keluaran) - flt(ppn_masukan)
			
			self.total_ppn_keluaran = ppn_keluaran
			self.total_ppn_masukan = ppn_masukan
			
			if selisih > 0:
				self.ppn_kurang_bayar = selisih
				self.ppn_lebih_bayar = 0
			else:
				self.ppn_kurang_bayar = 0
				self.ppn_lebih_bayar = abs(selisih)
			
			self.status = "Generated"
			self.save()
			
			frappe.msgprint(_("SPT Masa PPN generated successfully"), indicator="green")
			
			return {
				"status": "success",
				"ppn_keluaran": ppn_keluaran,
				"ppn_masukan": ppn_masukan,
				"selisih": selisih
			}
			
		except Exception as e:
			frappe.log_error(f"Error generating SPT: {str(e)}", "SPT Generation Error")
			frappe.throw(_("Error generating SPT: {0}").format(str(e)))
	
	def calculate_ppn_keluaran(self):
		"""
		Calculate total PPN Keluaran for the period
		"""
		# Get Sales Invoices for the period
		filters = {
			"docstatus": 1,
			"company": self.company,
			"posting_date": [
				"between",
				[
					f"{self.tahun_pajak}-{self.masa_pajak}-01",
					f"{self.tahun_pajak}-{self.masa_pajak}-31"
				]
			],
			"total_taxes_and_charges": [">", 0]
		}
		
		sales_invoices = frappe.get_all(
			"Sales Invoice",
			filters=filters,
			fields=["total_taxes_and_charges"]
		)
		
		total = sum(flt(inv.total_taxes_and_charges) for inv in sales_invoices)
		return total
	
	def calculate_ppn_masukan(self):
		"""
		Calculate total PPN Masukan for the period
		"""
		# Get Purchase Invoices for the period
		filters = {
			"docstatus": 1,
			"company": self.company,
			"bill_date": [
				"between",
				[
					f"{self.tahun_pajak}-{self.masa_pajak}-01",
					f"{self.tahun_pajak}-{self.masa_pajak}-31"
				]
			],
			"total_taxes_and_charges": [">", 0]
		}
		
		purchase_invoices = frappe.get_all(
			"Purchase Invoice",
			filters=filters,
			fields=["total_taxes_and_charges"]
		)
		
		total = sum(flt(inv.total_taxes_and_charges) for inv in purchase_invoices)
		return total
	
	@frappe.whitelist()
	def validate_reconciliation(self):
		"""
		Validate SPT reconciliation - check completeness and data integrity
		"""
		try:
			validation_results = {
				"complete": True,
				"warnings": [],
				"errors": []
			}
			
			# Check if PPN Keluaran and Masukan are calculated
			if not self.total_ppn_keluaran:
				validation_results["warnings"].append("PPN Keluaran belum dihitung")
				validation_results["complete"] = False
			
			if not self.total_ppn_masukan:
				validation_results["warnings"].append("PPN Masukan belum dihitung")
				validation_results["complete"] = False
			
			# Validate data completeness
			si_count = frappe.db.count("Sales Invoice", {
				"docstatus": 1,
				"company": self.company,
				"posting_date": [
					"between",
					[
						f"{self.tahun_pajak}-{self.masa_pajak}-01",
						f"{self.tahun_pajak}-{self.masa_pajak}-31"
					]
				],
				"total_taxes_and_charges": [">", 0]
			})
			
			pi_count = frappe.db.count("Purchase Invoice", {
				"docstatus": 1,
				"company": self.company,
				"bill_date": [
					"between",
					[
						f"{self.tahun_pajak}-{self.masa_pajak}-01",
						f"{self.tahun_pajak}-{self.masa_pajak}-31"
					]
				],
				"total_taxes_and_charges": [">", 0]
			})
			
			if si_count == 0 and pi_count == 0:
				validation_results["warnings"].append("Tidak ada faktur untuk periode ini")
			
			# Check if reconciliation is balanced
			selisih = flt(self.total_ppn_keluaran) - flt(self.total_ppn_masukan)
			if abs(selisih) > 0.01:  # Allow small rounding differences
				validation_results["warnings"].append(
					f"Selisih PPN: {selisih:,.2f} (Keluaran: {self.total_ppn_keluaran:,.2f}, Masukan: {self.total_ppn_masukan:,.2f})"
				)
			
			return validation_results
			
		except Exception as e:
			frappe.log_error(f"Error validating reconciliation: {str(e)}", "SPT Validation Error")
			return {
				"complete": False,
				"errors": [str(e)],
				"warnings": []
			}
	
	@frappe.whitelist()
	def export_to_djp_format(self):
		"""
		Export SPT to DJP format (CSV/Excel)
		"""
		try:
			if self.status != "Generated":
				frappe.throw(_("Please generate SPT first"))
			
			# Validate reconciliation first
			validation = self.validate_reconciliation()
			if validation.get("errors"):
				frappe.throw(_("Validation errors found: {0}").format(", ".join(validation["errors"])))
			
			# Generate CSV/Excel file
			import csv
			from frappe.utils import get_site_path
			import os
			
			file_name = f"SPT_Masa_PPN_{self.company}_{self.masa_pajak}_{self.tahun_pajak}.csv"
			file_path = get_site_path('private', 'files', file_name)
			
			# Create CSV content
			with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(['SPT Masa PPN'])
				writer.writerow(['Company', self.company])
				writer.writerow(['Masa Pajak', self.masa_pajak])
				writer.writerow(['Tahun Pajak', self.tahun_pajak])
				writer.writerow(['Total PPN Keluaran', self.total_ppn_keluaran])
				writer.writerow(['Total PPN Masukan', self.total_ppn_masukan])
				writer.writerow(['PPN Kurang Bayar', self.ppn_kurang_bayar])
				writer.writerow(['PPN Lebih Bayar', self.ppn_lebih_bayar])
				
				# Add validation warnings if any
				if validation.get("warnings"):
					writer.writerow([])
					writer.writerow(['Validation Warnings'])
					for warning in validation["warnings"]:
						writer.writerow([warning])
			
			# Attach file to document
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_url": f"/private/files/{file_name}",
				"file_name": file_name,
				"attached_to_doctype": self.doctype,
				"attached_to_name": self.name,
			})
			file_doc.save(ignore_permissions=True)
			
			self.export_file = file_doc.file_url
			self.export_status = "Exported"
			self.save()
			
			frappe.msgprint(_("SPT exported successfully"), indicator="green")
			
			return {
				"status": "success",
				"file_url": file_doc.file_url,
				"validation": validation
			}
			
		except Exception as e:
			frappe.log_error(f"Error exporting SPT: {str(e)}", "SPT Export Error")
			frappe.throw(_("Error exporting SPT: {0}").format(str(e)))
