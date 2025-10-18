import frappe
from frappe import _
from havano_company.apis.company import register_company

def get_context(context):
	# do your magic here
	pass


def on_submit(doc, method=None):
	"""
	This function will be called when the webform is submitted.
	It calls the register_company API to handle all company registration logic.
	"""
	try:
		# Get current user
		current_user = frappe.session.user
		if not current_user or current_user == "Guest":
			frappe.throw(_("You must be logged in to create a company"))
		
		# Validate required fields
		if not doc.organization_name:
			frappe.throw(_("Organization Name is required"))
		
		# Get current user details
		user_doc = frappe.get_doc("User", current_user)
		
		# Use logged-in user's information
		full_name = user_doc.full_name or f"{user_doc.first_name or ''} {user_doc.last_name or ''}".strip() or user_doc.name
		email = user_doc.email
		phone = user_doc.phone or doc.phone
		
		# Call the register_company API with user_email parameter
		register_company(
			organization_name=doc.organization_name,
			full_name=full_name,
			email=email,
			phone=phone,
			industry=doc.industry,
			country=doc.country,
			city=doc.city,
			user_email=current_user
		)
		
		# Update Company Registration document
		doc.user_created = current_user
		doc.status = "Created"
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		
		# Set success message
		frappe.msgprint(_("Company registered successfully!"), alert=True)
		
	except Exception as e:
		frappe.log_error("Company Registration Webform Error", frappe.get_traceback())
		frappe.throw(_("Registration failed. Please try again or contact support."))
