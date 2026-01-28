import frappe
from frappe import _

def validate_address_hierarchy(doc, method):
	"""
	Ensure Province and City align with Indonesian standards.
	If Country is Indonesia, validate against RajaOngkir data if available.
	"""
	if doc.country != "Indonesia":
		return

	if not doc.city and not doc.state:
		return

	# Try to validate against cached cities
	cities = frappe.cache().get_value("rajaongkir_cities")
	if not cities:
		from erpnext_indonesia_localization.api.shipping import sync_cities
		try:
			cities = sync_cities()
		except Exception:
			# If sync fails (e.g. no internet/API key), skip validation to avoid blocking user
			return

	if cities:
		# Check if city matches any in the list
		# City name in RajaOngkir is usually like "Jakarta Barat" or "Bandung"
		match = False
		for city in cities:
			if doc.city and doc.city.lower() == city.get("city_name").lower():
				# City matched, now check province
				if doc.state and doc.state.lower() != city.get("province").lower():
					frappe.msgprint(_("Warning: City '{0}' is usually in province '{1}', but you selected '{2}'.").format(
						doc.city, city.get("province"), doc.state
					))
				
				# Automatically set custom_rajaongkir_city_id if not set
				if not doc.custom_rajaongkir_city_id:
					doc.custom_rajaongkir_city_id = city.get("city_id")
				
				match = True
				break
		
		if not match and doc.city:
			frappe.msgprint(_("Notice: City '{0}' was not found in the official RajaOngkir list. Please ensure the spelling is correct for accurate shipping calculations.").format(doc.city))
