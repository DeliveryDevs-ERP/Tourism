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
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 90
        },
        {
            "fieldname": "voucher_no",
            "label": _("Inv. No"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 160
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "invoiced",
            "label": _("Sale Amt (Net)"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "credit_note",
            "label": _("Refund Amt"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "paid",
            "label": _("Receipt"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "outstanding",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "age",
            "label": _("Days Over"),
            "fieldtype": "Int",
            "width": 80
        }
    ]


def get_data(filters):
    conditions = ""

    if filters.get("party"):
        conditions = "AND si.customer = %(party)s"

    report_date = filters.get("report_date") or frappe.utils.today()

    data = frappe.db.sql("""
        SELECT
            si.posting_date                          AS posting_date,
            si.name                                  AS voucher_no,
            si.title                                 AS description,
            si.grand_total                           AS invoiced,
            0                                        AS credit_note,
            (si.grand_total - si.outstanding_amount) AS paid,
            si.outstanding_amount                    AS outstanding,
            DATEDIFF(%(report_date)s, si.due_date)   AS age
        FROM
            `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.outstanding_amount > 0
            {conditions}
        ORDER BY
            si.posting_date ASC
    """.format(conditions=conditions), {
        "party": filters.get("party"),
        "report_date": report_date
    }, as_dict=1)

    return data