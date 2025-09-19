# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def setup_company_role_permissions():
	"""
	Setup permissions for Company User Role
	"""
	try:
		# Create Company User Role if it doesn't exist
		if not frappe.db.exists("Role", "Company User Role"):
			role_doc = frappe.get_doc({
				"doctype": "Role",
				"role_name": "Company User Role",
				"desk_access": 1
			})
			role_doc.insert(ignore_permissions=True)
		
		# Set up basic permissions for Company User Role
		# These permissions will be restricted by company-based filtering
		doctypes_to_permit = [
			"Company Registration",
			"User",
			"Company",
			"Customer",
			"Supplier",
			"Item",
			"Sales Invoice",
			"Purchase Invoice",
			"Quotation",
			"Sales Order",
			"Purchase Order",
			"Stock Entry",
			"Delivery Note",
			"Purchase Receipt"
		]
		
		for doctype in doctypes_to_permit:
			if frappe.db.exists("DocType", doctype):
				# Check if permission already exists
				if not frappe.db.exists("Custom DocPerm", {
					"parent": doctype,
					"role": "Company User Role"
				}):
					perm_doc = frappe.get_doc({
						"doctype": "Custom DocPerm",
						"parent": doctype,
						"parenttype": "DocType",
						"parentfield": "permissions",
						"role": "Company User Role",
						"read": 1,
						"write": 1,
						"create": 1,
						"delete": 1,
						"submit": 1,
						"cancel": 1,
						"amend": 1,
						"report": 1,
						"export": 1,
						"import": 1,
						"share": 1,
						"print": 1,
						"email": 1
					})
					perm_doc.insert(ignore_permissions=True)
		
		frappe.db.commit()
		frappe.msgprint(_("Company User Role permissions setup completed successfully"))
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Role Setup Error")
		frappe.throw(_("Failed to setup company role permissions"))

def after_install():
	"""
	Called after app installation
	"""
	setup_company_role_permissions()
