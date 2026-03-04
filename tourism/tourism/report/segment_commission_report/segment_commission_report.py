# Copyright (c) 2026, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Invoice No"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 160
        },
        {
            "fieldname": "custom_airline",
            "label": _("Airline"),
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "custom_gds1",
            "label": _("GDS"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "custom_sectors",
            "label": _("Sectors"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "custom_full_route",
            "label": _("Full Route"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "custom_ticket_for",
            "label": _("Ticket For"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "custom_tour_from",
            "label": _("Tour From"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "custom_tour_to",
            "label": _("Tour To"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "custom_passenger",
            "label": _("Passenger"),
            "fieldtype": "Data",
            "width": 160
        },
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 150
        },
        {
            "fieldname": "custom_commission",
            "label": _("Commission"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "grand_total",
            "label": _("Grand Total"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "outstanding_amount",
            "label": _("Outstanding Amount"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = ""
    values = {}

    # ── Airline Filter ──
    if filters.get("airline"):
        conditions += " AND pi.supplier = %(airline)s"
        values["airline"] = filters.get("airline")

    # ── Passenger Filter ──
    if filters.get("passenger"):
        conditions += " AND pi.custom_passenger = %(passenger)s"
        values["passenger"] = filters.get("passenger")

    # ── Customer Filter ──
    if filters.get("customer"):
        conditions += " AND pi.custom_customer = %(customer)s"
        values["customer"] = filters.get("customer")

    # ── Supplier Filter ──
    if filters.get("supplier"):
        conditions += " AND pi.supplier = %(supplier)s"
        values["supplier"] = filters.get("supplier")

    # ── Commission Type Filter ──
    if filters.get("commission_type"):
        conditions += " AND pi.custom_commission_type = %(commission_type)s"
        values["commission_type"] = filters.get("commission_type")

    # ── Status Filter ──
    if filters.get("status"):
        conditions += " AND pi.status = %(status)s"
        values["status"] = filters.get("status")

    # ── Ticket Date Filter (DateRange) ──
    if filters.get("ticket_date"):
        ticket_date = filters.get("ticket_date")
        if isinstance(ticket_date, list):
            if ticket_date[0]:
                conditions += " AND pi.posting_date >= %(ticket_from)s"
                values["ticket_from"] = ticket_date[0]
            if ticket_date[1]:
                conditions += " AND pi.posting_date <= %(ticket_to)s"
                values["ticket_to"] = ticket_date[1]

    # ── Date Range Filter ──
    if filters.get("date_range"):
        date_range = filters.get("date_range")
        if isinstance(date_range, list):
            if date_range[0]:
                conditions += " AND pi.posting_date >= %(date_from)s"
                values["date_from"] = date_range[0]
            if date_range[1]:
                conditions += " AND pi.posting_date <= %(date_to)s"
                values["date_to"] = date_range[1]

    # ── Project Filter ──
    if filters.get("project"):
        conditions += " AND pi.project = %(project)s"
        values["project"] = filters.get("project")

    data = frappe.db.sql("""
        SELECT
            pi.name                 AS name,
            pi.posting_date         AS posting_date,
            pi.supplier             AS supplier,
            pi.custom_airline       AS custom_airline,
            pi.custom_gds1          AS custom_gds1,
            pi.custom_sectors       AS custom_sectors,
            pi.custom_full_route    AS custom_full_route,
            pi.custom_ticket_for    AS custom_ticket_for,
            pi.custom_tour_from     AS custom_tour_from,
            pi.custom_tour_to       AS custom_tour_to,
            pi.custom_passenger     AS custom_passenger,
            pi.project              AS project,
            pi.custom_commission    AS custom_commission,
            pi.status               AS status,
            pi.grand_total          AS grand_total,
            pi.outstanding_amount   AS outstanding_amount
        FROM
            `tabPurchase Invoice` pi
        WHERE
            pi.docstatus = 1
            AND pi.custom_purchase_invoice_for_ = 'Air Fare'
            {conditions}
        ORDER BY
            pi.posting_date DESC
        LIMIT 999999
    """.format(conditions=conditions), values, as_dict=1)

        # ── Batch fetch project names ──
    project_ids = set(row.get("project") for row in data if row.get("project"))
    project_name_map = {}
    if project_ids:
        project_records = frappe.get_all(
            "Project",
            filters={"name": ["in", list(project_ids)]},
            fields=["name", "project_name"],
        )
        for proj in project_records:
            project_name_map[proj.name] = proj.project_name or proj.name

    for row in data:
        project_id = row.get("project", "")
        row["project_display"] = project_name_map.get(project_id, project_id)

    # ── Calculate Totals ──
    total_commission  = sum(row.get("custom_commission", 0) or 0 for row in data)
    total_grand_total = sum(row.get("grand_total", 0) or 0 for row in data)
    total_outstanding = sum(row.get("outstanding_amount", 0) or 0 for row in data)
    total_sectors     = sum(int(row.get("custom_sectors") or 0) for row in data)


    # ── Append Total Row ──
    if data:
        data.append({
            "name":               "Total",
            "posting_date":       "",
            "supplier":           "",
            "custom_airline":     "",
            "custom_gds1":        "",
            "custom_sectors":     str(total_sectors),
            "custom_full_route":  "",
            "custom_ticket_for":  "",
            "custom_tour_from":   "",
            "custom_tour_to":     "",
            "custom_passenger":   "",
            "project":            "",
            "project_display":    "",
            "custom_commission":  total_commission,
            "status":             "TOTAL",
            "grand_total":        total_grand_total,
            "outstanding_amount": total_outstanding,
            "bold":               1
        })

    return data