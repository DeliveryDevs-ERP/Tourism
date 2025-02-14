# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VisaChargesandRequirements(Document):
    pass

@frappe.whitelist()
def get_visa_types(country):
    if not country:
        return []

    visa_types = []
    # Get all entries from "Country visa type" including their names
    visa_type_entries = frappe.get_list("Country visa type", fields=["*"])

    for entry in visa_type_entries:
        # frappe.errprint(f"entry {entry}")
        # Fetch all "Country cdt" entries that are linked to the current "Country visa type"
        countries = frappe.get_all("Country cdt", 
                                    filters={
                                        'parent': entry['name'],
                                        'parenttype': "Country visa type",
                                        'parentfield': "country"
                                    },
                                    fields=["country"])
        # frappe.errprint(f"countries cdt {countries}")
        if any(c['country'] == country for c in countries):
            visa_types.append(entry['visa_type'])

    # frappe.errprint(f"visa_types {visa_types}")
    return visa_types
