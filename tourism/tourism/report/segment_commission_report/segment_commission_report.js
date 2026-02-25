// Copyright (c) 2026, OsamaASidd and contributors
// For license information, please see license.txt

frappe.query_reports["Segment Commission Report"] = {
    "filters": [
        {
            "fieldname": "airline",
            "label": __("Airline"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0
        },
        {
            "fieldname": "passenger",
            "label": __("Passenger"),
            "fieldtype": "Data",
            "reqd": 0
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0
        },
        {
            "fieldname": "supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0
        },
        {
            "fieldname": "commission_type",
            "label": __("Commission Type"),
            "fieldtype": "Select",
            "options": "\nDomestic\nInternational\nCargo\nGroup",
            "reqd": 0
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nSubmitted\nCancelled\nReturn",
            "reqd": 0
        },
        {
            "fieldname": "ticket_date",
            "label": __("Ticket Date"),
            "fieldtype": "DateRange",
            "reqd": 0
        },
        {
            "fieldname": "date_range",
            "label": __("Date Range"),
            "fieldtype": "DateRange",
            "reqd": 0
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        }
    ]
};