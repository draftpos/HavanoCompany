# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def setup_company_role_permissions():
	"""
	Setup permissions for Company User Role with specific granular permissions
	"""
	try:
		# Create Company User Role if it doesn't exist
		if not frappe.db.exists("Role", "Company User Role"):
			role_doc = frappe.get_doc({
				"doctype": "Role",
				"role_name": "Company User Role",
				"desk_access": 1,
				"disabled": 0
			})
			role_doc.insert(ignore_permissions=True)
			frappe.logger().info("Created Company User Role")
		
		# Define specific permissions for Company User Role
		permissions = [
			# Item - modify only if creator
			{
				"doctype": "Item",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 0,
				"delete": 0,
				"if_owner": 1,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Product Bundle - add and modify
			{
				"doctype": "Product Bundle",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 1,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Item Price - add and modify
			{
				"doctype": "Item Price",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 1,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Stock Reconciliation (Stock Adjustment) - add and get
			{
				"doctype": "Stock Reconciliation",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 1,
				"amend": 1,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Stock Entry (Stock Transfer) - add and get list
			{
				"doctype": "Stock Entry",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 1,
				"amend": 1,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Purchase Invoice - create and list get
			{
				"doctype": "Purchase Invoice",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"submit": 1,
				"print": 1,
				"cancel": 1,
				"amend": 1,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Supplier - create
			{
				"doctype": "Supplier",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 1,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Sales Invoice - create
			{
				"doctype": "Sales Invoice",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"submit": 1,
				"print": 1,
				"cancel": 1,
				"amend": 1,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Customer - for customer balances
			{
				"doctype": "Customer",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 1,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Payment Entry - for payments entry
			{
				"doctype": "Payment Entry",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"submit": 1,
				"print": 1,
				"cancel": 1,
				"amend": 1,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Currency Exchange - for exchange rate (read only)
			{
				"doctype": "Currency Exchange",
				"role": "Company User Role",
				"read": 1,
				"write": 0,
				"create": 0,
				"delete": 0,
				"print": 0,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 0
			},
			# Item Group - get item group (read only)
			{
				"doctype": "Item Group",
				"role": "Company User Role",
				"read": 1,
				"write": 0,
				"create": 0,
				"delete": 0,
				"print": 0,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 0
			},
			# Warehouse - get warehouse (read only)
			{
				"doctype": "Warehouse",
				"role": "Company User Role",
				"read": 1,
				"write": 0,
				"create": 0,
				"delete": 0,
				"print": 0,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 0
			},
			# Cost Center - get cost center (read only)
			{
				"doctype": "Cost Center",
				"role": "Company User Role",
				"read": 1,
				"write": 0,
				"create": 0,
				"delete": 0,
				"print": 0,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 0
			},
			# Company Registration - for company management
			{
				"doctype": "Company Registration",
				"role": "Company User Role",
				"read": 1,
				"write": 1,
				"create": 1,
				"delete": 0,
				"print": 1,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 1
			},
			# Company - read access
			{
				"doctype": "Company",
				"role": "Company User Role",
				"read": 1,
				"write": 0,
				"create": 0,
				"delete": 0,
				"print": 0,
				"cancel": 0,
				"amend": 0,
				"import": 0,
				"export": 1,
				"report": 1,
				"select": 1,
				"share": 0
			}
		]
		
		# Add permissions to the role
		for perm in permissions:
			doctype = perm.pop("doctype")
			role = perm.pop("role")
			
			# Check if DocType exists
			if not frappe.db.exists("DocType", doctype):
				frappe.logger().warning(f"DocType {doctype} not found, skipping...")
				continue
			
			# Check if permission already exists
			existing_perm = frappe.db.exists("Custom DocPerm", {
				"parent": doctype,
				"role": role
			})
			
			if not existing_perm:
				# Add the permission
				try:
					custom_perm = frappe.get_doc({
						"doctype": "Custom DocPerm",
						"parent": doctype,
						"parenttype": "DocType",
						"parentfield": "permissions",
						"role": role,
						**perm
					})
					custom_perm.insert(ignore_permissions=True)
					frappe.logger().info(f"Added permission for {role} on {doctype}")
				except Exception as e:
					frappe.logger().warning(f"Could not add permission for {role} on {doctype}: {str(e)}")
		
		frappe.db.commit()
		frappe.logger().info("Company User Role permissions setup completed successfully")
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Company Role Setup Error", frappe.get_traceback())

def after_install():
	"""
	Called after app installation
	"""
	setup_company_role_permissions()
