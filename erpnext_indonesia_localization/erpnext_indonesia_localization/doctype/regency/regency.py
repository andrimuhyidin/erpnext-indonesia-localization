"""
Regency DocType Controller.

Regency (Kabupaten/Kota) master data for Indonesia.
Part of the Indonesian address hierarchy:
Province > Regency > District > Village
"""

import frappe
from frappe import _
from frappe.model.document import Document


class Regency(Document):
	"""
	Regency DocType for Indonesian administrative divisions.

	Represents cities (Kota) and regencies (Kabupaten) under provinces.
	"""

	def validate(self):
		"""Validate regency data."""
		self.validate_province()
		self.validate_regency_code()
		self.validate_regency_name()

	def validate_province(self):
		"""Validate province is specified."""
		if not self.province:
			frappe.throw(_("Province is required for regency"))

	def validate_regency_code(self):
		"""Validate regency code format."""
		if self.regency_code:
			# Indonesian regency codes are 4 digits (province code + 2 digits)
			code = str(self.regency_code).strip()
			if not code.isdigit() or len(code) != 4:
				frappe.throw(_("Regency code must be a 4-digit number"))

			# Validate prefix matches province code
			if self.province:
				province_code = frappe.db.get_value("Province", self.province, "province_code")
				if province_code and not code.startswith(str(province_code)):
					frappe.msgprint(
						_("Regency code prefix ({0}) doesn't match province code ({1})").format(
							code[:2], province_code
						),
						indicator="orange"
					)

	def validate_regency_name(self):
		"""Validate regency name is provided."""
		if not self.regency_name:
			frappe.throw(_("Regency Name is required"))

	def get_districts(self):
		"""
		Get all districts (kecamatan) in this regency.

		Returns:
			list: List of district records
		"""
		return frappe.get_all(
			"District",
			filters={"regency": self.name},
			fields=["name", "district_name", "district_code"],
			order_by="district_name"
		)

	def get_full_address_path(self):
		"""
		Get full address path: Province > Regency

		Returns:
			str: Full address path
		"""
		province_name = frappe.db.get_value("Province", self.province, "province_name")
		return f"{province_name}, {self.regency_name}"

	@staticmethod
	def get_by_province(province_name):
		"""
		Get all regencies for a province.

		Args:
			province_name: Province document name

		Returns:
			list: Regency records
		"""
		return frappe.get_all(
			"Regency",
			filters={"province": province_name},
			fields=["name", "regency_name", "regency_code", "regency_type"],
			order_by="regency_name"
		)
