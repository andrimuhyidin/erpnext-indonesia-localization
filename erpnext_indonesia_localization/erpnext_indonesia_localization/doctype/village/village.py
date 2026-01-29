"""
Village DocType Controller.

Village (Kelurahan/Desa) master data for Indonesia.
Part of the Indonesian address hierarchy:
Province > Regency > District > Village
"""

import frappe
from frappe import _
from frappe.model.document import Document


class Village(Document):
	"""
	Village DocType for Indonesian administrative divisions.

	Represents the lowest level of administrative division:
	- Kelurahan (urban villages)
	- Desa (rural villages)
	"""

	def validate(self):
		"""Validate village data."""
		self.validate_district()
		self.validate_village_code()
		self.validate_village_name()
		self.set_postal_code_format()

	def validate_district(self):
		"""Validate district is specified."""
		if not self.district:
			frappe.throw(_("District is required for village"))

	def validate_village_code(self):
		"""Validate village code format."""
		if self.village_code:
			# Indonesian village codes are 10 digits (district code + 3 digits)
			code = str(self.village_code).strip()
			if not code.isdigit() or len(code) != 10:
				frappe.throw(_("Village code must be a 10-digit number"))

			# Validate prefix matches district code
			if self.district:
				district_code = frappe.db.get_value("District", self.district, "district_code")
				if district_code and not code.startswith(str(district_code)):
					frappe.msgprint(
						_("Village code prefix ({0}) doesn't match district code ({1})").format(
							code[:7], district_code
						),
						indicator="orange"
					)

	def validate_village_name(self):
		"""Validate village name is provided."""
		if not self.village_name:
			frappe.throw(_("Village Name is required"))

	def set_postal_code_format(self):
		"""Validate postal code format if provided."""
		if self.postal_code:
			# Indonesian postal codes are 5 digits
			code = str(self.postal_code).strip()
			if not code.isdigit() or len(code) != 5:
				frappe.msgprint(
					_("Postal code should be 5 digits"),
					indicator="orange"
				)

	def get_full_address_path(self):
		"""
		Get full address path: Province > Regency > District > Village

		Returns:
			str: Full address path
		"""
		district = frappe.get_doc("District", self.district)
		regency = frappe.get_doc("Regency", district.regency)
		province_name = frappe.db.get_value("Province", regency.province, "province_name")

		return f"{province_name}, {regency.regency_name}, {district.district_name}, {self.village_name}"

	def get_formatted_address(self):
		"""
		Get formatted address for display.

		Returns:
			str: Formatted address with postal code
		"""
		address = self.get_full_address_path()
		if self.postal_code:
			return f"{address} {self.postal_code}"
		return address

	@staticmethod
	def get_by_district(district_name):
		"""
		Get all villages for a district.

		Args:
			district_name: District document name

		Returns:
			list: Village records
		"""
		return frappe.get_all(
			"Village",
			filters={"district": district_name},
			fields=["name", "village_name", "village_code", "village_type", "postal_code"],
			order_by="village_name"
		)

	@staticmethod
	def search_by_postal_code(postal_code):
		"""
		Search villages by postal code.

		Args:
			postal_code: Postal code to search

		Returns:
			list: Matching village records
		"""
		return frappe.get_all(
			"Village",
			filters={"postal_code": postal_code},
			fields=["name", "village_name", "district", "village_code"]
		)
