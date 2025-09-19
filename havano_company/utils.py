# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def set_company_field(doc, method=None):
	"""
	Automatically set company field for new documents created by company users
	This ensures all documents created by a company user belong to their company
	"""
	try:
		# Skip if user is System Manager or Administrator
		if frappe.session.user in ["Administrator", "Guest"]:
			return
		
		# Skip if document already has company field set
		if hasattr(doc, 'company') and doc.company:
			return
		
		# Get current user's company
		user_doc = frappe.get_doc("User", frappe.session.user)
		if user_doc.company:
			# Set company field if it exists in the doctype
			if hasattr(doc, 'company'):
				doc.company = user_doc.company
			elif hasattr(doc, 'company_name'):
				doc.company_name = user_doc.company
			elif hasattr(doc, 'organization'):
				doc.organization = user_doc.company
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Field Auto-Population Error")

def get_company_filter():
	"""
	Return company filter for queries to restrict data to user's company
	"""
	try:
		if frappe.session.user in ["Administrator", "Guest"]:
			return ""
		
		user_doc = frappe.get_doc("User", frappe.session.user)
		if user_doc.company:
			return f"company = '{user_doc.company}'"
		
		return ""
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Filter Error")
		return ""

def has_company_permission(doc, user=None):
	"""
	Check if user has permission to access document based on company
	"""
	try:
		if not user:
			user = frappe.session.user
		
		if user in ["Administrator", "Guest"]:
			return True
		
		user_doc = frappe.get_doc("User", user)
		if not user_doc.company:
			return False
		
		# Check if document belongs to user's company
		if hasattr(doc, 'company') and doc.company == user_doc.company:
			return True
		elif hasattr(doc, 'company_name') and doc.company_name == user_doc.company:
			return True
		elif hasattr(doc, 'organization') and doc.organization == user_doc.company:
			return True
		
		return False
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Permission Check Error")
		return False
