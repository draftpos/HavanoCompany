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
	It creates a company, updates user type to System User, and assigns comprehensive roles for full ERPNext access
	"""
	try:
		# Get current user
		current_user = frappe.session.user
		if not current_user or current_user == "Guest":
			frappe.throw(_("You must be logged in to create a company"))
		
		# Get current user details
		user_doc = frappe.get_doc("User", current_user)
		
		# Use logged-in user's information instead of form data
		doc.full_name = user_doc.full_name or f"{user_doc.first_name or ''} {user_doc.last_name or ''}".strip() or user_doc.name
		doc.email = user_doc.email
		doc.phone = user_doc.phone or doc.phone  # Use form phone if provided, otherwise user's phone
		
		# Validate required fields
		if not doc.organization_name:
			frappe.throw(_("Organization Name is required"))
		
		# Clean and validate company name
		company_name = doc.organization_name.strip()
		if not company_name:
			frappe.throw(_("Organization Name cannot be empty"))
		
		frappe.logger().info(f"Processing company registration - Original name: '{doc.organization_name}', Cleaned: '{company_name}'")
		
		# Generate unique company name and abbreviation
		import datetime
		timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		original_company_name = company_name
		company_name = f"{original_company_name}_{timestamp}"
		company_abbr = f"{original_company_name[:3].upper()}{timestamp[-4:]}"
		
		frappe.logger().info(f"Generated unique company: '{company_name}' (abbr: '{company_abbr}')")
		
		
		# Create Company
		try:
			company_doc = frappe.get_doc({
				"doctype": "Company",
				"company_name": company_name,
				"default_currency": "USD",
				"country": doc.country or "United States",
				"enabled": 1,
				"abbr": company_abbr,
				"default_letter_head": None,
				"is_group": 0,
				"default_bank_account": None
			})
			company_doc.insert(ignore_permissions=True)
			frappe.logger().info(f"Company created successfully: {company_doc.name}")
		except Exception as e:
			frappe.logger().error(f"Error creating company: {str(e)}")
			frappe.throw(_("Failed to create company. Please try again."))
		
		# Commit the company creation
		frappe.db.commit()
		
		# Assign current user as System Manager and update user type
		try:
			# Update user type to System User
			frappe.db.set_value("User", current_user, "user_type", "System User")
			frappe.logger().info(f"Updated user {current_user} user_type to System User")
			
			# Define comprehensive roles for full ERPNext access
			roles_to_assign = [
				"System Manager",
				"Accounts Manager", 
				"Sales Manager",
				"Purchase Manager",
				"Stock Manager",
				"HR Manager",
				"Manufacturing Manager",
				"Projects Manager",
				"Support Team",
				"Website Manager",
				"Report Manager",
				"Blogger",
				"Knowledge Base User",
				"Helpdesk User",
				"Employee",
				"Employee Self Service"
			]
			
			# Assign all roles to the user
			assigned_roles = []
			for role in roles_to_assign:
				# Check if role exists
				if frappe.db.exists("Role", role):
					# Check if user already has this role
					has_role = frappe.db.exists("Has Role", {
						"parent": current_user,
						"role": role
					})
					
					if not has_role:
						# Assign role to current user
						frappe.get_doc({
							"doctype": "Has Role",
							"parent": current_user,
							"parenttype": "User",
							"parentfield": "roles",
							"role": role
						}).insert(ignore_permissions=True)
						assigned_roles.append(role)
						frappe.logger().info(f"Assigned {role} role to user {current_user}")
				else:
					frappe.logger().warning(f"Role {role} not found, skipping...")
			
			frappe.logger().info(f"Successfully assigned {len(assigned_roles)} roles to user {current_user}: {assigned_roles}")
			
			# Create user permission for the company
			create_user_permission_for_company(current_user, company_doc.name)
			# Create user permission for the user itself
			create_user_permission_for_user(current_user)
			
			frappe.db.commit()
			
		except Exception as e:
			frappe.log_error(f"Error updating user type and assigning roles: {str(e)}")
			frappe.throw(_("Failed to update user type and assign roles. Please try again or contact support."))
		
		# Update Company Registration document with company reference
		doc.company = company_doc.name
		doc.user_created = current_user
		doc.status = "Created"
		doc.save(ignore_permissions=True)
		
		# Final commit
		frappe.db.commit()
		
		# Send notification email
		# send_company_created_email(user_doc, company_doc)
		
		# Log successful registration
		# frappe.logger().info(f"Company registration successful: Company={company_doc.name}, User={current_user}")
		
		# Set success message
		frappe.msgprint(_("Company created successfully! Your user type has been updated to System User and you have been assigned comprehensive roles for full ERPNext access."), alert=True)
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Registration Error")
		frappe.throw(_("Registration failed. Please try again or contact support."))

def create_user_permission_for_company(user, company):
	"""Create user permission for the company"""
	try:
		# Check if user permission already exists
		existing_permission = frappe.db.exists("User Permission", {
			"user": user,
			"allow": "Company",
			"for_value": company
		})
		
		if not existing_permission:
			# Create user permission
			user_permission = frappe.get_doc({
				"doctype": "User Permission",
				"user": user,
				"allow": "Company",
				"for_value": company,
				"apply_to_all_doctypes": 1,
				'is_default': 1
			})
			user_permission.insert(ignore_permissions=True)
			frappe.db.commit()
			
			frappe.logger().info(f"User permission created for user {user} and company {company}")
		
	except Exception as e:
		frappe.log_error(f"Error creating user permission: {str(e)}")
		# Don't throw error to avoid blocking the process
		frappe.logger().error(f"Failed to create user permission for user {user} and company {company}: {str(e)}")

def create_user_permission_for_user(user):
	"""Create user permission for the user itself (allow=User, for_value=<user>)"""
	try:
		# Check if user permission already exists
		existing_permission = frappe.db.exists("User Permission", {
			"user": user,
			"allow": "User",
			"for_value": user
		})
		
		if not existing_permission:
			# Create user permission
			user_permission = frappe.get_doc({
				"doctype": "User Permission",
				"user": user,
				"allow": "User",
				"for_value": user,
				"apply_to_all_doctypes": 1
			})
			user_permission.insert(ignore_permissions=True)
			frappe.db.commit()
			
			frappe.logger().info(f"User self-permission created for user {user}")
	
	except Exception as e:
		frappe.log_error(f"Error creating self user permission: {str(e)}")
		# Don't throw error to avoid blocking the process
		frappe.logger().error(f"Failed to create self user permission for user {user}: {str(e)}")

def send_company_created_email(user_doc, company_doc):
	"""Send notification email about company creation"""
	try:
		
		subject = f"Company {company_doc.company_name} Created Successfully!"
		
		# Get site URL
		site_url = frappe.utils.get_url()
		
		message = f"""
		<html>
		<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
			<div style="max-width: 600px; margin: 0 auto; padding: 20px;">
				<h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
					Company Created Successfully!
				</h2>
				
				<p>Dear {user_doc.first_name or user_doc.name},</p>
				
				<p>Congratulations! Your company <strong>{company_doc.company_name}</strong> has been successfully created in Havano.</p>
				
				<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
					<h3 style="color: #2c3e50; margin-top: 0;">Company Details:</h3>
					<p><strong>Company Name:</strong> {company_doc.company_name}</p>
					<p><strong>Company Code:</strong> {company_doc.abbr}</p>
					<p><strong>Country:</strong> {company_doc.country or 'Not specified'}</p>
					<p><strong>Your User Type:</strong> System User</p>
					<p><strong>Your Roles:</strong> System Manager, Accounts Manager, Sales Manager, Purchase Manager, Stock Manager, HR Manager, Manufacturing Manager, Projects Manager, Support Team, Website Manager, Report Manager, Blogger, Knowledge Base User, Helpdesk User, Employee, Employee Self Service</p>
					<p><strong>Access URL:</strong> <a href="{site_url}/app/company" style="color: #3498db;">{site_url}/app/company</a></p>
				</div>
				
				<p>With your comprehensive roles, you now have full access to:</p>
				<ul>
					<li><strong>System Management:</strong> Complete system administration and user management</li>
					<li><strong>Accounting:</strong> Full access to accounting, invoicing, and financial reports</li>
					<li><strong>Sales & CRM:</strong> Manage customers, leads, opportunities, and sales processes</li>
					<li><strong>Purchase Management:</strong> Handle suppliers, purchase orders, and procurement</li>
					<li><strong>Inventory:</strong> Complete stock management and warehouse operations</li>
					<li><strong>Human Resources:</strong> Employee management, payroll, and HR processes</li>
					<li><strong>Manufacturing:</strong> Production planning, work orders, and manufacturing operations</li>
					<li><strong>Project Management:</strong> Project tracking, task management, and resource allocation</li>
					<li><strong>Support & Helpdesk:</strong> Customer support and ticket management</li>
					<li><strong>Website Management:</strong> Website content and e-commerce management</li>
					<li><strong>Reporting:</strong> Access to all reports and analytics</li>
					<li><strong>Knowledge Base:</strong> Documentation and knowledge management</li>
				</ul>
				
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
		frappe.logger().info(f"Company creation notification sent successfully to {user_doc.email} for company {company_doc.company_name}")
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Company Creation Email Error")
		# Don't throw error to avoid blocking the registration process
		frappe.logger().error(f"Failed to send company creation email to {user_doc.name}: {str(e)}")

def generate_unique_company_name(base_name):
	"""Generate a unique company name by adding a counter if needed"""
	company_name = base_name
	counter = 1
	
	while frappe.db.sql("""
		SELECT name FROM `tabCompany` 
		WHERE LOWER(company_name) = LOWER(%s)
	""", (company_name,)):
		company_name = f"{base_name} {counter}"
		counter += 1
		if counter > 999:  # Safety limit
			import datetime
			timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
			company_name = f"{base_name} {timestamp}"
			break
	
	return company_name

def generate_unique_company_abbr(base_name):
	"""Generate a unique company abbreviation"""
	base_abbr = base_name[:3].upper() if len(base_name) >= 3 else base_name.upper()
	company_abbr = base_abbr
	counter = 1
	
	while frappe.db.exists("Company", {"abbr": company_abbr}):
		company_abbr = f"{base_abbr}{counter:02d}"
		counter += 1
		if counter > 99:  # Safety limit
			import datetime
			timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
			company_abbr = f"{base_abbr}{timestamp[-4:]}"
			break
	
	return company_abbr
