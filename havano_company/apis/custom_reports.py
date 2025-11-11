import frappe
from frappe.utils import cint
from frappe.utils import flt
import json
from frappe.utils import flt, today, add_days

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

import frappe
from frappe.utils import flt, today, add_days


import frappe
from frappe.utils import flt, today, add_days

@frappe.whitelist(allow_guest=True)
def calculate_and_store_profit_and_loss():
    # Default dates: yesterday to today
    to_date = today()
    from_date = add_days(to_date, -1)

    # Get all companies
    companies = frappe.get_all("Company", pluck="name")

    for company in companies:
        # Get all cost centers for this company
        cost_centers = frappe.get_all("Cost Center", filters={"company": company}, pluck="name")
        cost_centers.append(None)  # Include total for the whole company

        for cc in cost_centers:
            filters = ["company=%s"]
            values = [company]

            filters.append("posting_date >= %s")
            values.append(from_date)
            filters.append("posting_date <= %s")
            values.append(to_date)

            if cc:
                filters.append("cost_center=%s")
                values.append(cc)

            where_clause = " AND ".join(filters)

            # Total Income
            income_total = frappe.db.sql(f"""
                SELECT SUM(credit - debit) as total_income
                FROM `tabGL Entry`
                WHERE {where_clause} AND account IN (
                    SELECT name FROM `tabAccount` WHERE root_type='Income'
                )
            """, tuple(values), as_dict=1)[0]["total_income"] or 0

            # Total Expense
            expense_total = frappe.db.sql(f"""
                SELECT SUM(debit - credit) as total_expense
                FROM `tabGL Entry`
                WHERE {where_clause} AND account IN (
                    SELECT name FROM `tabAccount` WHERE root_type='Expense'
                )
            """, tuple(values), as_dict=1)[0]["total_expense"] or 0

            gross_profit_loss = flt(income_total) - flt(expense_total)

            # Create / insert record in Profit and Loss per Cost Center
            pl_doc = frappe.get_doc({
                "doctype": "Profit and Loss per Cost Center",
                "company": company,
                "cost_center": cc or "All",
                "income": flt(income_total),
                "expense": flt(expense_total),
                "gross_profit__loss": gross_profit_loss,
                "date": to_date
            })

            pl_doc.flags.ignore_permissions = True
            pl_doc.insert()
            frappe.db.commit()

    return {"status": "success", "message": "Profit and Loss per Cost Center calculated and stored."}

