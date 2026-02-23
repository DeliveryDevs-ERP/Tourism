// Copyright (c) 2026, OsamaASidd and contributors
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
			reqd: 1,
		},
		{
			fieldname: "ageing_based_on",
			label: __("Ageing Based On"),
			fieldtype: "Select",
			options: "Due Date\nPosting Date",
			default: "Due Date",
		},
		{
			fieldname: "range1",
			label: __("Ageing Range 1"),
			fieldtype: "Int",
			default: 30,
			reqd: 1,
		},
		{
			fieldname: "range2",
			label: __("Ageing Range 2"),
			fieldtype: "Int",
			default: 60,
			reqd: 1,
		},
		{
			fieldname: "range3",
			label: __("Ageing Range 3"),
			fieldtype: "Int",
			default: 90,
			reqd: 1,
		},
		{
			fieldname: "range4",
			label: __("Ageing Range 4"),
			fieldtype: "Int",
			default: 120,
			reqd: 1,
		},
		{
			fieldname: "party",
			label: __("Customer"),
			fieldtype: "MultiSelectLink",
			options: "Customer",
			get_query: function () {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
					},
				};
			},
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "MultiSelectLink",
			options: "Customer Group",
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "MultiSelectLink",
			options: "Territory",
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

		return value;
	},
};