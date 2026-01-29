"""
Address Standardizer DocType

Address Standardizer utility for Indonesia addresses.
"""

from __future__ import annotations

import frappe
from frappe.model.document import Document


class AddressStandardizer(Document):
	"""
	Address Standardizer DocType controller.
	"""

	def validate(self) -> None:
		"""Auto-generate standardized address."""
		components: list[str] = []

		if self.village:
			village = frappe.get_doc("Village", self.village)
			if getattr(village, "village_name", None):
				components.append(village.village_name)
			if getattr(village, "postal_code", None):
				self.postal_code = village.postal_code

		if self.district:
			district = frappe.get_doc("District", self.district)
			if getattr(district, "district_name", None):
				components.append(f"Kec. {district.district_name}")

		if self.regency:
			regency = frappe.get_doc("Regency", self.regency)
			if getattr(regency, "regency_name", None):
				prefix = getattr(regency, "type", "") or ""
				prefix = f"{prefix} " if prefix else ""
				components.append(f"{prefix}{regency.regency_name}")

		if self.province:
			province = frappe.get_doc("Province", self.province)
			if getattr(province, "province_name", None):
				components.append(f"Prov. {province.province_name}")

		if components:
			self.standardized_address = ", ".join(components)


def auto_fill_indonesia_address(doc, method: str | None = None) -> None:
	"""Hook helper for Frappe ``Address`` DocType.

	If the Address has a ``village`` field (custom field) linked to the
	Indonesia Village master, this function will:

	- Auto-fill ``district``, ``regency``, ``province``, and ``postal_code``
	  fields on the Address document when they are empty.
	- Keep existing values if the user has already set them.

	This allows Address forms to behave similarly to the Address Standardizer
	utility, but inline on the core Address DocType.
	"""
	# Only apply for Indonesia-style addresses where custom fields exist.
	village_name = getattr(doc, "village", None)
	if not village_name:
		return

	fields = frappe.get_meta("Address").fields
	fieldnames = {f.fieldname for f in fields}

	# If these custom fields are not present on Address, do nothing.
	required_custom_fields = {"district", "regency", "province", "postal_code"}
	if not required_custom_fields.issubset(fieldnames):
		return

	village = frappe.get_doc("Village", village_name)

	# Expect Village doctype to have links up the hierarchy when available.
	if not getattr(doc, "district", None) and getattr(village, "district", None):
		doc.district = village.district
	if not getattr(doc, "regency", None) and getattr(village, "regency", None):
		doc.regency = village.regency
	if not getattr(doc, "province", None) and getattr(village, "province", None):
		doc.province = village.province
	if not getattr(doc, "postal_code", None) and getattr(village, "postal_code", None):
		doc.postal_code = village.postal_code
