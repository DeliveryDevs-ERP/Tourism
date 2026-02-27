# tourism/request_for_quotation.py

import frappe
from frappe import _
from frappe.core.doctype.communication.email import make
from frappe.desk.form.load import get_attachments
from frappe.utils import get_url
from frappe.utils.user import get_user_fullname

STANDARD_USERS = ("Guest", "Administrator")


def on_submit(doc, method):
    """
    Custom on_submit hook for Request for Quotation.
    Reads custom_send_email checkbox.
    If 1, sends email to all suppliers using 'Email Template for RFQ 02'
    with a custom subject that includes custom_group_vendor_code.
    """
    if not doc.custom_send_email:
        return

    send_custom_rfq_emails(doc)


def send_custom_rfq_emails(doc):
    """
    Loops through all suppliers in the RFQ and sends
    email using 'Email Template for RFQ 02' template.
    Subject is modified to include custom_group_vendor_code.
    """
    template_name = "Email Template for RFQ 02"

    # Validate template exists
    if not frappe.db.exists("Email Template", template_name):
        frappe.throw(
            _("Email Template '{0}' not found. Please create it first.").format(template_name)
        )

    email_template = frappe.get_doc("Email Template", template_name)

    # Get the portal link (same as original)
    rfq_link = get_rfq_portal_link(doc)

    for rfq_supplier in doc.suppliers:

        # Validate email exists
        if not rfq_supplier.email_id:
            frappe.log_error(
                message=f"No email found for supplier {rfq_supplier.supplier} in RFQ {doc.name}",
                title="RFQ Custom Email Skipped"
            )
            frappe.msgprint(
                _("Row {0}: No email found for Supplier {1}, skipping.").format(
                    rfq_supplier.idx, frappe.bold(rfq_supplier.supplier)
                ),
                alert=True,
                indicator="orange"
            )
            continue

        # Build doc_args exactly like original supplier_rfq_mail()
        full_name = get_user_fullname(frappe.session["user"])
        if full_name == "Guest":
            full_name = "Administrator"

        doc_args = doc.as_dict()

        if rfq_supplier.get("contact"):
            contact = frappe.get_doc("Contact", rfq_supplier.get("contact"))
            doc_args["contact"] = contact.as_dict()

        doc_args.update(
            {
                "supplier": rfq_supplier.get("supplier"),
                "supplier_name": rfq_supplier.get("supplier_name"),
                "portal_link": f'<a href="{rfq_link}" class="btn btn-default btn-xs" target="_blank"> {_("Submit your Quotation")} </a>',
                "user_fullname": full_name,
            }
        )

        # Render the template body
        message = frappe.render_template(email_template.response_, doc_args)

        # Build custom subject with custom_group_vendor_code
        group_vendor_code = doc.get("custom_group_vendor_code") or ""
        subject = f"Request for Quotation - {doc.name} | Group Vendor Code: {group_vendor_code}"

        # Handle sender
        sender = (
            frappe.session.user
            if frappe.session.user not in STANDARD_USERS
            else None
        )

        # Handle attachments (same as original)
        attachments = []
        if doc.send_attached_files:
            attachments = [d.name for d in get_attachments(doc.doctype, doc.name)]

        if doc.send_document_print:
            supplier_language = frappe.db.get_value(
                "Supplier", rfq_supplier.supplier, "language"
            )
            system_language = frappe.db.get_single_value("System Settings", "language")
            attachments.append(
                frappe.attach_print(
                    doc.doctype,
                    doc.name,
                    doc=doc,
                    print_format=doc.meta.default_print_format or "Standard",
                    lang=supplier_language or system_language,
                    letterhead=doc.letter_head,
                )
            )

        # Send email using make() exactly like the original
        make(
            subject=subject,
            content=message,
            recipients=rfq_supplier.email_id,
            sender=sender,
            attachments=attachments,
            send_email=True,
            doctype=doc.doctype,
            name=doc.name,
        )

        frappe.msgprint(
            _("Email Sent to Supplier {0}").format(rfq_supplier.supplier)
        )


def get_rfq_portal_link(doc):
    """Get the supplier portal link for this RFQ."""
    route = frappe.db.get_value(
        "Portal Menu Item",
        {"reference_doctype": "Request for Quotation"},
        ["route"]
    )
    if not route:
        frappe.throw(
            _("Please add Request for Quotation to the sidebar in Portal Settings.")
        )
    return get_url(f"{route}/{doc.name}")