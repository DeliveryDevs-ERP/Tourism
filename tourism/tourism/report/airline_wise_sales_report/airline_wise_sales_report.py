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
            "label": _("Purchase Invoice"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "fieldname": "posting_date",
            "label": _("Ticket Date"),
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "supplier",
            "label": _("Airline / Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 160
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

    # ── Supplier Filter ──
    if filters.get("supplier"):
        conditions += " AND pi.supplier = %(supplier)s"
        values["supplier"] = filters.get("supplier")

    # ── Status Filter ──
    if filters.get("status"):
        conditions += " AND pi.status = %(status)s"
        values["status"] = filters.get("status")

    # ── Ticket Date Filter (DateRange) ──
    if filters.get("ticket_date"):
        ticket_date = filters.get("ticket_date")
        if isinstance(ticket_date, list):
            if ticket_date[0]:
                conditions += " AND pi.posting_date >= %(from_date)s"
                values["from_date"] = ticket_date[0]
            if ticket_date[1]:
                conditions += " AND pi.posting_date <= %(to_date)s"
                values["to_date"] = ticket_date[1]

    # ── Project Filter ──
    if filters.get("project"):
        conditions += " AND pi.project = %(project)s"
        values["project"] = filters.get("project")

    data = frappe.db.sql("""
        SELECT
            pi.name                       AS name,
            pi.posting_date               AS posting_date,
            pi.supplier                   AS supplier,
            pi.custom_passenger           AS custom_passenger,
            pi.project                    AS project,
            pi.status                     AS status,
            pi.grand_total                AS grand_total,
            pi.outstanding_amount         AS outstanding_amount
        FROM
            `tabPurchase Invoice` pi
        WHERE
            pi.docstatus != 2
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
    total_grand_total = sum(row.get("grand_total", 0) or 0 for row in data)
    total_outstanding = sum(row.get("outstanding_amount", 0) or 0 for row in data)

    # ── Append Total Row ──
    if data:
        data.append({
            "name":               "Total",
            "posting_date":       "",
            "supplier":           "",
            "custom_passenger":   "",
            "project":            "",
            "project_display":    "",
            "status":             "TOTAL",
            "grand_total":        total_grand_total,
            "outstanding_amount": total_outstanding,
            "bold":               1
        })

    return data