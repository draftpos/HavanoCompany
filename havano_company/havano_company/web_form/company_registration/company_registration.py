import frappe
from frappe import _
from frappe.utils import now, cstr
import hashlib
import secrets

def get_context(context):
	# do your magic here
	pass


def on_submit(doc, method=None):
	"""
	This function will be called when the webform is submitted
	It creates a user and company based on the form data
	"""
	try:
		# Validate required fields
		if not doc.full_name:
			frappe.throw(_("Full Name is required"))
		if not doc.email:
			frappe.throw(_("Email is required"))
		if not doc.organization_name:
			frappe.throw(_("Organization Name is required"))
		if not doc.username:
			frappe.throw(_("Username is required"))
		if not doc.password:
			frappe.throw(_("Password is required"))
		
		# Validate password confirmation
		if doc.password != doc.confirm_password:
			frappe.throw(_("Password and Confirm Password do not match"))
		
		# Basic password validation
		if len(doc.password) < 6:
			frappe.throw(_("Password must be at least 6 characters long"))
		
		# Check if username already exists
		if frappe.db.exists("User", doc.username):
			frappe.throw(_("Username already exists. Please choose a different username."))
		
		# Check if email already exists
		if frappe.db.exists("User", doc.email):
			frappe.throw(_("Email already exists. Please use a different email."))
		
		# Check if company name already exists
		if frappe.db.exists("Company", doc.organization_name):
			frappe.throw(_("Company with this name already exists. Please choose a different company name."))
		
		# Check if company abbreviation already exists
		company_abbr = doc.organization_name[:3].upper() if len(doc.organization_name) >= 3 else doc.organization_name.upper()
		existing_company_with_abbr = frappe.db.get_value("Company", {"abbr": company_abbr}, "name")
		if existing_company_with_abbr:
			frappe.throw(_("Company abbreviation '{0}' is already used by '{1}'. Please choose a different company name.").format(company_abbr, existing_company_with_abbr))
		
		# Create Company
		company_doc = frappe.get_doc({
			"doctype": "Company",
			"company_name": doc.organization_name,
			"default_currency": "USD",
			"country": doc.country or "United States",
			"enabled": 1,
			"abbr": doc.organization_name[:3].upper() if len(doc.organization_name) >= 3 else doc.organization_name.upper(),
			"default_letter_head": None,
			"is_group": 0,
			"default_bank_account": None
		})
		company_doc.insert(ignore_permissions=True)
		
		# Commit the company creation
		frappe.db.commit()
		
		# Create User
		user_doc = frappe.get_doc({
			"doctype": "User",
			"email": doc.email,
			"first_name": doc.full_name.split()[0] if doc.full_name else "",
			"last_name": " ".join(doc.full_name.split()[1:]) if len(doc.full_name.split()) > 1 else "",
			"username": doc.username,
			"send_welcome_email": 0,
			"enabled": 1,
			"user_type": "Website User",
			"phone": doc.phone or "",
			"mobile_no": doc.phone or "",
			"company": company_doc.name,
			"language": "en",
			"time_zone": "Asia/Kolkata"
		})
		
		# Insert user first
		user_doc.insert(ignore_permissions=True)
		
		# Set password using Frappe's password hashing
		from frappe.utils.password import update_password
		update_password(user_doc.name, doc.password)
		
		# Commit the user creation
		frappe.db.commit()
		
		# Assign Company User Role to the user
		frappe.get_doc({
			"doctype": "Has Role",
			"parent": user_doc.name,
			"parenttype": "User",
			"parentfield": "roles",
			"role": "Company User Role"
		}).insert(ignore_permissions=True)
		
		# Set user's company
		user_doc.company = company_doc.name
		user_doc.save(ignore_permissions=True)
		
		# Update Company Registration document with company reference
		doc.company = company_doc.name
		doc.user_created = user_doc.name
		doc.save(ignore_permissions=True)
		
		# Final commit
		frappe.db.commit()
		
		# Send welcome email with login credentials
		send_welcome_email(user_doc, company_doc, doc.password)
		
		# Log successful registration
		frappe.logger().info(f"Company registration successful: Company={company_doc.name}, User={user_doc.name}, Email={doc.email}")
		
		# Set success message
		frappe.msgprint(_("Registration successful! Welcome email sent to {0}").format(doc.email), alert=True)
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Registration Error")
		frappe.throw(_("Registration failed. Please try again or contact support."))

def send_welcome_email(user_doc, company_doc, password):
	"""Send welcome email with login credentials"""
	try:
		subject = f"Welcome to Havano - Your {company_doc.company_name} Account is Ready!"
		
		# Get site URL
		site_url = frappe.utils.get_url()
		
		message = f"""
		<html>
		<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
			<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
				<h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
					Welcome to Havano!
				</h2>
				
				<p>Dear {user_doc.first_name},</p>
				
				<p>Congratulations! Your company <strong>{company_doc.company_name}</strong> has been successfully registered with Havano.</p>
				
				<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
					<h3 style="color: #2c3e50; margin-top: 0;">Your Login Credentials:</h3>
					<p><strong>Username:</strong> {user_doc.username}</p>
					<p><strong>Password:</strong> {password}</p>
					<p><strong>Company:</strong> {company_doc.company_name}</p>
					<p><strong>Login URL:</strong> <a href="{site_url}/login" style="color: #3498db;">{site_url}/login</a></p>
				</div>
				
				<p>You can now:</p>
				<ul>
					<li>Log in to your company dashboard</li>
					<li>Manage your company data</li>
					<li>Create and manage documents</li>
					<li>Invite team members</li>
				</ul>
				
				<p style="margin-top: 30px;">
					<strong>Important:</strong> Please keep your login credentials secure and do not share them with unauthorized persons.
				</p>
				
				<p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
				
				<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
					<p>Best regards,<br>
					<strong>The Havano Team</strong></p>
					<p>This is an automated message. Please do not reply to this email.</p>
				</div>
			</div>
		</body>
		</html>
		"""
		
		frappe.sendmail(
			recipients=[user_doc.email],
			subject=subject,
			message=message,
			now=True,
			delayed=False
		)
		
		# Log successful email sending
		frappe.logger().info(f"Welcome email sent successfully to {user_doc.email} for company {company_doc.company_name}")
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Welcome Email Error")
		# Don't throw error to avoid blocking the registration process
		frappe.logger().error(f"Failed to send welcome email to {user_doc.email}: {str(e)}")
