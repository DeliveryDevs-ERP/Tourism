import frappe
from frappe import _


def execute(filters=None):
	args = {
		"party_type": "Customer",
		"naming_by": ["Selling Settings", "cust_master_name"],
	}
	return ReceivableReport(filters).run(args)


class ReceivableReport:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.filters.report_date = self.filters.report_date or frappe.utils.today()
		self.filters.company = self.filters.company or frappe.defaults.get_user_default("Company")
		self.filters.party_type = "Customer"
		self.filters.ageing_based_on = self.filters.ageing_based_on or "Due Date"
		self.filters.range1 = self.filters.range1 or 30
		self.filters.range2 = self.filters.range2 or 60
		self.filters.range3 = self.filters.range3 or 90
		self.filters.range4 = self.filters.range4 or 120

	def run(self, args):
		from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as ar_execute

		# Build filters for the standard AR report
		ar_filters = frappe._dict({
			"company": self.filters.company,
			"report_date": self.filters.report_date,
			"ageing_based_on": self.filters.ageing_based_on,
			"range1": self.filters.range1,
			"range2": self.filters.range2,
			"range3": self.filters.range3,
			"range4": self.filters.range4,
			"party_type": "Customer",
			"party": self.filters.party or [],
			"customer_group": self.filters.customer_group or [],
			"territory": self.filters.territory or [],
		})

		# Execute the standard AR report
		columns, data, *rest = ar_execute(ar_filters)

		# Build custom columns
		custom_columns = self.get_columns()

		# Enrich data with custom fields
		enriched_data = self.enrich_data(data)

		chart = self.get_chart_data(enriched_data)
		report_summary = self.get_report_summary(enriched_data)

		return custom_columns, enriched_data, None, chart, report_summary

	def get_columns(self):
		columns = [
			{
				"label": _("Posting Date"),
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"width": 90,
			},
			{
				"label": _("Party"),
				"fieldname": "party",
				"fieldtype": "Dynamic Link",
				"options": "party_type",
				"width": 180,
			},
			{
				"label": _("Project"),
				"fieldname": "project",
				"fieldtype": "Link",
				"options": "Project",
				"width": 100,
			},
			{
				"label": _("Voucher Type"),
				"fieldname": "voucher_type",
				"fieldtype": "Data",
				"width": 120,
			},
			{
				"label": _("Voucher No"),
				"fieldname": "voucher_no",
				"fieldtype": "Dynamic Link",
				"options": "voucher_type",
				"width": 180,
			},
			{
				"label": _("Party Description"),
				"fieldname": "custom_party_description",
				"fieldtype": "Small Text",
				"width": 100,
			},
			{
				"label": _("Payment Type"),
				"fieldname": "payment_type",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _("Due Date"),
				"fieldname": "due_date",
				"fieldtype": "Date",
				"width": 90,
			},
			{
				"label": _("Invoiced Amount"),
				"fieldname": "invoiced",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Paid Amount"),
				"fieldname": "paid",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Credit Note"),
				"fieldname": "credit_note",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Outstanding Amount"),
				"fieldname": "outstanding",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Age (Days)"),
				"fieldname": "age",
				"fieldtype": "Int",
				"width": 80,
			},
			{
				"label": _("0-30"),
				"fieldname": "range1",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("31-60"),
				"fieldname": "range2",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("61-90"),
				"fieldname": "range3",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("91-120"),
				"fieldname": "range4",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("121-Above"),
				"fieldname": "range5",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Notes"),
				"fieldname": "custom_notes",
				"fieldtype": "Long Text",
				"width": 100,
			},
			{
				"label": _("Cost Center"),
				"fieldname": "cost_center",
				"fieldtype": "Data",
				"width": 120,
			},
			{
				"label": _("Receivable Account"),
				"fieldname": "party_account",
				"fieldtype": "Link",
				"options": "Account",
				"width": 180,
			},
			{
				"label": _("Customer Contact"),
				"fieldname": "customer_primary_contact",
				"fieldtype": "Link",
				"options": "Contact",
				"width": 120,
			},
			{
				"label": _("Customer LPO"),
				"fieldname": "po_no",
				"fieldtype": "Data",
				"width": 120,
			},
			{
				"label": _("Territory"),
				"fieldname": "territory",
				"fieldtype": "Link",
				"options": "Territory",
				"width": 120,
			},
			{
				"label": _("Customer Group"),
				"fieldname": "customer_group",
				"fieldtype": "Link",
				"options": "Customer Group",
				"width": 120,
			},
			{
				"label": _("Currency"),
				"fieldname": "currency",
				"fieldtype": "Link",
				"options": "Currency",
				"width": 80,
			},
			{
				"label": _("Party Type"),
				"fieldname": "party_type",
				"fieldtype": "Data",
				"width": 100,
			},
		]

		return columns

	def enrich_data(self, data):
		"""Enrich data rows with custom fields from Payment Entry and Sales Invoice."""
		if not data:
			return data

		# Collect voucher numbers by type for batch fetching
		payment_entries = set()
		sales_invoices = set()

		for row in data:
			if isinstance(row, dict):
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
				fields=["name", "custom_party_description", "payment_type", "custom_notes"],
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
				row["custom_party_description"] = pe.get("custom_party_description", "")
				row["payment_type"] = pe.get("payment_type", "")
				row["custom_notes"] = pe.get("custom_notes", "")

			if voucher_type == "Sales Invoice" and voucher_no in si_data:
				si = si_data[voucher_no]
				row["project"] = si.get("project", "")

		return data

	def get_chart_data(self, data):
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

	def get_report_summary(self, data):
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