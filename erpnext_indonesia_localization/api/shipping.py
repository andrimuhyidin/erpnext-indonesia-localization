import frappe
import requests
from frappe import _

@frappe.whitelist()
def get_shipping_rates(destination_city, weight, couriers=None):
	"""
	Fetch shipping rates from RajaOngkir.
	destination_city: ID or Name of city
	weight: Total weight in grams
	couriers: List of courier codes (jne, jnt, sicepat)
	"""
	settings = frappe.get_single("Indonesia Logistics Settings")
	if not settings.enabled:
		return []

	api_key = settings.get_password("rajaongkir_api_key")
	origin = settings.origin_city_id
	api_type = settings.api_type.lower() # starter, basic, pro

	url = f"https://api.rajaongkir.com/{api_type}/cost"
	
	if not couriers:
		couriers = [d.courier for d in settings.enabled_couriers if d.enabled]
	
	if isinstance(couriers, list):
		couriers = ",".join(couriers)

	headers = {
		'key': api_key,
		'content-type': "application/x-www-form-urlencoded"
	}

	payload = {
		"origin": origin,
		"destination": destination_city,
		"weight": weight,
		"courier": couriers
	}

	try:
		response = requests.post(url, data=payload, headers=headers)
		response.raise_for_status()
		data = response.json()
		
		results = []
		if data.get("rajaongkir", {}).get("status", {}).get("code") == 200:
			for courier_data in data["rajaongkir"]["results"]:
				for service in courier_data["costs"]:
					results.append({
						"courier": courier_data["code"].upper(),
						"service": service["service"],
						"description": service["description"],
						"cost": service["cost"][0]["value"],
						"etd": service["cost"][0]["etd"],
						"id": f"{courier_data['code']}_{service['service']}".lower()
					})
		return results
	except Exception as e:
		frappe.log_error(f"RajaOngkir API Error: {str(e)}", "Logistics Integration")
		return []

@frappe.whitelist()
def sync_cities():
	"""Sync City list from RajaOngkir and store in a cache or custom DocType"""
	settings = frappe.get_single("Indonesia Logistics Settings")
	api_key = settings.get_password("rajaongkir_api_key")
	api_type = settings.api_type.lower()

	url = f"https://api.rajaongkir.com/{api_type}/city"
	headers = {'key': api_key}

	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		data = response.json()
		if data.get("rajaongkir", {}).get("status", {}).get("code") == 200:
			cities = data["rajaongkir"]["results"]
			# Store in Cache for efficiency
			frappe.cache().set_value("rajaongkir_cities", cities, expires_in_sec=86400 * 7)
			return cities
	except Exception as e:
		frappe.throw(_("Failed to sync cities: {0}").format(str(e)))

@frappe.whitelist()
def apply_custom_shipping_charge(cost, description):
	"""
	Apply a custom shipping charge to the current cart's quotation.
	This creates a temporary Shipping Rule or updates the quotation charges.
	Requires webshop app to be installed.
	"""
	# Check if webshop is installed
	if "webshop" not in frappe.get_installed_apps():
		frappe.throw(_("Webshop app is required for shipping integration"))
	
	from webshop.webshop.shopping_cart.cart import _get_cart_quotation
	
	quotation = _get_cart_quotation()
	
	# Clear existing shipping rule if any
	quotation.shipping_rule = None
	
	# Add custom charge
	# We search for a 'Shipping' account in the company's taxes
	tax_account = frappe.db.get_value("Sales Taxes and Charges", {"account_head": ["like", "%Shipping%"]}, "account_head")
	if not tax_account:
		# Fallback to a general account or create a generic 'Shipping' charge
		tax_account = quotation.company # Likely to fail if not account
	
	# We'll use the description to identify the charge
	# For simplicity, we can append to 'taxes' table directly
	
	# Remove old logistics charges
	quotation.set("taxes", [d for d in quotation.taxes if d.description != "Indonesian Logistics"])
	
	quotation.append("taxes", {
		"charge_type": "Actual",
		"account_head": tax_account or "Shipping Charges",
		"description": "Indonesian Logistics",
		"tax_amount": cost,
		"rate": 0,
		"included_in_print_rate": 0
	})
	
	quotation.flags.ignore_permissions = True
	quotation.save()
	
	# Import here after webshop check above
	from webshop.webshop.shopping_cart.cart import get_cart_quotation
	return get_cart_quotation(quotation)
