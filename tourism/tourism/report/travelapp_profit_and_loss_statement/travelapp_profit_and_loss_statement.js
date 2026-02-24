// Copyright (c) 2026, OsamaASidd and contributors
// For license information, please see license.txt

frappe.query_reports["TravelApp Profit and Loss Statement"] = {
    "filters": []
};

frappe.query_reports["TravelApp Profit and Loss Statement"] = $.extend(
    {},
    erpnext.financial_statements
);

erpnext.utils.add_dimensions("TravelApp Profit and Loss Statement", 10);

// ── STEP 1: Remove the built-in Project filter to avoid duplicate ──
var existing_filters = frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"];
frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"] = existing_filters.filter(
    f => f.fieldname !== "project"
);

// ── STEP 2: Add Customer Filter ──
frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"].push({
    fieldname: "customer",
    label: __("Customer"),
    fieldtype: "Link",
    options: "Customer",
    reqd: 0,
    on_change: function(report) {
        var customer = report.get_filter_value("customer");

        // Clear project filter when customer is cleared
        if (!customer) {
            report.set_filter_value("project", []);
            return;
        }

        // Fetch all projects linked to selected customer
        frappe.db.get_list("Project", {
            filters: { "customer": customer },
            fields: ["name"],
            limit: 0
        }).then(function(projects) {
            if (projects && projects.length > 0) {
                var project_names = projects.map(p => p.name);
                report.set_filter_value("project", project_names);
            } else {
                report.set_filter_value("project", []);
                frappe.msgprint({
                    title: __("No Projects Found"),
                    message: __("There are no projects linked to the selected customer."),
                    indicator: "orange"
                });
            }
        });
    }
});

// ── STEP 3: Add Project MultiSelect Filter ──
frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"].push({
    fieldname: "project",
    label: __("Project"),
    fieldtype: "MultiSelectList",
    reqd: 0,
    get_data: function(txt) {
        var customer = frappe.query_report.get_filter_value("customer");
        var filters = {};

        if (customer) {
            filters["customer"] = customer;
        }

        if (txt) {
            filters["name"] = ["like", "%" + txt + "%"];
        }

        return frappe.db.get_list("Project", {
            filters: filters,
            fields: ["name"],
            limit: 20
        }).then(function(projects) {
            return projects.map(p => ({
                value: p.name,
                description: p.name
            }));
        });
    }
});

// ── STEP 4: Checkboxes come AFTER Customer and Project ──
frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"].push({
    fieldname: "selected_view",
    label: __("Select View"),
    fieldtype: "Select",
    options: [
        { value: "Report", label: __("Report View") },
        { value: "Growth", label: __("Growth View") },
        { value: "Margin", label: __("Margin View") },
    ],
    default: "Report",
    reqd: 1,
});

frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"].push({
    fieldname: "accumulated_values",
    label: __("Accumulated Values"),
    fieldtype: "Check",
    default: 1,
});

frappe.query_reports["TravelApp Profit and Loss Statement"]["filters"].push({
    fieldname: "include_default_book_entries",
    label: __("Include Default FB Entries"),
    fieldtype: "Check",
    default: 1,
});