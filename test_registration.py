#!/usr/bin/env python3
"""
Test script for Company Registration functionality
Run this script to test the registration process
"""

import frappe
from frappe import _

def test_company_registration():
	"""Test the company registration process"""
	
	# Test data
	test_data = {
		"full_name": "John Doe",
		"email": "john.doe@testcompany.com",
		"phone": "+1234567890",
		"industry": "Retail grocery",
		"organization_name": "Test Company Ltd",
		"country": "United States",
		"city": "New York",
		"username": "johndoe",
		"password": "testpass123",
		"confirm_password": "testpass123"
	}
	
	try:
		print("Testing Company Registration...")
		
		# Create Company Registration document
		doc = frappe.get_doc({
			"doctype": "Company Registration",
			**test_data
		})
		doc.insert()
		
		# Submit the document (this will trigger the on_submit function)
		doc.submit()
		
		print("✅ Company Registration successful!")
		print(f"Company: {doc.company}")
		print(f"User: {doc.user_created}")
		
		# Verify company was created
		company = frappe.get_doc("Company", doc.company)
		print(f"Company Name: {company.company_name}")
		print(f"Company Country: {company.country}")
		
		# Verify user was created
		user = frappe.get_doc("User", doc.user_created)
		print(f"User Email: {user.email}")
		print(f"User Company: {user.company}")
		
		# Check if user has the correct role
		user_roles = [role.role for role in user.roles]
		print(f"User Roles: {user_roles}")
		
		print("\n🎉 Test completed successfully!")
		
	except Exception as e:
		print(f"❌ Test failed: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Test Registration Error")

if __name__ == "__main__":
	# Initialize Frappe
	frappe.init(site="your-site-name")  # Replace with your site name
	frappe.connect()
	
	# Run the test
	test_company_registration()
	
	# Disconnect
	frappe.destroy()
