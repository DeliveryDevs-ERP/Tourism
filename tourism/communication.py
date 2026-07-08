# tourism/communication.py

import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import get_url

# User groups whose members get notified about received RFQ emails.
NOTIFY_USER_GROUPS = ["Operations", "Sales"]


def after_insert(doc, method=None):
    """When an email is *received* against a Request for Quotation, notify all
    members of the Operations and Sales user groups and give them a link to
    open the RFQ.

    Wired via `doc_events` on Communication (see hooks.py).
    """
    # Only inbound emails (the "RE:" reply the supplier sends back).
    if doc.communication_type != "Communication":
        return
    if doc.sent_or_received != "Received":
        return
    # Must be linked to a Request for Quotation.
    if doc.reference_doctype != "Request for Quotation" or not doc.reference_name:
        return

    recipients = get_group_recipients(NOTIFY_USER_GROUPS)
    if not recipients:
        return

    rfq = doc.reference_name
    rfq_link = get_url(f"/app/request-for-quotation/{rfq}")

    subject = f"RE: Supplier reply received against RFQ {rfq}"

    message = frappe.render_template(
        """
        <p>An email has been received from a supplier against
        <b>Request for Quotation {{ rfq }}</b>.</p>
        <table style="border-collapse:collapse;">
            <tr><td style="padding:2px 8px;"><b>From</b></td>
                <td style="padding:2px 8px;">{{ sender_full_name or sender or "" }}
                    {% if sender %}&lt;{{ sender }}&gt;{% endif %}</td></tr>
            <tr><td style="padding:2px 8px;"><b>Subject</b></td>
                <td style="padding:2px 8px;">{{ email_subject or "" }}</td></tr>
        </table>
        <p style="margin-top:16px;">
            <a href="{{ rfq_link }}" class="btn btn-primary"
               style="background:#2490ef;color:#fff;padding:8px 16px;
                      border-radius:6px;text-decoration:none;" target="_blank">
                Open Request for Quotation
            </a>
        </p>
        """,
        {
            "rfq": rfq,
            "rfq_link": rfq_link,
            "sender": doc.sender,
            "sender_full_name": doc.sender_full_name,
            "email_subject": doc.subject,
        },
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        reference_doctype=doc.reference_doctype,
        reference_name=doc.reference_name,
    )

    # Bell-icon (System) notification. Clicking it opens the RFQ because
    # document_type / document_name are set. type="Alert" so it shows even
    # when the recipient happens to be the sender.
    enqueue_create_notification(
        recipients,
        {
            "type": "Alert",
            "document_type": doc.reference_doctype,
            "document_name": doc.reference_name,
            "subject": subject,
            "from_user": doc.sender or frappe.session.user,
            "email_content": message,
        },
    )


def get_group_recipients(groups):
    """Return the de-duplicated email addresses of enabled users belonging to
    the given User Groups."""
    users = frappe.get_all(
        "User Group Member",
        filters={"parenttype": "User Group", "parent": ["in", groups]},
        pluck="user",
    )
    if not users:
        return []

    emails = frappe.get_all(
        "User",
        filters={"name": ["in", list(set(users))], "enabled": 1},
        pluck="email",
    )
    return list({e for e in emails if e})
