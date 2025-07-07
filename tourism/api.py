# travel_app/api/tickets.py

import frappe
from frappe import _

@frappe.whitelist()
def get_ticket_purchase_invoices(project):
    if not project:
        return []

    config = frappe.get_doc("TravelApp Config", "TravelApp Config")
    ticket_item = config.ticket_item

    if not ticket_item:
        return []

    return frappe.get_all(
        "Purchase Invoice",
        filters={
            "project": project,
            "custom_sales_invoice": ["is", "not set"],
            "custom_purchase_invoice_for_": ticket_item
        },
        fields=[
            "name",
            "supplier",
            "custom_passenger",
            "custom_ticket_number",
            "custom_airline",
            "custom_net_fare",
            "custom_route",
            "custom_sectors"
        ],
        limit_page_length=100
    )



@frappe.whitelist()
def sales_invoice_on_submit(doc, method):
    """Triggered on Sales Invoice submit via hooks.py"""
    if not doc.get("custom_ticket_purchase_invoices"):
        return

    for row in doc.custom_ticket_purchase_invoices:
        if row.get("purchase_invoice"):
            try:
                frappe.db.set_value(
                    "Purchase Invoice",
                    row.purchase_invoice,
                    "custom_sales_invoice",
                    doc.name
                )
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Failed to update Purchase Invoice {row.purchase_invoice}")


@frappe.whitelist()
def purchase_invoice_validate(doc, method):
    """
    Prevent creating more than one Purchase Invoice for the same ticket
    (unless it's a return).
    """
    # Get the configured ticket item code
    ticket_item_code = frappe.db.get_single_value("TravelApp Config", "ticket_item")

    # Only apply this check for invoices marked against the ticket item
    if doc.custom_purchase_invoice_for_ == ticket_item_code:
        # Skip if this invoice is a return or already linked to a return
        is_return = getattr(doc, "is_return", False)
        has_return_against = bool(getattr(doc, "return_against", None))
        if not is_return and not has_return_against:
            ticket_no = doc.custom_ticket_number
            if ticket_no:
                # Look for any other PI with the same ticket number
                dup = frappe.get_all(
                    "Purchase Invoice",
                    filters={
                        "custom_purchase_invoice_for_": ticket_item_code,
                        "custom_ticket_number": ticket_no,
                        "name": ["!=", doc.name]
                    },
                    limit_page_length=1
                )
                if dup:
                    frappe.throw(_(
                        "A Purchase Invoice for ticket {0} already exists (Invoice {1})."
                    ).format(ticket_no, dup[0].name))
