# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def get_permission_query_conditions(user, doctype):
	"""
	Add company-based filtering to queries for company users
	"""
	if user in ["Administrator", "Guest"]:
		return ""
	
	try:
		user_doc = frappe.get_doc("User", user)
		if not user_doc.company:
			return "1=0"  # No access if user has no company
		
		# Check if doctype has company field
		meta = frappe.get_meta(doctype)
		company_fields = []
		
		for field in meta.fields:
			if field.fieldname in ['company', 'company_name', 'organization'] and field.fieldtype == 'Link':
				company_fields.append(field.fieldname)
		
		if company_fields:
			conditions = []
			for field in company_fields:
				conditions.append(f"{field} = '{user_doc.company}'")
			return " OR ".join(conditions)
		
		return ""
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Permission Query Error")
		return "1=0"

def has_permission(doc, user=None):
	"""
	Check if user has permission to access specific document
	"""
	if not user:
		user = frappe.session.user
	
	if user in ["Administrator", "Guest"]:
		return True
	
	try:
		user_doc = frappe.get_doc("User", user)
		if not user_doc.company:
			return False
		
		# Check if document belongs to user's company
		meta = frappe.get_meta(doc.doctype)
		company_fields = []
		
		for field in meta.fields:
			if field.fieldname in ['company', 'company_name', 'organization'] and field.fieldtype == 'Link':
				company_fields.append(field.fieldname)
		
		for field in company_fields:
			if hasattr(doc, field) and getattr(doc, field) == user_doc.company:
				return True
		
		return False
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Permission Check Error")
		return False