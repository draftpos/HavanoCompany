import frappe
from frappe import _
from havano_company.apis.utils import create_response
import datetime
import time


@frappe.whitelist(allow_guest=True)
def register_company(organization_name, full_name=None, email=None, phone=None, industry=None, 
                     country=None, city=None, user_email=None):
    """
    API endpoint for company registration
    
    Args:
        organization_name: Organization/Company name (required)
        full_name: Contact person's full name (optional, defaults to current user's full name)
        email: Contact email (optional, defaults to current user's email)
        phone: Phone number (optional)
        industry: Industry type (optional) - Options: Retail grocery, Hardshop, Butchery, Ressturant, Bar, Other Retail, Other
        country: Country (optional)
        city: City (optional)
        user_email: User email for guest registration (required if guest)
    
    Returns:
        dict: Success message with company registration details
    """
    try:
        # Validate required parameters
        if not organization_name:
            frappe.throw(_("Organization name is required"))
        
        # Get current user
        user = frappe.session.user
        
        # Handle guest users (for initial company registration after signup)
        if user == "Guest":
            if not user_email:
                frappe.throw(_("User email is required for company registration"))
            
            # Validate user exists
            if not frappe.db.exists("User", user_email):
                frappe.throw(_("User not found. Please signup first."))
            
            user = user_email
        
        # Check if user already has a company registration
        existing_registration = frappe.db.exists("Company Registration", {"user_created": user})
        if existing_registration:
            frappe.throw(_("You already have a company registration"))
        
        # Get user details if not provided
        if not full_name or not email:
            user_doc = frappe.get_doc("User", user)
            if not full_name:
                full_name = user_doc.full_name
            if not email:
                email = user_doc.email
        
        # Validate industry options
        valid_industries = ["Retail grocery", "Hardshop", "Butchery", "Ressturant", "Bar", "Other Retail", "Other"]
        if industry and industry not in valid_industries:
            frappe.throw(_(f"Invalid industry. Must be one of: {', '.join(valid_industries)}"))
        
        # Create Company Registration document
        company_registration = frappe.get_doc({
            "doctype": "Company Registration",
            "organization_name": organization_name,
            # "company": organization_name,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "industry": industry,
            "country": country,
            "city": city,
            "status": "Created",
            "user_created": user
        })
        
        company_registration.insert(ignore_permissions=True)
        frappe.db.commit()

        submit_company_registration(company_registration)
        company_registration = frappe.get_doc("Company Registration", company_registration.name)
        company_registration.company = company_registration.organization_name
        company_registration.save(ignore_permissions=True)
        frappe.db.commit()

        warehouse = frappe.get_all(
            "Warehouse",
            filters={
                "company": organization_name,
                "warehouse_name": ["like", "Stores%"]
            },
            fields=["name"],
            limit=1
        )

        if warehouse:
            user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": user_email,
            "allow": "Warehouse",
            "for_value": warehouse,
            "apply_to_all_doctypes": 1,
            "is_default": 1 
            })
            user_permission.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            print("No warehouse found starting with 'Stores'")
        
        # ----------------------------------------------------------------------
        all_warehouse = frappe.get_all(
                "Warehouse",
                filters={"company": organization_name},
                fields=["name"]
            )

        for i in all_warehouse:
            try:
               
                if i["name"] != warehouse[0]['name']:
                    print(f"--------------name--------{i["name"]}")
                    print(f"-----------def warehouse-----------{warehouse[0]['name']}")
                    user_permission = frappe.get_doc({
                        "doctype": "User Permission",
                        "user": user_email,
                        "allow": "Warehouse",
                        "for_value": i["name"],
                        "apply_to_all_doctypes": 1,
                        "is_default": 0
                    })
                    user_permission.insert(ignore_permissions=True)
                    frappe.db.commit()
            except Exception as e:
                frappe.log_error(f"Error assigning warehouse permission: {str(e)}")
        # ----------------------------------------------------------------------

        def_customer=create_customer(f"cust-{organization_name}")
        
        try:
            user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": user_email,
            "allow": "Customer",
            "for_value": def_customer["customer_id"],
            "apply_to_all_doctypes": 1,
            "is_default": 1 
            })
            user_permission.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            return e

        try:
            cost_center=default_cost_center(organization_name)
            user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": user_email,
            "allow": "Cost Center",
            "for_value": cost_center,
            "apply_to_all_doctypes": 1,
            "is_default": 1 
            })
            user_permission.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            return e
    
   

                
        create_response(
            status=201,
            message=_("Company registered successfully"),
            data={
                "company_registration": {
                    "name": company_registration.name,
                    "organization_name": organization_name,
                    "full_name": full_name,
                    "email": email,
                    "user_created": user,
                    "defual_warehouse":warehouse,
                    "default_customer":def_customer
                }
            }
        )
        # -----------------------------------get warehouse
       


            
        return
    
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Company Registration Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return



@frappe.whitelist()
@frappe.whitelist()
def default_cost_center(company):
    """
    Returns the first Cost Center for a given company
    whose name starts with 'Main' (case-insensitive).
    """
    if not company:
        return None

    # Fetch all cost centers for this company
    cost_centers = frappe.get_all(
        "Cost Center",
        filters={"company": company},
        fields=["name"],
    )

    # Find the first one that starts with 'Main'
    for cc in cost_centers:
        cc_name = cc["name"]
        if cc_name.upper().startswith("MAIN"):
            print(f"-------------------Matched: {cc_name}")
            return cc_name

    return None

@frappe.whitelist()
def create_customer(
    customer_name,
):
    """
    Creates a Customer with extended custom fields and address info.
    """

    # --- Step 1: Check if customer exists ---
    if frappe.db.exists("Customer", {"customer_name": customer_name}):
        return {"message": f"Customer {customer_name} already exists"}

    # --- Step 2: Create the Customer ---
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_type": "Individual",
        "customer_group": "All Customer Groups",
        "territory": "All Territories",
        # Custom fields
        "custom_telephone_number": "000000000",
        "custom_email_address": "custom_email_address",
        "custom_customer_tin": "000000000",
        "custom_customer_vat": "000000000",
        "custom_trade_name": "custom_trade_name",
        "custom_customer_address": "custom_customer_address",
        "custom_street": "custom_street",
        "custom_house_no": "custom_house_no",
        "custom_city": "custom_city",
        "custom_province": "custom_province"
    })

    # --- Step 3: Insert the record ---
    customer.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message": "Customer created successfully",
        "customer_id": customer.name,
        "customer_name": customer.customer_name
    }

@frappe.whitelist()
def get_company_registration():
    """
    Get company registration for current user
    
    Returns:
        dict: Company registration details or None
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            frappe.throw(_("Please login to view company registration"))
        
        company_registration = frappe.get_all(
            "Company Registration",
            filters={"user_created": user},
            fields=["name", "organization_name", "full_name", "email", "phone", 
                   "industry", "country", "city", "status", "company", "creation", "modified"],
            ignore_permissions=True
        )
        
        if company_registration:
            create_response(
                status=200,
                message=_("Company registration retrieved successfully"),
                data={
                    "company_registration": company_registration[0]
                }
            )
            return
        else:
            create_response(
                status=404,
                message=_("No company registration found")
            )
            return
    
    except Exception as e:
        frappe.log_error("Get Company Registration Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist()
def update_company_registration(organization_name=None, full_name=None, email=None, phone=None, 
                                industry=None, country=None, city=None):
    """
    Update company registration for current user
    
    Args:
        organization_name: Organization/Company name (optional)
        full_name: Contact person's full name (optional)
        email: Contact email (optional)
        phone: Phone number (optional)
        industry: Industry type (optional) - Options: Retail grocery, Hardshop, Butchery, Ressturant, Bar, Other Retail, Other
        country: Country (optional)
        city: City (optional)
    
    Returns:
        dict: Success message with updated details
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            frappe.throw(_("Please login to update company registration"))
        
        # Find existing registration
        existing_registration = frappe.db.get_value("Company Registration", {"user_created": user}, "name")
        if not existing_registration:
            frappe.throw(_("No company registration found. Please register first."))
        
        # Get the document
        company_doc = frappe.get_doc("Company Registration", existing_registration)
        
        # Validate industry options if provided
        valid_industries = ["Retail grocery", "Hardshop", "Butchery", "Ressturant", "Bar", "Other Retail", "Other"]
        if industry and industry not in valid_industries:
            frappe.throw(_(f"Invalid industry. Must be one of: {', '.join(valid_industries)}"))
        
        # Update fields if provided
        if organization_name:
            company_doc.organization_name = organization_name
        if full_name:
            company_doc.full_name = full_name
        if email:
            company_doc.email = email
        if phone:
            company_doc.phone = phone
        if industry:
            company_doc.industry = industry
        if country:
            company_doc.country = country
        if city:
            company_doc.city = city
        
        company_doc.save(ignore_permissions=True)
        company_doc.submit()
        frappe.db.commit()
        
        create_response(
            status=200,
            message=_("Company registration updated successfully"),
            data={
                "company_registration": {
                    "name": company_doc.name,
                    "organization_name": company_doc.organization_name,
                    "full_name": company_doc.full_name,
                    "email": company_doc.email
                }
            }
        )
        return
    
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Update Company Registration Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist()
def delete_company_registration():
    """
    Delete company registration for current user
    
    Returns:
        dict: Success message
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            frappe.throw(_("Please login to delete company registration"))
        
        # Find existing registration
        existing_registration = frappe.db.get_value("Company Registration", {"user_created": user}, "name")
        if not existing_registration:
            frappe.throw(_("No company registration found"))
        
        # Delete the document
        frappe.delete_doc("Company Registration", existing_registration, ignore_permissions=True)
        frappe.db.commit()
        
        create_response(
            status=200,
            message=_("Company registration deleted successfully")
        )
    
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Delete Company Registration Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )


@frappe.whitelist()
def get_industry_options():
    """
    Get list of available industry options
    
    Returns:
        dict: List of industry options
    """
    try:
        industries = ["Retail grocery", "Hardshop", "Butchery", "Ressturant", "Bar", "Other Retail", "Other"]
        
        create_response(
            status=200,
            message=_("Industry options retrieved successfully"),
            data={
                "industries": industries
            }
        )
    
    except Exception as e:
        frappe.log_error("Get Industry Options Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )


@frappe.whitelist()
def assign_user_to_company(user_email, company_name=None):
    """
    Assign a user to a company
    
    Args:
        user_email: Email of the user to assign
        company_name: Company name (optional, defaults to current user's company)
    
    Returns:
        Response with assignment details
    """
    try:
        current_user = frappe.session.user
        if current_user == "Guest":
            frappe.throw(_("Please login to assign users"))
        
        # Validate user exists
        if not frappe.db.exists("User", user_email):
            frappe.throw(_("User not found"))
        
        # If company_name not provided, get current user's company
        if not company_name:
            company_registration = frappe.db.get_value(
                "Company Registration",
                {"user_created": current_user},
                ["company"],
                as_dict=True
            )
            
            if not company_registration or not company_registration.company:
                frappe.throw(_("You do not have a company to assign users to"))
            
            company_name = company_registration.company
        
        # Validate company exists
        if not frappe.db.exists("Company", company_name):
            frappe.throw(_("Company not found"))
        
        # Check if current user has permission to assign users (is owner or has System Manager role)
        is_company_owner = frappe.db.exists("Company Registration", {
            "user_created": current_user,
            "company": company_name
        })
        
        has_system_role = frappe.db.exists("Has Role", {
            "parent": current_user,
            "role": "System Manager"
        })
        
        if not is_company_owner and not has_system_role:
            frappe.throw(_("You do not have permission to assign users to this company"))
        
        # Check if user permission already exists
        existing_permission = frappe.db.exists("User Permission", {
            "user": user_email,
            "allow": "Company",
            "for_value": company_name
        })
        
        if existing_permission:
            create_response(
                status=200,
                message=_("User is already assigned to this company"),
                data={
                    "user": user_email,
                    "company": company_name,
                    "permission": existing_permission
                }
            )
            return
        
        # Create user permission
        user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": user_email,
            "allow": "Company",
            "for_value": company_name,
            "apply_to_all_doctypes": 1
        })
        user_permission.insert(ignore_permissions=True)
        frappe.db.commit()
        
        create_response(
            status=201,
            message=_("User assigned to company successfully"),
            data={
                "user": user_email,
                "company": company_name,
                "permission": user_permission.name
            }
        )
        return
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Assign User to Company Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist()
def remove_user_from_company(user_email, company_name=None):
    """
    Remove a user from a company
    
    Args:
        user_email: Email of the user to remove
        company_name: Company name (optional, defaults to current user's company)
    
    Returns:
        Response with removal confirmation
    """
    try:
        current_user = frappe.session.user
        if current_user == "Guest":
            frappe.throw(_("Please login to remove users"))
        
        # If company_name not provided, get current user's company
        if not company_name:
            company_registration = frappe.db.get_value(
                "Company Registration",
                {"user_created": current_user},
                ["company"],
                as_dict=True
            )
            
            if not company_registration or not company_registration.company:
                frappe.throw(_("You do not have a company"))
            
            company_name = company_registration.company
        
        # Check if current user has permission
        is_company_owner = frappe.db.exists("Company Registration", {
            "user_created": current_user,
            "company": company_name
        })
        
        has_system_role = frappe.db.exists("Has Role", {
            "parent": current_user,
            "role": "System Manager"
        })
        
        if not is_company_owner and not has_system_role:
            frappe.throw(_("You do not have permission to remove users from this company"))
        
        # Prevent removing the company owner
        is_owner = frappe.db.exists("Company Registration", {
            "user_created": user_email,
            "company": company_name
        })
        
        if is_owner:
            frappe.throw(_("Cannot remove company owner from the company"))
        
        # Find and delete user permission
        permission_name = frappe.db.get_value("User Permission", {
            "user": user_email,
            "allow": "Company",
            "for_value": company_name
        }, "name")
        
        if not permission_name:
            frappe.throw(_("User is not assigned to this company"))
        
        frappe.delete_doc("User Permission", permission_name, ignore_permissions=True)
        frappe.db.commit()
        
        create_response(
            status=200,
            message=_("User removed from company successfully"),
            data={
                "user": user_email,
                "company": company_name
            }
        )
        return
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Remove User from Company Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist()
def get_company_users(company_name=None):
    """
    Get all users assigned to a company
    
    Args:
        company_name: Company name (optional, defaults to current user's company)
    
    Returns:
        List of users assigned to the company
    """
    try:
        current_user = frappe.session.user
        if current_user == "Guest":
            frappe.throw(_("Please login to view company users"))
        
        # If company_name not provided, get current user's company
        if not company_name:
            company_registration = frappe.db.get_value(
                "Company Registration",
                {"user_created": current_user},
                ["company"],
                as_dict=True
            )
            
            if not company_registration or not company_registration.company:
                frappe.throw(_("You do not have a company"))
            
            company_name = company_registration.company
        
        # Check if current user has access to this company
        has_access = frappe.db.exists("User Permission", {
            "user": current_user,
            "allow": "Company",
            "for_value": company_name
        }) or frappe.db.exists("Has Role", {
            "parent": current_user,
            "role": "System Manager"
        })
        
        if not has_access:
            frappe.throw(_("You do not have access to this company"))
        
        # Get all users assigned to the company
        user_permissions = frappe.get_all(
            "User Permission",
            filters={
                "allow": "Company",
                "for_value": company_name
            },
            fields=["user", "name", "creation", "is_default"],
            ignore_permissions=True
        )
        
        # Get user details
        users = []
        for perm in user_permissions:
            user_doc = frappe.get_doc("User", perm.user)
            users.append({
                "email": user_doc.email,
                "full_name": user_doc.full_name,
                "username": user_doc.username,
                "enabled": user_doc.enabled,
                "user_type": user_doc.user_type,
                "permission_name": perm.name,
                "is_default": perm.is_default,
                "assigned_on": perm.creation
            })
        
        # Check if there's a company owner
        owner = frappe.db.get_value("Company Registration", {
            "company": company_name
        }, ["user_created", "full_name", "email"], as_dict=True)
        
        create_response(
            status=200,
            message=_("Company users retrieved successfully"),
            data={
                "company": company_name,
                "owner": owner,
                "users": users,
                "total_users": len(users)
            }
        )
        return
        
    except Exception as e:
        frappe.log_error("Get Company Users Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist()
def get_user_companies(user_email=None):
    """
    Get all companies a user is assigned to
    
    Args:
        user_email: Email of the user (optional, defaults to current user)
    
    Returns:
        List of companies the user is assigned to
    """
    try:
        current_user = frappe.session.user
        if current_user == "Guest":
            frappe.throw(_("Please login to view companies"))
        
        # If user_email not provided, use current user
        if not user_email:
            user_email = current_user
        
        # Only allow users to view their own companies unless they're System Manager
        if user_email != current_user:
            has_system_role = frappe.db.exists("Has Role", {
                "parent": current_user,
                "role": "System Manager"
            })
            
            if not has_system_role:
                frappe.throw(_("You can only view your own company assignments"))
        
        # Get all company permissions for the user
        company_permissions = frappe.get_all(
            "User Permission",
            filters={
                "user": user_email,
                "allow": "Company"
            },
            fields=["for_value", "name", "creation", "is_default", "apply_to_all_doctypes"],
            ignore_permissions=True
        )
        
        # Get company details
        companies = []
        for perm in company_permissions:
            if frappe.db.exists("Company", perm.for_value):
                company = frappe.db.get_value("Company", perm.for_value, 
                                             ["name", "company_name", "country", "abbr"], 
                                             as_dict=True)
                companies.append({
                    "company": company.name,
                    "company_name": company.company_name,
                    "country": company.country,
                    "abbr": company.abbr,
                    "permission_name": perm.name,
                    "is_default": perm.is_default,
                    "assigned_on": perm.creation
                })
        
        # Check if user owns any companies
        owned_companies = frappe.get_all(
            "Company Registration",
            filters={"user_created": user_email},
            fields=["company", "organization_name", "status"],
            ignore_permissions=True
        )
        
        create_response(
            status=200,
            message=_("User companies retrieved successfully"),
            data={
                "user": user_email,
                "companies": companies,
                "owned_companies": owned_companies,
                "total_companies": len(companies)
            }
        )
        return
        
    except Exception as e:
        frappe.log_error("Get User Companies Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )
        return


def submit_company_registration(company_registration):
    """
    Submit company registration
    
    Args:
        company_registration: Company registration document
        method: Method name
    """
    try:
        company_abbr = company_registration.organization_name[:3].upper() + company_registration.user_created[:3] + str(time.time())[-4:]
        create_company(company_registration.organization_name, company_registration.country, company_abbr)
        create_user_permission_for_company(company_registration.user_created, company_registration.organization_name)

        create_response(
            status=200,
            message=_("Company registration submitted successfully")
        )
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Submit Company Registration Error", frappe.get_traceback())
        create_response(
            status=400,
            message=str(e)
        )

def create_user_permission_for_company(user, company):
	"""Create user permission for the company"""
	try:
		# Create Company User Role if it doesn't exist
		if not frappe.db.exists("Role", "Company User Role"):
			company_user_role = frappe.get_doc({
				"doctype": "Role",
				"role_name": "Company User Role",
				"desk_access": 1,
				"disabled": 0
			})
			company_user_role.insert(ignore_permissions=True)
		
		# Update user type to System User
		frappe.db.set_value("User", user, "user_type", "System User")

		# Define comprehensive roles for full ERPNext access
		roles_to_assign = [
			"Company User Role",
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
					"parent": user,
					"role": role
				})
				
				if not has_role:
					# Assign role to user
					frappe.get_doc({
						"doctype": "Has Role",
						"parent": user,
						"parenttype": "User",
						"parentfield": "roles",
						"role": role
					}).insert(ignore_permissions=True)
					assigned_roles.append(role)
					frappe.logger().info(f"Assigned {role} role to user {user}")
			else:
				frappe.logger().warning(f"Role {role} not found, skipping...")
		
		frappe.logger().info(f"Successfully assigned {len(assigned_roles)} roles to user {user}: {assigned_roles}")
		
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
		frappe.log_error("Error creating user permission", f"Failed to create user permission for user {user} and company {company}: {str(e)}\n\n{frappe.get_traceback()}")
		# Don't throw error to avoid blocking the process

def create_company(company_name, country, company_abbr):
    """
    Create a company with retry logic for database deadlocks
    
    Args:
        company_name: Name of the company
        country: Country of the company
        company_abbr: Company abbreviation
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            company_doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": company_name,
                "default_currency": "USD",
                "country": country or "United States",
                "enabled": 1,
                "abbr": company_abbr,
                "default_letter_head": None,
                "is_group": 0,
                "default_bank_account": None
            })
            company_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(f"Company created successfully: {company_doc.name}")
            return company_doc
            
        except frappe.QueryDeadlockError as e:
            # Rollback the transaction
            frappe.db.rollback()
            
            if attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                wait_time = retry_delay * (2 ** attempt)
                frappe.logger().warning(
                    f"Database deadlock detected while creating company '{company_name}'. "
                    f"Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                # Max retries reached
                frappe.log_error(
                    "Company Creation Failed - Deadlock",
                    f"Failed to create company '{company_name}' after {max_retries} attempts due to deadlock\n\n{frappe.get_traceback()}"
                )
                frappe.throw(_("Failed to create company due to database deadlock. Please try again in a moment."))
                
        except Exception as e:
            # For non-deadlock errors, rollback and throw immediately
            frappe.db.rollback()
            frappe.log_error("Company Creation Error", f"Error creating company '{company_name}': {str(e)}\n\n{frappe.get_traceback()}")
            frappe.throw(_("Failed to create company. Please try again."))