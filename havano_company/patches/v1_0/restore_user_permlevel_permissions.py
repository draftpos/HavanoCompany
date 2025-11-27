# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute():
	"""
	Restore missing permlevel 1 permissions for User doctype.
	The roles field requires permlevel 1 access to be visible.
	"""
	try:
		# Check if permlevel 1 permission exists for System Manager
		existing_perm = frappe.db.exists("DocPerm", {
			"parent": "User",
			"role": "System Manager",
			"permlevel": 1
		})
		
		if not existing_perm:
			# Get the User DocType
			user_doctype = frappe.get_doc("DocType", "User")
			
			# Add permlevel 1 permission for System Manager
			user_doctype.append("permissions", {
				"role": "System Manager",
				"permlevel": 1,
				"read": 1,
				"write": 1,
				"create": 0,
				"delete": 0,
				"submit": 0,
				"cancel": 0,
				"amend": 0
			})
			
			# Save the doctype
			user_doctype.save(ignore_permissions=True)
			frappe.db.commit()
			frappe.clear_cache(doctype="User")
			
			frappe.logger().info("Successfully restored permlevel 1 permission for System Manager on User doctype")
			print("✓ Restored permlevel 1 permission for System Manager")
		else:
			frappe.logger().info("Permlevel 1 permission already exists for System Manager on User doctype")
			print("✓ Permlevel 1 permission already exists")
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Restore User Permlevel Permissions Error", frappe.get_traceback())
		print(f"✗ Error: {str(e)}")
		raise

