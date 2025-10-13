import frappe
from frappe.utils import escape_html,cstr
from frappe.auth import LoginManager
from frappe import throw, msgprint, _
from frappe.utils.background_jobs import enqueue
import requests
import random
import json
import base64
from .utils import create_response, check_user_has_company
from tzlocal import get_localzone
import pytz

@frappe.whitelist(allow_guest=True)
def login(usr,pwd, timezone):

    local_tz = str(get_localzone())
    erpnext_tz = frappe.utils.get_system_timezone()

    if timezone != erpnext_tz:
        frappe.local.response.http_status_code = 400
        frappe.local.response["message"] = f"Timezone mismatch. Your timezone is {timezone}, but system requires {erpnext_tz}"
        return

    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr,pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response.http_status_code = 422
        frappe.local.response["message"] =  "Invalid Email or Password"
        return
    
    user = frappe.get_doc('User',frappe.session.user)

    # Get user permissions for warehouse and cost center
    warehouses = frappe.get_list("User Permission", 
        filters={
            "user": user.name,
            "allow": "Warehouse"
        },
        pluck="for_value",
        ignore_permissions=True
    )
    
    cost_centers = frappe.get_list("User Permission",
        filters={
            "user": user.name, 
            "allow": "Cost Center"
        },
        pluck="for_value",
        ignore_permissions=True
    )
    default_warehouse = frappe.db.get_value("User Permission", 
        {"user": user.name, "allow": "Warehouse", "is_default": 1}, "for_value")
    
    default_cost_center = frappe.db.get_value("User Permission",
        {"user": user.name, "allow": "Cost Center", "is_default": 1}, "for_value")

    default_customer = frappe.db.get_value("User Permission",
        {"user": user.name, "allow": "Customer", "is_default": 1}, "for_value") 

    # Get items and their quantities from default warehouse
    warehouse_items = []
    if default_warehouse:
        warehouse_items = frappe.db.sql("""
            SELECT 
                item.item_code,
                item.item_name,
                item.description,
                item.stock_uom,
                bin.actual_qty,
                bin.projected_qty
            FROM `tabItem` item
            LEFT JOIN `tabBin` bin ON bin.item_code = item.item_code 
            WHERE bin.warehouse = %s
        """, default_warehouse, as_dict=1)

    # Get customers with the same cost center as the default cost center
    customers = []
    if default_cost_center:
        customers = frappe.get_list("Customer",
            filters={
                "custom_cost_center": default_cost_center
            },
            fields=["name", "customer_name", "customer_group", "territory", "custom_cost_center"],
            ignore_permissions=True
        )

    # Get all docs created by or assigned to the user
    company_registration = frappe.db.sql("""
        SELECT name, organization_name, status, company, industry, country, city
        FROM `tabCompany Registration`
        WHERE user_created = %(user)s
        OR name IN (
            SELECT reference_name
            FROM `tabToDo`
            WHERE reference_type = 'Company Registration'
                AND allocated_to = %(user)s
        )
    """, {"user": usr}, as_dict=True)

    company_permission =frappe.db.get_all("User Permission",
        filters={
            "user": usr,
            "allow": "Company Registration",
        },
        fields=["name", "allow", "for_value"],
        ignore_permissions=True
    )

    # Check if user has company registration
    has_company = bool(company_registration)
    
    # Prepare company registration message if needed
    company_message = None
    if not has_company:
        company_message = "You need to register your company to access all features."
        
    frappe.response["user"] =   {
        "first_name": escape_html(user.first_name or ""),
        "last_name": escape_html(user.last_name or ""),
        "gender": escape_html(user.gender or "") or "",
        "birth_date": user.birth_date or "",       
        "mobile_no": user.mobile_no or "",
        "username":user.username or "",
        "full_name":user.full_name or "",
        "email":user.email or "",
        "warehouse": default_warehouse,
        "cost_center": default_cost_center,
        "default_customer": default_customer,
        "customers": customers,
        "warehouse_items": warehouse_items,
        "time_zone": f"{local_tz}{erpnext_tz}",
        "company" : company_registration[0].get("company") if company_registration else None,
        "has_company_registration": has_company,
        "company_registration": company_registration[0] if company_registration else None,
        "company_message": company_message
    }
    
    # Add help information if no company
    if not has_company:
        frappe.response["help"] = {
            "endpoint": "/api/method/havano_company.apis.company.register_company",
            "required_fields": ["user_email", "organization_name"],
            "message": "Please register your company to access all features",
            "example": {
                "user_email": user.email,
                "organization_name": "Your Company Name",
                "industry": "Retail grocery"
            }
        }
    
    return


@frappe.whitelist()
def verify_company_registration():
    """
    Endpoint to verify if current user has a company registration
    
    Returns:
        Response with company registration status and data
    """
    try:
        company_registration = check_user_has_company()
        
        create_response(
            status=200,
            message=_("User has a valid company registration"),
            data={
                "has_company_registration": True,
                "company_registration": company_registration
            }
        )
        return
        
    except frappe.ValidationError as e:
        create_response(
            status=403,
            message=str(e)
        )
        return
        
    except frappe.PermissionError as e:
        create_response(
            status=401,
            message=str(e)
        )
        return