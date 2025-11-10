import frappe
from frappe import _
from frappe.utils import validate_email_address
import re
import random
from havano_company.apis.utils import create_response


@frappe.whitelist(allow_guest=True)
def signup(email, password, first_name, last_name=None, full_name=None,pin=None,phone_number=None):
    """
    API endpoint for user signup
    
    Args:
        email: User's email address
        password: User's password
        first_name: User's first name
        last_name: User's last name (optional)
        full_name: User's full name (optional, will be constructed from first_name and last_name if not provided)
    
    Returns:
        dict: Success message with user details
    """
    try:
        # Validate input parameters
        if not email:
            frappe.throw(_("Email is required"))
        
        if not password:
            frappe.throw(_("Password is required"))
        if not pin:
            frappe.throw(_("Pin is required"))
            
        if not first_name:
            frappe.throw(_("First name is required"))

        if not phone_number:
            frappe.throw(_("Phone number is required"))
        
        # Validate email format
        try:
            validate_email_address(email, throw=True)
        except Exception:
            frappe.throw(_("Please enter a valid email address"))
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            frappe.throw(_("User with this email already exists"))
        
        # Validate password strength
        validate_password(password)
        
        # Construct full name if not provided
        if not full_name:
            if last_name:
                full_name = f"{first_name} {last_name}"
            else:
                full_name = first_name
        # pin = random.randint(1000, 9999)

        
        # Create new user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name or "",
            "full_name": full_name,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email": 1,  # Set to 1 if you want to send welcome email
            "user_type": "System User",
            "pin":pin,
            "phone_number":phone_number
        })
        
        user.flags.ignore_permissions = True
        user.insert()
        
        # Add default role (customize based on your requirements)
        user.add_roles("Desk User")  # Change to appropriate role
        
        frappe.db.commit()
        
        create_response(
            status=200,
            message=_("User registered successfully"),
            data={
                "user": {
                    "email": email,
                    "full_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "pin":pin
                }
            }
        )
        return
    
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        create_response(
            status=400,
            message=str(e)
        )
        return


@frappe.whitelist(allow_guest=True)
def edit_user(email, first_name=None, last_name=None, full_name=None, password=None, pin=None,phone_number=None,user_status=None,role_select=None):
    """
    API endpoint to edit an existing user
    
    Args:
        email: User's email address (required to identify the user)
        first_name: New first name (optional)
        last_name: New last name (optional)
        full_name: New full name (optional, will be constructed if not provided)
        password: New password (optional)
        pin: New PIN (optional)
    
    Returns:
        dict: Success message with updated user details
    """
    try:
        if not email:
            frappe.throw(_("Email is required"))

        user = frappe.get_doc("User", email)
        if not user:
            frappe.throw(_("User not found"))

        # Update fields if provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if last_name:
            user.last_name = last_name
        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone_number = phone_number
        if user_status:
            user.user_status = user_status
        if role_select:
            user.role_select = role_select
        elif first_name or last_name:
            # Construct full_name if not provided
            user.full_name = f"{user.first_name} {user.last_name}".strip()

        if password:
            # Optionally validate password strength
            validate_password(password)
            user.new_password = password

        if pin:
            user.pin = pin

        user.flags.ignore_permissions = True
        user.save()
        frappe.db.commit()

        create_response(
            status=200,
            message=_("User updated successfully"),
            data={
                "user": {
                    "email": user.email,
                    "full_name": user.full_name,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "pin": getattr(user, "pin", None)
                }
            }
        )
        return

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Edit User Error")
        create_response(
            status=400,
            message=str(e)
        )
        return

@frappe.whitelist()
def get_users():
    """
    Returns a list of users that belong to the same company as the currently logged-in user.
    """
    try:
        # Ensure user is logged in
        if not frappe.session.user or frappe.session.user == "Guest":
            return {
                "status": 403,
                "message": _("Login required to fetch users"),
                "data": []
            }

        # Get current user's company from User Permission
        current_user_company = frappe.db.get_value(
            "User Permission",
            {"user": frappe.session.user, "allow": "Company"},
            "for_value"
        )

        if not current_user_company:
            return {
                "status": 404,
                "message": _("No company permission found for current user"),
                "data": []
            }

        # Get all users who have the same company in User Permissions
        users_with_same_company = frappe.get_all(
            "User Permission",
            filters={"allow": "Company", "for_value": current_user_company},
            fields=["user"]
        )

        user_names = [u.user for u in users_with_same_company if u.user]

        if not user_names:
            return {
                "status": 404,
                "message": _("No users found for this company"),
                "data": []
            }

        # Get user details
        users = frappe.get_all(
            "User",
            filters={"name": ["in", user_names]},
            fields=[
                "name", "email", "full_name", "first_name", "last_name",
                "phone_number", "enabled", "user_type","pin","role_select"
            ]
        )

        # Attach roles for each user====================================================
        for user in users:
            user_doc = frappe.get_doc("User", user["name"])
            user["roles"] = [role.role for role in user_doc.roles]

        return {
            "status": 200,
            "message": _("Users fetched successfully"),
            "company": current_user_company,
            "data": users
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Users Error")
        return {
            "status": 400,
            "message": str(e),
            "data": []
        }


def validate_password(password):
    """
    Validate password strength
    
    Args:
        password: Password to validate
    
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < 8:
        frappe.throw(_("Password must be at least 8 characters long"))
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        frappe.throw(_("Password must contain at least one uppercase letter"))
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        frappe.throw(_("Password must contain at least one lowercase letter"))
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        frappe.throw(_("Password must contain at least one number"))
    
    # Check for at least one special character (optional, comment out if not needed)
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     frappe.throw(_("Password must contain at least one special character"))


@frappe.whitelist(allow_guest=True)
def verify_email(email, verification_code):
    """
    API endpoint for email verification (optional)
    
    Args:
        email: User's email address
        verification_code: Verification code sent to email
    
    Returns:
        dict: Success message
    """
    try:
        # Implement your email verification logic here
        # This is a placeholder implementation
        
        user = frappe.get_doc("User", email)
        
        if not user:
            frappe.throw(_("User not found"))
        
        # Add your verification logic here
        # For example, check verification_code against stored code
        
        user.enabled = 1
        user.save(ignore_permissions=True)
        frappe.db.commit()
        
        create_response(
            status=200,
            message=_("Email verified successfully")
        )
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Email Verification Error")
        create_response(
            status=400,
            message=str(e)
        )
