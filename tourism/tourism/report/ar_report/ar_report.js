// Copyright (c) 2026, Your Company and contributors
// For license information, please see license.txt

frappe.query_reports["AR Report"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "report_date",
			label: __("Posting Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "party",
			label: __("Customer"),
			fieldtype: "MultiSelectList",
			options: "Customer",
			get_data: function (txt) {
				return frappe.db.get_link_options("Customer", txt);
			},
		},
		{
			fieldname: "party_account",
			label: __("Receivable Account"),
			fieldtype: "Link",
			options: "Account",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
						account_type: "Receivable",
						is_group: 0,
					},
				};
			},
		},
		{
			fieldname: "ageing_based_on",
			label: __("Ageing Based On"),
			fieldtype: "Select",
			options: "Posting Date\nDue Date",
			default: "Due Date",
		},
		{
			fieldname: "calculate_ageing_with",
			label: __("Calculate Ageing With"),
			fieldtype: "Select",
			options: "Report Date\nPosting Date",
			default: "Report Date",
		},
		{
			fieldname: "range",
			label: __("Ageing Range"),
			fieldtype: "Data",
			default: "30, 60, 90, 120",
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "MultiSelectList",
			options: "Customer Group",
			get_data: function (txt) {
				return frappe.db.get_link_options("Customer Group", txt);
			},
		},
		{
			fieldname: "payment_terms_template",
			label: __("Payment Terms Template"),
			fieldtype: "Link",
			options: "Payment Terms Template",
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "MultiSelectList",
			options: "Territory",
			get_data: function (txt) {
				return frappe.db.get_link_options("Territory", txt);
			},
		},
		{
			fieldname: "sales_partner",
			label: __("Sales Partner"),
			fieldtype: "Link",
			options: "Sales Partner",
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		},
		{
			fieldname: "based_on_payment_terms",
			label: __("Based On Payment Terms"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_future_payments",
			label: __("Show Future Payments"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_delivery_notes",
			label: __("Show Delivery Notes"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_sales_person",
			label: __("Show Sales Person"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_remarks",
			label: __("Show Remarks"),
			fieldtype: "Check",
		},
		{
			fieldname: "tax_id",
			label: __("Tax Id"),
			fieldtype: "Data",
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "outstanding" && data) {
			if (flt(data.outstanding) > 0) {
				value = "<span style='color:red;font-weight:bold'>" + value + "</span>";
			}
		}

		if (column.fieldname === "age" && data) {
			if (data.age > 120) {
				value = "<span style='color:red;font-weight:bold'>" + value + "</span>";
			} else if (data.age > 90) {
				value = "<span style='color:orange;font-weight:bold'>" + value + "</span>";
			}
		}

		if (column.fieldname === "voucher_no" && data) {
			value = "<b>" + value + "</b>";
		}

		return value;
	},
};

erpnext.utils.add_dimensions("AR Report", 9);