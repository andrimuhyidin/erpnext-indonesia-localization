# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

"""
Pajak.io API Helper Utilities
Centralized functions for authentication, error handling, and common API patterns
"""

import json
import requests
import frappe
import base64
import time
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from frappe import _
from typing import Dict, Any, Optional, Tuple

from erpnext_indonesia_localization.utils.exceptions import (
    PajakioAPIError,
    PajakioConnectionError,
    PajakioTimeoutError,
    PajakioAuthenticationError,
    MissingAPIKeyError,
    MissingURLConfigError,
)


def get_pajakio_headers() -> Dict[str, str]:
	"""
	Get standardized API headers with authentication.
	
	Returns:
		Dictionary with API headers including Authorization
		
	Raises:
		frappe.ValidationError: If API key is not configured
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
	except Exception as e:
		frappe.log_error(f"Error getting Indonesia Localization Settings: {str(e)}", "Pajak.io API Error")
		raise frappe.ValidationError(_("Failed to retrieve Indonesia Localization Settings. Please ensure the settings are configured."))
	
	try:
		api_key = indonesia_localization_settings.get_password('pajakio_api_key')
		if not api_key:
			raise ValueError("Pajak.io API Key is not set in Indonesia Localization Settings")
		
		# Validate API key format (should not be empty after trimming)
		api_key = api_key.strip()
		if not api_key:
			raise ValueError("Pajak.io API Key cannot be empty")
		
		key = bytes(api_key, 'utf-8')
		pajakio_api_key = base64.b64encode(key).decode('utf-8')
		
		return {
			"accept": "application/json",
			"content-type": "application/json",
			"Authorization": pajakio_api_key
		}
	except ValueError as e:
		frappe.log_error(f"Pajak.io API Key validation error: {str(e)}", "Pajak.io API Error")
		raise frappe.ValidationError(_("Pajak.io API Key is not configured. Please set it in Indonesia Localization Settings."))
	except Exception as e:
		frappe.log_error(f"Error getting Pajak.io API key: {str(e)}", "Pajak.io API Error")
		raise frappe.ValidationError(_("Failed to retrieve Pajak.io API Key. Please check Indonesia Localization Settings and ensure the API key is properly configured."))


def validate_api_response(response_data: Any, required_fields: Optional[list] = None) -> Tuple[bool, Optional[str]]:
	"""
	Validate API response structure.
	
	Args:
		response_data: Response data from API
		required_fields: List of required field names (optional)
		
	Returns:
		Tuple (is_valid, error_message)
	"""
	if not isinstance(response_data, dict):
		return False, "Invalid response format: expected dictionary"
	
	if 'code' not in response_data:
		return False, "Invalid response format: missing 'code' field"
	
	if required_fields:
		for field in required_fields:
			if field not in response_data:
				return False, f"Invalid response format: missing '{field}' field"
	
	return True, None


def handle_pajakio_error(error: Exception, context: str = "") -> str:
	"""
	Centralized error handling for Pajak.io API errors.
	
	Args:
		error: Exception object
		context: Additional context string for logging
		
	Returns:
		User-friendly error message
	"""
	error_context = f" {context}" if context else ""
	
	if isinstance(error, Timeout):
		frappe.log_error(f"Pajak.io API timeout{error_context}: {str(error)}", "Pajak.io API Timeout")
		return _("Request to Pajak.io API timed out. Please try again later.")
	
	elif isinstance(error, ConnectionError):
		frappe.log_error(f"Pajak.io API connection error{error_context}: {str(error)}", "Pajak.io API Connection Error")
		return _("Failed to connect to Pajak.io API. Please check your internet connection.")
	
	elif isinstance(error, HTTPError):
		try:
			error_detail = error.response.text if hasattr(error, 'response') else str(error)
			frappe.log_error(f"Pajak.io API HTTP error{error_context}: {error_detail}", "Pajak.io API HTTP Error")
			
			# Try to parse error message from response
			if hasattr(error, 'response') and error.response:
				try:
					error_data = error.response.json()
					if isinstance(error_data, dict) and 'message' in error_data:
						return _("Pajak.io API Error: {0}").format(error_data['message'])
				except (ValueError, json.JSONDecodeError, AttributeError):
					pass
			
			return _("HTTP error from Pajak.io API: {0}").format(str(error))
		except Exception as e:
			frappe.log_error(f"Error handling HTTPError: {str(e)}", "Pajak.io API Error Handler")
			return _("HTTP error from Pajak.io API")
	
	elif isinstance(error, RequestException):
		frappe.log_error(f"Pajak.io API request error{error_context}: {str(error)}", "Pajak.io API Request Error")
		return _("Error calling Pajak.io API: {0}").format(str(error))
	
	else:
		frappe.log_error(f"Unexpected Pajak.io API error{error_context}: {str(error)}", "Pajak.io API Unexpected Error")
		return _("Unexpected error: {0}").format(str(error))


def make_pajakio_request(
	method: str,
	url: str,
	headers: Optional[Dict[str, str]] = None,
	json_data: Optional[Dict[str, Any]] = None,
	params: Optional[Dict[str, Any]] = None,
	max_retries: int = 3,
	retry_delay: int = 2,
	timeout_seconds: int = 30,
	context: str = ""
) -> Dict[str, Any]:
	"""
	Generic request handler with retry logic for Pajak.io API.
	
	Args:
		method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
		url: API endpoint URL
		headers: Request headers (defaults to get_pajakio_headers())
		json_data: JSON payload for POST/PUT requests
		params: URL parameters for GET requests
		max_retries: Maximum number of retry attempts
		retry_delay: Delay between retries in seconds
		timeout_seconds: Request timeout in seconds
		context: Additional context for error logging
		
	Returns:
		Response data as dictionary
		
	Raises:
		frappe.ValidationError: If all retries fail
	"""
	if headers is None:
		headers = get_pajakio_headers()
	
	logger = frappe.logger("pajak_io", with_more_info=True, allow_site=True, file_count=10)
	
	for attempt in range(max_retries):
		try:
			# Make request based on method
			if method.upper() == 'GET':
				response = requests.get(url, headers=headers, params=params, timeout=timeout_seconds)
			elif method.upper() == 'POST':
				response = requests.post(url, headers=headers, json=json_data, timeout=timeout_seconds)
			elif method.upper() == 'PUT':
				response = requests.put(url, headers=headers, json=json_data, timeout=timeout_seconds)
			elif method.upper() == 'DELETE':
				response = requests.delete(url, headers=headers, params=params, timeout=timeout_seconds)
			else:
				raise ValueError(f"Unsupported HTTP method: {method}")
			
			response.raise_for_status()
			
			# Validate and parse response
			try:
				response_data = response.json()
				is_valid, error_msg = validate_api_response(response_data)
				
				if not is_valid:
					raise ValueError(error_msg or "Invalid response format")
				
				logger.debug(f"Pajak.io API Request{context} - Success: {response_data.get('code', 'N/A')}")
				return response_data
				
			except (ValueError, json.JSONDecodeError) as e:
				logger.error(f"Invalid response format{context}: {str(e)}")
				raise frappe.ValidationError(f"Invalid response from Pajak.io API: {str(e)}")
		
		except Timeout:
			if attempt < max_retries - 1:
				logger.warning(f"Request timeout{context}, retrying ({attempt + 1}/{max_retries})...")
				time.sleep(retry_delay)
				continue
			else:
				error_msg = handle_pajakio_error(Timeout("Request timeout"), context)
				raise frappe.ValidationError(error_msg)
		
		except ConnectionError as e:
			if attempt < max_retries - 1:
				logger.warning(f"Connection error{context}, retrying ({attempt + 1}/{max_retries}): {str(e)}")
				time.sleep(retry_delay)
				continue
			else:
				error_msg = handle_pajakio_error(e, context)
				raise frappe.ValidationError(error_msg)
		
		except HTTPError as e:
			# Don't retry on client errors (4xx), but retry on server errors (5xx)
			if 400 <= e.response.status_code < 500:
				error_msg = handle_pajakio_error(e, context)
				raise frappe.ValidationError(error_msg)
			elif attempt < max_retries - 1:
				logger.warning(f"HTTP error{context}, retrying ({attempt + 1}/{max_retries}): {e.response.status_code}")
				time.sleep(retry_delay)
				continue
			else:
				error_msg = handle_pajakio_error(e, context)
				raise frappe.ValidationError(error_msg)
		
		except RequestException as e:
			if attempt < max_retries - 1:
				logger.warning(f"Request error{context}, retrying ({attempt + 1}/{max_retries}): {str(e)}")
				time.sleep(retry_delay)
				continue
			else:
				error_msg = handle_pajakio_error(e, context)
				raise frappe.ValidationError(error_msg)
		
		except Exception as e:
			logger.error(f"Unexpected error{context}: {str(e)}")
			frappe.log_error(f"Unexpected error in make_pajakio_request{context}: {str(e)}", "Pajak.io API Error")
			raise
	
	# Should not reach here, but just in case
	raise frappe.ValidationError(_("Pajak.io API request failed after all retries."))


def get_pajakio_url(setting_field: str) -> str:
	"""
	Get Pajak.io API URL from Indonesia Localization Settings.
	
	Args:
		setting_field: Field name in Indonesia Localization Settings
		
	Returns:
		API URL string
		
	Raises:
		frappe.ValidationError: If URL is not configured or invalid
	"""
	try:
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
	except Exception as e:
		frappe.log_error(f"Error getting Indonesia Localization Settings: {str(e)}", "Pajak.io API Error")
		raise frappe.ValidationError(_("Failed to retrieve Indonesia Localization Settings. Please ensure the settings are configured."))
	
	url = getattr(indonesia_localization_settings, setting_field, None)
	
	if not url:
		raise frappe.ValidationError(_("Pajak.io API URL '{0}' is not configured in Indonesia Localization Settings. Please configure this URL to use Pajak.io API features.").format(setting_field))
	
	# Validate URL format
	url = url.strip()
	if not url:
		raise frappe.ValidationError(_("Pajak.io API URL '{0}' cannot be empty. Please configure it in Indonesia Localization Settings.").format(setting_field))
	
	# Basic URL format validation
	if not (url.startswith('http://') or url.startswith('https://')):
		frappe.log_error(f"Invalid URL format for {setting_field}: {url}", "Pajak.io API Error")
		raise frappe.ValidationError(_("Pajak.io API URL '{0}' has invalid format. URL must start with http:// or https://").format(setting_field))
	
	return url
