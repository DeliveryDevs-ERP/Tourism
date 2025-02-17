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
def get_stay_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage stay cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)

@frappe.whitelist()
def get_hotels_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage Hotel cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def get_clause_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage clause cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)

@frappe.whitelist()
def get_Itinerary_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage itinerary cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def get_visa_type_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage loc visa cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)




@frappe.whitelist()
def get_visa_requirements_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage visa req cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
        """, (package_name,), as_dict=True)


@frappe.whitelist()
def get_visa_charges_data(package_name):
    if package_name:
        return frappe.db.sql("""
            SELECT *
            FROM `tabPackage visa charges cdt`
            WHERE `parenttype` = 'Package' AND `parent` = %s
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
                "field_map": {"opportunity_from": "quotation_to", "name": "enq_no"},
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
                    "to_date" : "to_date"
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist
