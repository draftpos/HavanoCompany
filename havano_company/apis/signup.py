import frappe
from frappe import _
from frappe.utils import validate_email_address
import re
from havano_company.apis.utils import create_response


@frappe.whitelist(allow_guest=True)
def signup(email, password, first_name, last_name=None, full_name=None):
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
        
        if not first_name:
            frappe.throw(_("First name is required"))
        
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
            "user_type": "System User"  # Change to "Website User" if needed
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
                    "last_name": last_name
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
