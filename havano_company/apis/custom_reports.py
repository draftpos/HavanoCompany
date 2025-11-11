import frappe
from frappe.utils import cint
from frappe.utils import flt
import json

@frappe.whitelist(allow_guest=True)
def get_sales_invoice_report():
    """
    Returns a summary of Sales Invoices with optional filters.
    Expects JSON payload with:
    {
        "created_by": "user@example.com",
        "from_date": "2025-01-01",
        "to_date": "2025-01-31",
        "company": "Saas Company (Demo)"
    }
    """

    try:
        data = json.loads(frappe.request.data)  # Parse JSON payload
    except Exception:
        return {"status": "error", "message": "Invalid JSON payload"}

    created_by = data.get("created_by")
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    company = data.get("company")

    if not company:
        return {"status": "error", "message": "company is required"}

    filters = {}

    if created_by:
        filters["owner"] = created_by
    if from_date and to_date:
        filters["creation"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["creation"] = [">=", from_date]
    elif to_date:
        filters["creation"] = ["<=", to_date]
    filters["company"] = company

    # Fetch invoices
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "customer", "grand_total", "creation", "owner", "company"],
        order_by="creation desc"
    )

    total_count = len(invoices)
    total_amount = sum([flt(inv.get("grand_total") or 0) for inv in invoices])

    return {
        "status": "success",
        "total_count": total_count,
        "total_amount": total_amount,
    }
