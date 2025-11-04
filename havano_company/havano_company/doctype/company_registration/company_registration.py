# Copyright (c) 2025, nasirucode and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from datetime import datetime

class CompanyRegistration(Document):
    def before_save(doc, method=None):
        if doc.subscription:
            print("===================sss================reg")
            try:
                # Convert to Python date
                subscription_date = frappe.utils.getdate(doc.subscription)
                today = frappe.utils.getdate(frappe.utils.nowdate())

                # Calculate difference in days
                days_left = (subscription_date - today).days

                print(f"==================================={days_left} reg")

                # Assign result to a field on the DocType (you must have this field)
                doc.days_left = days_left

            except Exception as e:
                print(f"Error calculating days left: {str(e)}")
