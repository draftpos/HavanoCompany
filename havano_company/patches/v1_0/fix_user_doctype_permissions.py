# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute():
	"""
	Patch to remove Custom DocPerm entries for User doctype that are causing
	roles field to be hidden and enabled field to be readonly.
	
	The issue: Custom DocPerm entries override standard permissions
	and only grant permlevel 0 access, while the roles field requires
	permlevel 1 access.
	"""
	try:
		# Get all Custom DocPerm entries for User doctype
		custom_perms = frappe.get_all("Custom DocPerm", 
			filters={"parent": "User"},
			fields=["name", "role", "permlevel"])
		
		if custom_perms:
			frappe.logger().info(f"Found {len(custom_perms)} Custom DocPerm entries for User doctype")
			
			# Delete each custom permission
			for perm in custom_perms:
				frappe.logger().info(f"Removing Custom DocPerm: {perm['name']} (Role: {perm['role']}, Permlevel: {perm['permlevel']})")
				frappe.delete_doc("Custom DocPerm", perm['name'], ignore_permissions=True, force=True)
			
			frappe.db.commit()
			frappe.clear_cache()
			
			frappe.logger().info(f"Successfully fixed User doctype permissions - removed {len(custom_perms)} custom entries")
		else:
			frappe.logger().info("No Custom DocPerm entries found for User doctype")
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Fix User Permissions Patch Error", frappe.get_traceback())
		raise

