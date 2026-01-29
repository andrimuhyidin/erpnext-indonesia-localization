"""
District DocType Controller.

District (Kecamatan) master data for Indonesia.
Part of the Indonesian address hierarchy:
Province > Regency > District > Village
"""

import frappe
from frappe import _
from frappe.model.document import Document


class District(Document):
	"""
	District DocType for Indonesian administrative divisions.

	Represents sub-districts (Kecamatan) under regencies/cities.
	"""

	def validate(self):
		"""Validate district data."""
		self.validate_regency()
		self.validate_district_code()
		self.validate_district_name()

	def validate_regency(self):
		"""Validate regency is specified."""
		if not self.regency:
			frappe.throw(_("Regency is required for district"))

	def validate_district_code(self):
		"""Validate district code format."""
		if self.district_code:
			# Indonesian district codes are 7 digits (regency code + 3 digits)
			code = str(self.district_code).strip()
			if not code.isdigit() or len(code) != 7:
				frappe.throw(_("District code must be a 7-digit number"))

			# Validate prefix matches regency code
			if self.regency:
				regency_code = frappe.db.get_value("Regency", self.regency, "regency_code")
				if regency_code and not code.startswith(str(regency_code)):
					frappe.msgprint(
						_("District code prefix ({0}) doesn't match regency code ({1})").format(
							code[:4], regency_code
						),
						indicator="orange"
					)

	def validate_district_name(self):
		"""Validate district name is provided."""
		if not self.district_name:
			frappe.throw(_("District Name is required"))

	def get_villages(self):
		"""
		Get all villages (kelurahan/desa) in this district.

		Returns:
			list: List of village records
		"""
		return frappe.get_all(
			"Village",
			filters={"district": self.name},
			fields=["name", "village_name", "village_code", "village_type"],
			order_by="village_name"
		)

	def get_full_address_path(self):
		"""
		Get full address path: Province > Regency > District

		Returns:
			str: Full address path
		"""
		regency = frappe.get_doc("Regency", self.regency)
		province_name = frappe.db.get_value("Province", regency.province, "province_name")
		return f"{province_name}, {regency.regency_name}, {self.district_name}"

	@staticmethod
	def get_by_regency(regency_name):
		"""
		Get all districts for a regency.

		Args:
			regency_name: Regency document name

		Returns:
			list: District records
		"""
		return frappe.get_all(
			"District",
			filters={"regency": regency_name},
			fields=["name", "district_name", "district_code"],
			order_by="district_name"
		)
