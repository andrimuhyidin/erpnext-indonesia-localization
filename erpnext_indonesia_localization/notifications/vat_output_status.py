# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
	"""Get context for VAT Output status notification"""
	return context


@frappe.whitelist()
def send_vat_output_status_notification(vom_name, status, message=None):
	"""
	Send notification when VAT Output Metadata status changes
	"""
	try:
		vom_doc = frappe.get_doc("VAT Output Metadata", vom_name)
		
		# Get users who should be notified
		users = get_users_to_notify()
		
		for user in users:
			# Create notification
			notification = frappe.get_doc({
				"doctype": "Notification Log",
				"for_user": user,
				"type": "Alert",
				"document_type": "VAT Output Metadata",
				"document_name": vom_name,
				"subject": f"VAT Output Status Changed: {status}",
				"email_content": message or f"VAT Output Metadata {vom_name} status changed to {status}",
			})
			notification.insert(ignore_permissions=True)
		
		# Send email if configured
		if frappe.db.get_single_value("Indonesia Localization Settings", "send_email_notifications"):
			send_email_notification(vom_doc, status, message)
			
	except Exception as e:
		frappe.log_error(f"Error sending VAT Output status notification: {str(e)}", "Notification Error")


def get_users_to_notify():
	"""Get list of users who should receive notifications"""
	# Get users with Accounts Manager or System Manager role
	users = frappe.get_all(
		"Has Role",
		filters={
			"role": ["in", ["Accounts Manager", "System Manager"]]
		},
		fields=["parent"],
		pluck="parent"
	)
	return list(set(users))  # Remove duplicates


def send_email_notification(vom_doc, status, message=None):
	"""Send email notification for VAT Output status change"""
	try:
		recipients = get_users_to_notify()
		
		if not recipients:
			return
		
		subject = f"VAT Output Status Changed: {status} - {vom_doc.name}"
		content = f"""
		<p>VAT Output Metadata {vom_doc.name} status has changed to <strong>{status}</strong>.</p>
		<p>Invoice: {vom_doc.noinvoice}</p>
		{message if message else ''}
		<p><a href="/app/vat-output-metadata/{vom_doc.name}">View VAT Output Metadata</a></p>
		"""
		
		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			message=content
		)
	except Exception as e:
		frappe.log_error(f"Error sending email notification: {str(e)}", "Email Notification Error")


def notify_on_vat_output_approval(doc, method):
	"""Hook to notify when VAT Output is approved"""
	if doc.status == "Approved" and doc.has_value_changed("status"):
		send_vat_output_status_notification(
			doc.name,
			"Approved",
			f"VAT Output Metadata {doc.name} has been approved. NOFA: {doc.nofa}"
		)


def notify_on_vat_output_rejection(doc, method):
	"""Hook to notify when VAT Output is rejected"""
	if doc.status == "Rejected" and doc.has_value_changed("status"):
		send_vat_output_status_notification(
			doc.name,
			"Rejected",
			f"VAT Output Metadata {doc.name} has been rejected."
		)
