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
            "custom_route"
        ],
        limit_page_length=100
    )
