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

	# ── NEW: Collect all project IDs for batch name lookup ──
	project_ids = set()
	for row in data:
		if not isinstance(row, dict):
			continue
		if row.get("project"):
			project_ids.add(row["project"])
	# Also collect from pe_data and si_data
	for pe in pe_data.values():
		if pe.get("project"):
			project_ids.add(pe["project"])
	for si in si_data.values():
		if si.get("project"):
			project_ids.add(si["project"])

	# ── NEW: Batch fetch project names ──
	project_name_map = {}
	if project_ids:
		project_records = frappe.get_all(
			"Project",
			filters={"name": ["in", list(project_ids)]},
			fields=["name", "project_name"],
		)
		for proj in project_records:
			project_name_map[proj.name] = proj.project_name or proj.name

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

		# ── NEW: Resolve project ID to full project name ──
		project_id = row.get("project", "")
		row["project_display"] = project_name_map.get(project_id, project_id)

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