import frappe


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
        
@frappe.whitelist()
def fetch_Opt_clauses(cities):
    # Check and parse if cities is a string representation of a list
    if isinstance(cities, str):
        cities = json.loads(cities)

    # frappe.errprint(f"Cities after parsing: {cities}")

    try:
        clauses = frappe.get_all('Package Clause',
                                 filters={'city': ['in', cities],
                                          'type': 'Optional'
                                          },
                                 fields=['city', 'type','description','rate'])

        # frappe.errprint(f"Fetched clauses: {clauses}")

        response = []
        for clause in clauses:
            response.append({
                'city': clause.city,
                'description': clause.description,
                'rate': clause.rate
            })

        return response

    except Exception as e:
        frappe.log_error(f"Error in fetch_clauses: {str(e)}", "Fetch Clauses Error")
        frappe.throw(_("An error occurred while fetching clauses: {0}").format(str(e)))
        
                
import json
import frappe
from frappe import _


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
