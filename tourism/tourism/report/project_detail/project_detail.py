# Copyright (c) 2026, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    if not filters or not filters.get("project"):
        return [], []

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "sales_order",
            "label": _("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 210
        },
        {
            "fieldname": "quotation",
            "label": _("Quotation"),
            "fieldtype": "Link",
            "options": "Quotation",
            "width": 210
        },
        {
            "fieldname": "opportunity",
            "label": _("Opportunity"),
            "fieldtype": "Link",
            "options": "Opportunity",
            "width": 210
        },
        {
            "fieldname": "rfq",
            "label": _("RFQ"),
            "fieldtype": "Link",
            "options": "Request for Quotation",
            "width": 210
        },
        {
            "fieldname": "costing",
            "label": _("Costing"),
            "fieldtype": "Link",
            "options": "Costing",
            "width": 210
        },
    ]


def get_data(filters):
    project = filters.get("project")
    data = []

    # ── Step 1: Get Sales Order linked to Project ──
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={"project": project, "docstatus": ["!=", 2]},
        fields=["name"]
    )

    if not sales_orders:
        return []

    for so in sales_orders:
        so_name = so.name

        # ── Step 2: Get Quotation from Sales Order items ──
        so_items = frappe.get_all(
            "Sales Order Item",
            filters={"parent": so_name},
            fields=["prevdoc_docname"],
            limit=1
        )

        if not so_items or not so_items[0].get("prevdoc_docname"):
            continue

        quotation_name = so_items[0].get("prevdoc_docname")

        # ── Step 3: Get Opportunity from Quotation ──
        quotations = frappe.get_all(
            "Quotation",
            filters={"name": quotation_name},
            fields=["name", "opportunity"]
        )

        if not quotations or not quotations[0].get("opportunity"):
            continue

        opportunity_name = quotations[0].get("opportunity")

        # ── Step 4: Get all RFQs linked to Opportunity ──
        rfqs = frappe.get_all(
            "Request for Quotation",
            filters={"opportunity": opportunity_name},
            fields=["name"]
        )

        if not rfqs:
            continue

        # ── Step 5: Get all Costings linked to Opportunity ──
        costings = frappe.get_all(
            "Costing",
            filters={"opportunity": opportunity_name},
            fields=["name"]
        )

        if not costings:
            continue

        # ── Step 6: Build rows — one row per RFQ + Costing combination ──
        for rfq in rfqs:
            for costing in costings:
                data.append({
                    "sales_order": so_name,
                    "quotation":   quotation_name,
                    "opportunity": opportunity_name,
                    "rfq":         rfq.name,
                    "costing":     costing.name,
                })

    return data
