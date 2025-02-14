import frappe
import json

@frappe.whitelist()
def filter_packages_by_city(*args, **kwargs):
    """Retrieve hotels that match all cities from the given list of cities."""
    txt = kwargs.get('txt', '')
    searchfield = kwargs.get('searchfield', None)
    start = int(kwargs.get('start', 0))
    page_len = int(kwargs.get('page_len', 20))
    filters = kwargs.get('filters', {})
    city_of_stay = args[5].get('city_of_stay') if len(args) > 5 else None
    
    if not city_of_stay:
        frappe.throw("No cities provided for filtering.")

    if city_of_stay:
        # Using a subquery to check each package for all required cities
        placeholders = ', '.join(['%s'] * len(city_of_stay))
        query = f"""
        SELECT `parent`
        FROM `tabPackage stay cdt`
        WHERE `parenttype` = 'Package'
        GROUP BY `parent`
        HAVING COUNT(DISTINCT `city_of_stay`) = {len(city_of_stay)}
        AND SUM(CASE WHEN `city_of_stay` IN ({placeholders}) THEN 1 ELSE 0 END) = {len(city_of_stay)}
        """
        return frappe.db.sql(query, city_of_stay)



@frappe.whitelist()
def get_hotels_based_on_city(*args, **kwargs):
    """Retrieve hotels that match any city from the given list of cities."""
    txt = kwargs.get('txt', '')
    searchfield = kwargs.get('searchfield', None)
    start = int(kwargs.get('start', 0))
    page_len = int(kwargs.get('page_len', 20))
    filters = kwargs.get('filters', {})
    cities = args[5].get('cities')    
    try:
        if cities:
            return frappe.db.sql(f"""
            SELECT `name`, `name1`
        FROM `tabHotel`
        WHERE `city` IN ({', '.join(['%s'] * len(cities))})
            """, (cities),
            )
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to execute SQL query in get_hotels_based_on_city")
        frappe.throw(("Error fetching container data: {0}").format(str(e)))


@frappe.whitelist()
def fetch_hotel_room_details(hotel_name , star):
    """Fetch room details for the specified hotel."""
    hotel = frappe.get_doc('Hotel', {'name': hotel_name})
    if not hotel:
        return []
    room_details = []
    for room in hotel.room_details: 
        room_details.append({
            'room_type': room.room_type,
            'rate_type': room.rate_type,
            'rate': room.rate
        })
    return room_details



import frappe
import json
from frappe import _

@frappe.whitelist()
def fetch_clauses(cities):
    # Check and parse if cities is a string representation of a list
    if isinstance(cities, str):
        cities = json.loads(cities)

    # frappe.errprint(f"Cities after parsing: {cities}")

    try:
        clauses = frappe.get_all('Package Clause',
                                 filters={'city': ['in', cities],
                                'type': ['in', ['Exclude', 'Include']]},
                                 fields=['city', 'type', 'description'])

        # frappe.errprint(f"Fetched clauses: {clauses}")

        response = []
        for clause in clauses:
            response.append({
                'city': clause.city,
                'type': clause.type,
                'description': clause.description
            })

        return response

    except Exception as e:
        frappe.log_error(f"Error in fetch_clauses: {str(e)}", "Fetch Clauses Error")
        frappe.throw(_("An error occurred while fetching clauses: {0}").format(str(e)))
        
# @frappe.whitelist()
# def fetch_Opt_clauses(cities):
#     # Check and parse if cities is a string representation of a list
#     if isinstance(cities, str):
#         cities = json.loads(cities)

#     # frappe.errprint(f"Cities after parsing: {cities}")

#     try:
#         clauses = frappe.get_all('Package Clause',
#                                  filters={'city': ['in', cities],
#                                           'type': 'Optional'
#                                           },
#                                  fields=['city', 'type','description','rate'])

#         # frappe.errprint(f"Fetched clauses: {clauses}")

#         response = []
#         for clause in clauses:
#             response.append({
#                 'city': clause.city,
#                 'description': clause.description,
#                 'rate': clause.rate
#             })

#         return response

#     except Exception as e:
#         frappe.log_error(f"Error in fetch_clauses: {str(e)}", "Fetch Clauses Error")
#         frappe.throw(_("An error occurred while fetching clauses: {0}").format(str(e)))
        

@frappe.whitelist()
def get_Itinerary(cities_day, num_of_cities):
    try:
        cities_day = json.loads(cities_day)[0]  
        total_days = cities_day['All']  
        response = []
        itineraries = frappe.get_all('Tour Itinerary',
                                     filters={'day': ['<=', total_days]},
                                     fields=['*'])
        
        for itinerary in itineraries:
            if int(num_of_cities) == 1:
                if itinerary.get('type') != "City-to-City":
                    response.append(itinerary)
            else:
                response.append(itinerary)

        response.sort(key=lambda x: x['day'])
        arrivals = [item for item in response if item.get('type') == "Arrival"]
        departures = [item for item in response if item.get('type') == "Departure"]
        others = [item for item in response if item.get('type') not in ["Arrival", "Departure"]]
        response = arrivals + others + departures
        return response

    except Exception as e:
        frappe.log_error(f"Error in get_Itinerary: {str(e)}", "Get Itinerary Error")
        frappe.throw(_("An error occurred while fetching itinerary: {0}").format(str(e)))


@frappe.whitelist()
def fetch_countries(cities):
    # Check and parse if cities is a string representation of a list
    if isinstance(cities, str):
        cities = json.loads(cities)

    # frappe.errprint(f"Cities after parsing: {cities}")

    try:
        # Fetch countries associated with the given cities
        city_country_pairs = frappe.get_all('City',
                                            filters={'name': ['in', cities]},
                                            fields=['country'])

        # frappe.errprint(f"Fetched city-country pairs: {city_country_pairs}")

        # Use a set to deduplicate countries
        unique_countries = set()
        for pair in city_country_pairs:
            unique_countries.add(pair['country'])

        # Convert the set back to a list of dictionaries for consistency with expected output
        response = [{'country': country} for country in unique_countries]

        return response

    except Exception as e:
        frappe.log_error(f"Error in fetch_countries: {str(e)}", "Fetch Countries Error")
        frappe.throw(_("An error occurred while fetching countries: {0}").format(str(e)))


@frappe.whitelist()
def fetch_country_visa_types(country):
    if not country:
        return []

    visa_types = []
    # Get all entries from "Country visa type" including their names
    visa_type_entries = frappe.get_list("Country visa type", fields=["*"])

    for entry in visa_type_entries:
        # frappe.errprint(f"entry {entry}")
        # Fetch all "Country cdt" entries that are linked to the current "Country visa type"
        countries = frappe.get_all("Country cdt", 
                                    filters={
                                        'parent': entry['name'],
                                        'parenttype': "Country visa type",
                                        'parentfield': "country"
                                    },
                                    fields=["country"])
        # frappe.errprint(f"countries cdt {countries}")
        if any(c['country'] == country for c in countries):
            visa_types.append(entry['visa_type'])

    return visa_types


@frappe.whitelist()
def fetch_visa_details(countryVisaMap):
    if isinstance(countryVisaMap, str):
        countryVisaMap = json.loads(countryVisaMap)

    try:
        response = []

        for country, visa_type in countryVisaMap.items():
            parent_doc = frappe.get_list('Visa Charges and Requirements',
                                         filters={'country': country, 'visa_type': visa_type},
                                         fields=['name', 'country', 'visa_type', 'requirements'])
            if parent_doc:
                parent_doc = parent_doc[0]
                child_docs = frappe.get_all('visa charges cdt',
                                            filters={'parent': parent_doc.name, 'parenttype': 'Visa Charges and Requirements'},
                                            fields=['name1', 'rate_type', 'amount'])
                visa_info = {
                'country': parent_doc.country,
                'visa_type': parent_doc.visa_type,
                'requirements' : parent_doc.requirements,
                'charges': []
                }
                for child in child_docs:
                    visa_info['charges'].append({
                        'name1': child.name1,
                        'rate_type': child.rate_type,
                        'amount': child.amount
                    })
                response.append(visa_info)
            
        return response

    except Exception as e:
        frappe.log_error(f"Error in fetch_visa_details: {str(e)}", "Fetch Visa Details Error")
        frappe.throw(_("An error occurred while fetching visa details: {0}").format(str(e)))
