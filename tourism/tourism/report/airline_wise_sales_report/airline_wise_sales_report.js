// Copyright (c) 2026, OsamaASidd and contributors
// For license information, please see license.txt

frappe.query_reports["Airline Wise Sales Report"] = {
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
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        },
        {
            "fieldname": "supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "reqd": 0
        }
    ],

    // ── Formatter to Bold and Highlight the Total Row ──
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && data.bold === 1) {
            value = `<span style="
                font-weight: bold;
                display: block;
                padding: 2px 4px;
            ">${value}</span>`;
        }

        return value;
    }
};