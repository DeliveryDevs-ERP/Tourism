import frappe
import json
from frappe.model.mapper import get_mapped_doc

# @frappe.whitelist()
# def filter_packages_by_city(*args, **kwargs):
#     """Retrieve hotels that match any city from the given list of cities."""
#     txt = kwargs.get('txt', '')
#     searchfield = kwargs.get('searchfield', None)
#     start = int(kwargs.get('start', 0))
#     page_len = int(kwargs.get('page_len', 20))
#     filters = kwargs.get('filters', {})
#     city_of_stay = args[5].get('city_of_stay') if len(args) > 5 else None
    
#     if not city_of_stay:
#         frappe.throw("No cities provided for filtering.")

#     if city_of_stay:
#         # Preparing the query string with placeholders for each city
#         placeholders = ', '.join(['%s'] * len(city_of_stay))  # Creates a placeholder for each city
#         query = f"""
#         SELECT `parent`
#         FROM `tabPackage stay cdt`
#         WHERE `parenttype` = 'Package' AND `city_of_stay` IN ({placeholders})
#         """
#         return frappe.db.sql(query, city_of_stay)

@frappe.whitelist()
def get_customer_branches(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")
    if customer:
        return frappe.db.sql("""
            SELECT branch_name
            FROM `tabCustomer Branch cdt`
            WHERE `parenttype` = 'Customer' AND `parent` = %s
        """, (customer,))
    return []

@frappe.whitelist()
def get_customer_depts(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer")
    if customer:
        return frappe.db.sql("""
            SELECT department_name
            FROM `tabCustomer departments cdt`
            WHERE `parenttype` = 'Customer' AND `parent` = %s
        """, (customer,))
    return []

@frappe.whitelist()
def get_stay_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage stay cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)

@frappe.whitelist()
def get_hotels_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabCosting Hotel cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)
        
@frappe.whitelist()
def get_final_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabCosting Final cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)

@frappe.whitelist()
def get_clause_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage clause cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)

@frappe.whitelist()
def get_Itinerary_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabCosting Itinerary cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def get_visa_type_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage loc visa cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)




@frappe.whitelist()
def get_visa_requirements_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage visa req cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def get_visa_charges_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage visa charges cdt`
            WHERE `parenttype` = 'Costing' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
    def set_missing_values(source, target):
        from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

        quotation = frappe.get_doc(target)

        company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

        if company_currency == quotation.currency:
            exchange_rate = 1
        else:
            exchange_rate = get_exchange_rate(
                quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
            )

        quotation.conversion_rate = exchange_rate

        # get default taxes
        taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=quotation.company)
        if taxes.get("taxes"):
            quotation.update(taxes)

        quotation.run_method("set_missing_values")
        quotation.run_method("calculate_taxes_and_totals")
        if not source.get("items", []):
            quotation.opportunity = source.name

    doclist = get_mapped_doc(
        "Opportunity",
        source_name,
        {
            "Opportunity": {
                "doctype": "Quotation",
                "field_map": {"opportunity_from": "quotation_to", "name": "enq_no", "custom_group_travel_date": "custom_group_travel_date", "custom_group_travel_estimated_date": "custom_expected_group_travel_date", "custom_proposal_submission_before": "custom_proposal_submission_before"},
            },
            "Opportunity Item": {
                "doctype": "Quotation Item",
                "field_map": {
                    "parent": "prevdoc_docname",
                    "parenttype": "prevdoc_doctype",
                    "uom": "stock_uom",
                },
                "add_if_empty": True,
            },
            "Opportunity cdt": {
                "doctype": "Package stay cdt",
                "field_map": {
                    "destination": "city_of_stay",
                    "from_date" : "from_date",
                    "to_date" : "to_date",
                    "days": "day",
                    "hotel":"hotel",
                    "hotel_category": "star" 
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist

@frappe.whitelist()
def make_costing(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def postprocess(source, target):
        target.opportunity = source.name  # Set Opportunity doc name
        # target.customer = source.party_name  # Set customer from Opportunity

    doc = get_mapped_doc(
        "Opportunity",
        source_name,
        {
            "Opportunity": {
                "doctype": "Costing",
                "field_map": {
                    "party_name": "customer",
                    "custom_group_travel_date" : "travel_date",
                    "custom_full_route" : "full_route",
                    "currency" : "currency"
                }
            },
            "Opportunity cdt": {
                "doctype": "Package stay cdt",
                "field_map": {
                    "destination": "city_of_stay",
                    "from_date": "from_date",
                    "to_date": "to_date",
                    "days": "day",
                    "hotel": "hotel",
                    "hotel_category": "star"
                },
                "add_if_empty": True
            },
        },
        target_doc,
        postprocess
    )

    return doc

@frappe.whitelist()
def make_costing_from_rfq(source_name, target_doc=None):
    """
    source_name = RFQ name
    It will create Costing by mapping from the linked Opportunity (using existing make_costing()).
    """
    rfq = frappe.get_doc("Request for Quotation", source_name)

    if not rfq.opportunity:
        frappe.throw("RFQ has no linked Opportunity.")

    # Reuse your existing Opportunity -> Costing mapping
    return make_costing(rfq.opportunity, target_doc)


@frappe.whitelist()
def make_quotation_from_costing(source_name, target_doc=None, costing_name=None):
    from frappe.model.mapper import get_mapped_doc
    from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
    from erpnext.setup.utils import get_exchange_rate

    def set_missing_values(source, target):
        quotation = frappe.get_doc(target)
        company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")
        
        # 💡 Set currency from Costing
        if costing_name:
            costing_currency = frappe.db.get_value("Costing", costing_name, "currency")
            if costing_currency:
                quotation.currency = costing_currency

        # 💱 Set exchange rate
        if company_currency == quotation.currency:
            exchange_rate = 1
        else:
            exchange_rate = get_exchange_rate(
                quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
            )

        quotation.conversion_rate = exchange_rate
        
        # if company_currency == quotation.currency:
        #     exchange_rate = 1
        # else:
        #     exchange_rate = get_exchange_rate(
        #         quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
        #     )

        quotation.conversion_rate = exchange_rate

        taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=quotation.company)
        if taxes.get("taxes"):
            quotation.update(taxes)

        quotation.custom_package = costing_name or ""  # Link the Costing doc name

        quotation.run_method("set_missing_values")
        quotation.run_method("calculate_taxes_and_totals")

        if not source.get("items", []):
            quotation.opportunity = source.name

    doclist = get_mapped_doc(
        "Opportunity",
        source_name,
        {
            "Opportunity": {
                "doctype": "Quotation",
                "field_map": {
                    "opportunity_from": "quotation_to",
                    "name": "enq_no",
                    "custom_operation_person_" : "custom_operation_person",
                    "custom_group_travel_date": "custom_group_travel_date",
                    "custom_group_travel_estimated_date": "custom_expected_group_travel_date",
                    "custom_proposal_submission_before": "custom_proposal_submission_before"
                },
            },
            "Opportunity Item": {
                "doctype": "Quotation Item",
                "field_map": {
                    "parent": "prevdoc_docname",
                    "parenttype": "prevdoc_doctype",
                    "uom": "stock_uom"
                },
                "add_if_empty": True
            },
            "Opportunity cdt": {
                "doctype": "Package stay cdt",
                "field_map": {
                    "destination": "city_of_stay",
                    "from_date": "from_date",
                    "to_date": "to_date",
                    "days": "day",
                    "hotel": "hotel",
                    "hotel_category": "star"
                },
            },
        },
        target_doc,
        lambda source, target: set_missing_values(source, target)
    )

    return doclist



def quotation_on_submit(doc, method):
    if doc.custom_package:
        frappe.db.set_value("Costing", doc.custom_package, "proposal", doc.name)
        frappe.db.commit()

@frappe.whitelist()
def quotation_on_trash(doc, method):
    try:
        if doc.custom_package:
            frappe.db.set_value("Costing", doc.custom_package, "proposal", None)
        
        # Now delete the Quotation safely
        frappe.delete_doc(
            doctype="Quotation",
            name=doc.name,
            ignore_permissions=True,
            ignore_missing=True,
            force=True,
            ignore_on_trash=True,
            ignore_links=True
        )

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Failed to unlink and delete Quotation on trash")
