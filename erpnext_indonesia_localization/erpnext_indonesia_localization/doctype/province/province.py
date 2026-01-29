"""
Province DocType Controller.

Province (Provinsi) master data for Indonesia.
Part of the Indonesian address hierarchy:
Province > Regency > District > Village
"""

import frappe
from frappe import _
from frappe.model.document import Document


class Province(Document):
	"""
	Province DocType for Indonesian administrative divisions.

	Represents the top level of Indonesian address hierarchy.
	Indonesia has 38 provinces (as of 2024).
	"""

	def validate(self):
		"""Validate province data."""
		self.validate_province_code()
		self.validate_province_name()

	def validate_province_code(self):
		"""Validate province code format."""
		if self.province_code:
			# Indonesian province codes are 2 digits
			code = str(self.province_code).strip()
			if not code.isdigit() or len(code) != 2:
				frappe.throw(_("Province code must be a 2-digit number (e.g., 31 for DKI Jakarta)"))

	def validate_province_name(self):
		"""Validate province name is provided."""
		if not self.province_name:
			frappe.throw(_("Province Name is required"))

	def get_regencies(self):
		"""
		Get all regencies (kabupaten/kota) in this province.

		Returns:
			list: List of regency records
		"""
		return frappe.get_all(
			"Regency",
			filters={"province": self.name},
			fields=["name", "regency_name", "regency_code", "regency_type"],
			order_by="regency_name"
		)

	def get_regency_count(self):
		"""
		Get count of regencies in this province.

		Returns:
			int: Number of regencies
		"""
		return frappe.db.count("Regency", {"province": self.name})

	@staticmethod
	def get_all_provinces():
		"""
		Get all provinces ordered by name.

		Returns:
			list: All province records
		"""
		return frappe.get_all(
			"Province",
			fields=["name", "province_name", "province_code"],
			order_by="province_name"
		)
