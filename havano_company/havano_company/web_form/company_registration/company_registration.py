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
		
		# Clean and validate username
		doc.username = doc.username.strip().lower()
		
		# Check if username already exists (case insensitive)
		existing_user = frappe.db.get_value("User", {"username": doc.username}, "name")
		if existing_user:
			frappe.throw(_("Username already exists. Please choose a different username."))
		
		# Check if email already exists
		existing_email = frappe.db.get_value("User", {"email": doc.email}, "name")
		if existing_email:
			frappe.throw(_("Email already exists. Please use a different email."))
		
		# Check if company name already exists
		if frappe.db.exists("Company", doc.organization_name):
			frappe.throw(_("Company with this name already exists. Please choose a different company name."))
		
		
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
		
		# Create User using direct database insertion to avoid hook issues
		try:
			# Create user data
			user_data = {
				"name": doc.username,
				"email": doc.email,
				"first_name": doc.full_name.split()[0] if doc.full_name else "",
				"last_name": " ".join(doc.full_name.split()[1:]) if len(doc.full_name.split()) > 1 else "",
				"username": doc.username,
				"enabled": 1,
				"user_type": "System User",
				"phone": doc.phone or "",
				"company": company_doc.name,
				"language": "en",
				"time_zone": "Africa/Harare",
				"creation": frappe.utils.now(),
				"modified": frappe.utils.now(),
				"owner": "Administrator",
				"modified_by": "Administrator"
			}
			
			# Insert user directly into database
			frappe.db.sql("""
				INSERT INTO `tabUser` 
				(name, email, first_name, last_name, username, enabled, user_type, 
				 phone, language, time_zone, creation, modified, owner, modified_by)
				VALUES (%(name)s, %(email)s, %(first_name)s, %(last_name)s, %(username)s, 
				        %(enabled)s, %(user_type)s, %(phone)s, 
				        %(language)s, %(time_zone)s, %(creation)s, %(modified)s, %(owner)s, %(modified_by)s)
			""", user_data)
			
			frappe.db.commit()
			
			# Set password using Frappe's password hashing
			from frappe.utils.password import update_password
			update_password(doc.username, doc.password)
			
			# Check if Company User Role exists, if not create it
			if not frappe.db.exists("Role", "Company User Role"):
				role_doc = frappe.get_doc({
					"doctype": "Role",
					"role_name": "Company User Role",
					"desk_access": 1
				})
				role_doc.insert(ignore_permissions=True)
				frappe.db.commit()
			
			# Assign Company User Role to the user
			frappe.get_doc({
				"doctype": "Has Role",
				"parent": doc.username,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Company User Role"
			}).insert(ignore_permissions=True)
			
			frappe.db.commit()
			
		except Exception as e:
			frappe.log_error(f"Error creating user: {str(e)}")
			frappe.throw(_("Failed to create user. Please try again or contact support."))
		
		# Update Company Registration document with company reference
		doc.company = company_doc.name
		doc.user_created = doc.username
		doc.save(ignore_permissions=True)
		
		# Final commit
		frappe.db.commit()
		
		# Send welcome email with login credentials
		send_welcome_email(doc.username, company_doc, doc.password)
		
		# Log successful registration
		frappe.logger().info(f"Company registration successful: Company={company_doc.name}, User={doc.username}, Email={doc.email}")
		
		# Set success message
		frappe.msgprint(_("Registration successful! Welcome email sent to {0}").format(doc.email), alert=True)
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Registration Error")
		frappe.throw(_("Registration failed. Please try again or contact support."))

def send_welcome_email(username, company_doc, password):
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
				
				<p>Dear User,</p>
				
				<p>Congratulations! Your company <strong>{company_doc.company_name}</strong> has been successfully registered with Havano.</p>
				
				<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
					<h3 style="color: #2c3e50; margin-top: 0;">Your Login Credentials:</h3>
					<p><strong>Username:</strong> {username}</p>
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
