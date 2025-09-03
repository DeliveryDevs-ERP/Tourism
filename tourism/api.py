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
            "custom_full_route",
            "custom_sectors",
            "custom_ticket_margin"
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
                    return
        if is_return:
            ticket_no = doc.custom_ticket_number
            dup = frappe.get_all(
                    "Purchase Invoice",
                    filters={
                        "custom_purchase_invoice_for_": ticket_item_code,
                        "custom_ticket_number": ticket_no,
                        "name": ["!=", doc.name]
                    },
                )
            if len(dup) > 1:
                    frappe.throw(_(
                        "Cannot create return. 2 Purchase Invoices for ticket {0} already exists."
                    ).format(ticket_no, dup[0].name))
                    return
            


@frappe.whitelist()
def get_customer_primary_contact_details(contact_person):
    """
    Fetch primary contact details and linked custom fields from the Contact associated with the given Customer.
    """
    if not contact_person:
        return {}

    # Get the Contact linked to the Customer
    contact = frappe.get_doc(
        "Contact",contact_person
    )

    # if not contact_links:
    #     return {}

    # contact_name = contact_links[0].parent
    # contact = frappe.get_doc("Contact", contact_name)

    # Find matching email from 'Contact Email' table inside doc
    email = ""
    if contact.email_ids:
        for row in contact.email_ids:
            if row.parent == contact.name:
                email = row.email_id
                break

    # Find matching phone from 'Contact Phone' table inside doc
    phone = ""
    if contact.phone_nos:
        for row in contact.phone_nos:
            if row.parent == contact.name:
                phone = row.phone
                break

    return {
        "custom_designation": contact.get("designation"),
        "custom_department": contact.get("department"),
        "custom_branch": contact.get("custom_branch"),
        "contact_email": email,
        "contact_mobile": phone
    }