# Copyright (c) 2026, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	# Force party_type to Customer for AR
	filters.party_type = "Customer"

	if not filters.get("report_date"):
		filters.report_date = frappe.utils.today()

	if not filters.get("company"):
		filters.company = frappe.defaults.get_user_default("Company")

	if not filters.get("range"):
		filters.range = "30, 60, 90, 120"

	# Parse range string into range1-4 as the standard report expects
	range_list = [int(x.strip()) for x in filters.range.split(",") if x.strip()]
	filters.range1 = range_list[0] if len(range_list) > 0 else 30
	filters.range2 = range_list[1] if len(range_list) > 1 else 60
	filters.range3 = range_list[2] if len(range_list) > 2 else 90
	filters.range4 = range_list[3] if len(range_list) > 3 else 120

	# Execute the standard AR report
	from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as ar_execute

	columns, data, *rest = ar_execute(filters)

	# Enrich data with custom fields
	data = enrich_data(data)

	# Build custom columns (insert custom ones into existing)
	custom_columns = get_custom_columns(columns)

	chart = get_chart_data(data)
	report_summary = get_report_summary(data)

	return custom_columns, data, None, chart, report_summary


def get_custom_columns(original_columns):
	"""Return columns matching the print format layout."""
	return [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90,
		},
		{
			"label": _("Inv. No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 120,
		},
		{
			"label": _("Notes"),
			"fieldname": "custom_notes",
			"fieldtype": "Small Text",
			"width": 200,
		},
		{
			"label": _("Voucher Type"),
			"fieldname": "payment_type",
			"fieldtype": "Data",
			"width": 120,
		},  
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
   			"options": "Project",
			"width": 120,
		},  
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 400,
		},
		{
			"label": _("SaleAmt (Net)"),
			"fieldname": "invoiced",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Refund Amt"),
			"fieldname": "credit_note",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 110,
		},
		{
			"label": _("Receipt"),
			"fieldname": "paid",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Balance"),
			"fieldname": "outstanding",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 130,
		},
		{
			"label": _("Days Over"),
			"fieldname": "age",
			"fieldtype": "Int",
			"width": 80,
		},
		# Hidden columns needed for links/print
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 0,
			"hidden": 1,
		},
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 0,
			"hidden": 1,
		},
	]


def enrich_data(data):
	"""Enrich data rows with custom fields from Payment Entry and Sales Invoice."""
	if not data:
		return data

	# Collect voucher numbers by type for batch fetching
	payment_entries = set()
	sales_invoices = set()

	for row in data:
		if not isinstance(row, dict):
			continue
		voucher_type = row.get("voucher_type", "")
		voucher_no = row.get("voucher_no", "")
		if voucher_type == "Payment Entry" and voucher_no:
			payment_entries.add(voucher_no)
		elif voucher_type == "Sales Invoice" and voucher_no:
			sales_invoices.add(voucher_no)

	# Fetch custom fields from Payment Entry
	pe_data = {}
	if payment_entries:
		pe_records = frappe.get_all(
			"Payment Entry",
			filters={"name": ["in", list(payment_entries)]},
			fields=["name", "project", "custom_party_description", "payment_type", "custom_notes"],
		)
		for pe in pe_records:
			pe_data[pe.name] = pe

	# Fetch project from Sales Invoice
	si_data = {}
	if sales_invoices:
		si_records = frappe.get_all(
			"Sales Invoice",
			filters={"name": ["in", list(sales_invoices)]},
			fields=["name", "project"],
		)
		for si in si_records:
			si_data[si.name] = si

	# Enrich rows
	for row in data:
		if not isinstance(row, dict):
			continue

		voucher_type = row.get("voucher_type", "")
		voucher_no = row.get("voucher_no", "")

		if voucher_type == "Payment Entry" and voucher_no in pe_data:
			pe = pe_data[voucher_no]
			row["project"] = pe.get("project", "")
			row["custom_party_description"] = pe.get("custom_party_description", "")
			row["payment_type"] = pe.get("payment_type", "")
			row["custom_notes"] = pe.get("custom_notes", "")

		if voucher_type == "Sales Invoice" and voucher_no in si_data:
			si = si_data[voucher_no]
			row["project"] = si.get("project", "")

		if not row.get("payment_type"):
			if voucher_type == "Sales Invoice":
				row["payment_type"] = "Sales Invoice"
			elif voucher_type == "Purchase Invoice":
				row["payment_type"] = "Purchase Invoice"
			elif voucher_type == "Journal Entry":
				row["payment_type"] = "Journal Entry"


		# Build description: party + party_description + project
		desc_parts = []
		if row.get("party"):
			desc_parts.append(row["party"])
		if row.get("custom_party_description"):
			desc_parts.append(row["custom_party_description"])
		if row.get("project"):
			desc_parts.append(row["project"])
		row["description"] = " - ".join(desc_parts)

	return data


def get_chart_data(data):
	if not data:
		return None

	total_range1 = total_range2 = total_range3 = total_range4 = total_range5 = 0

	for row in data:
		if not isinstance(row, dict):
			continue
		total_range1 += row.get("range1", 0) or 0
		total_range2 += row.get("range2", 0) or 0
		total_range3 += row.get("range3", 0) or 0
		total_range4 += row.get("range4", 0) or 0
		total_range5 += row.get("range5", 0) or 0

	return {
		"data": {
			"labels": ["0-30", "31-60", "61-90", "91-120", "121-Above"],
			"datasets": [
				{
					"name": _("Outstanding Amount"),
					"values": [total_range1, total_range2, total_range3, total_range4, total_range5],
				}
			],
		},
		"type": "bar",
		"colors": ["#318AD8"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_invoiced = 0
	total_paid = 0
	total_outstanding = 0
	total_credit_note = 0

	for row in data:
		if not isinstance(row, dict):
			continue
		total_invoiced += row.get("invoiced", 0) or 0
		total_paid += row.get("paid", 0) or 0
		total_outstanding += row.get("outstanding", 0) or 0
		total_credit_note += row.get("credit_note", 0) or 0

	return [
		{
			"value": total_invoiced,
			"indicator": "Blue",
			"label": _("Total Invoiced"),
			"datatype": "Currency",
		},
		{
			"value": total_paid,
			"indicator": "Green",
			"label": _("Total Paid"),
			"datatype": "Currency",
		},
		{
			"value": total_credit_note,
			"indicator": "Orange",
			"label": _("Total Credit Note"),
			"datatype": "Currency",
		},
		{
			"value": total_outstanding,
			"indicator": "Red",
			"label": _("Total Outstanding"),
			"datatype": "Currency",
		},
	]