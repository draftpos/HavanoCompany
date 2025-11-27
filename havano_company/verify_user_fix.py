# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe

def verify_user_doctype_fix():
	"""
	Verify that User doctype permissions are correctly configured
	"""
	print("\n" + "="*80)
	print("VERIFYING USER DOCTYPE FIX")
	print("="*80 + "\n")
	
	# 1. Check Custom DocPerm entries
	custom_perms = frappe.get_all("Custom DocPerm", 
		filters={"parent": "User"},
		fields=["name", "role", "permlevel"])
	
	print(f"1. Custom DocPerm entries for User: {len(custom_perms)}")
	if len(custom_perms) == 0:
		print("   ✓ PASS: No Custom DocPerm entries (should use standard permissions)")
	else:
		print("   ✗ FAIL: Found Custom DocPerm entries that may override standard permissions:")
		for perm in custom_perms:
			print(f"      - {perm['role']} (permlevel {perm['permlevel']})")
	
	# 2. Check standard DocPerm entries
	standard_perms = frappe.get_all("DocPerm",
		filters={"parent": "User"},
		fields=["role", "permlevel", "read", "write"],
		order_by="permlevel, role")
	
	print(f"\n2. Standard DocPerm entries: {len(standard_perms)}")
	permlevel_1_exists = False
	for perm in standard_perms:
		print(f"   - {perm['role']}: permlevel {perm['permlevel']}, read={perm['read']}, write={perm['write']}")
		if perm['permlevel'] == 1 and perm['role'] == 'System Manager':
			permlevel_1_exists = True
	
	if permlevel_1_exists:
		print("   ✓ PASS: Permlevel 1 permission exists for System Manager")
	else:
		print("   ✗ FAIL: Missing permlevel 1 permission for System Manager")
	
	# 3. Check roles field configuration
	roles_field = frappe.db.get_value("DocField",
		{"parent": "User", "fieldname": "roles"},
		["permlevel", "hidden", "read_only"], as_dict=True)
	
	print(f"\n3. Roles field configuration:")
	if roles_field:
		print(f"   - Permlevel: {roles_field['permlevel']}")
		print(f"   - Hidden: {roles_field['hidden']}")
		print(f"   - Read Only: {roles_field['read_only']}")
		
		if roles_field['permlevel'] == 1 and not roles_field['hidden']:
			print("   ✓ PASS: Roles field is at permlevel 1 and not hidden")
		else:
			print("   ✗ FAIL: Roles field configuration is incorrect")
	else:
		print("   ✗ FAIL: Roles field not found")
	
	# 4. Check enabled field configuration
	enabled_field = frappe.db.get_value("DocField",
		{"parent": "User", "fieldname": "enabled"},
		["permlevel", "hidden", "read_only"], as_dict=True)
	
	print(f"\n4. Enabled field configuration:")
	if enabled_field:
		print(f"   - Permlevel: {enabled_field['permlevel']}")
		print(f"   - Hidden: {enabled_field['hidden']}")
		print(f"   - Read Only: {enabled_field['read_only']}")
		
		if not enabled_field['read_only']:
			print("   ✓ PASS: Enabled field is not read-only")
		else:
			print("   ✗ FAIL: Enabled field is read-only")
	else:
		print("   ✗ FAIL: Enabled field not found")
	
	# Summary
	print("\n" + "="*80)
	if (len(custom_perms) == 0 and permlevel_1_exists and 
		roles_field and roles_field['permlevel'] == 1 and not roles_field['hidden'] and
		enabled_field and not enabled_field['read_only']):
		print("✓ ALL CHECKS PASSED - User doctype is correctly configured")
	else:
		print("✗ SOME CHECKS FAILED - Please review the issues above")
	print("="*80 + "\n")
	
	print("\nNOTE: After verifying the fix:")
	print("1. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
	print("2. Log out and log back in as System Manager")
	print("3. Navigate to User doctype and check if Roles field is visible")
	print()

if __name__ == "__main__":
	verify_user_doctype_fix()

