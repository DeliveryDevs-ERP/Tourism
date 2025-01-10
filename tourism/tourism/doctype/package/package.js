// Copyright (c) 2025, OsamaASidd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Package', {
    refresh(frm) {
        frm.fields_dict['hotels'].grid.get_field('hotel').get_query = function(doc, cdt, cdn) {
            let cities = [];
            if (doc.locations && doc.locations.length > 0) {
                cities = doc.locations.map(function(location) {
                    return location.city_of_stay;
                });
            }
            return {
                query: 'tourism.tourism.doctype.package.GetHotels.get_hotels_based_on_city',
                filters: { 
                    'cities':cities
                }
            };
        };
    
    },

    fetch_package_clauses: function (frm) {
		fetch_package_clauses(frm);
	},

    fetch_optional_package_clauses: function (frm) {
		fetch_Opt_package_clauses(frm);
	},

    create_itinerary: function (frm) {
		Create_Itinerary(frm);
	},






});

frappe.ui.form.on('Package Hotel cdt', {
    hotel: function(frm, cdt, cdn) {
        set_room_query(frm, cdt, cdn);
    },

    room_type: function(frm, cdt, cdn) {
        fetch_rate_type_amount(frm, cdt, cdn);
    }
});

function set_room_query(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.hotel) {
        frappe.call({
            method: "tourism.tourism.doctype.package.GetHotels.fetch_hotel_room_details",
            args: {
                hotel_name: child.hotel,
                star: child.star
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    // Set query directly within the grid context for 'room_type'
                    var grid_row = frm.fields_dict['hotels'].grid.get_row(cdn);
                    grid_row.get_field('room_type').get_query = function() {
                        return {
                            filters: [
                                ['name', 'in', r.message.map(room => room.room_type)]
                            ]
                        };
                    };
                    // Refresh the field to ensure the new query is applied
                    grid_row.refresh_field('room_type');
                }
            }
        });
    }
}

function fetch_rate_type_amount(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.room_type && child.hotel) {
        frappe.call({
            method: "tourism.tourism.doctype.package.GetHotels.fetch_hotel_room_details",
            args: {
                hotel_name: child.hotel,
                star: child.star
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    // Find the specific room details from the response
                    var room_details = r.message.find(room => room.room_type === child.room_type);
                    if (room_details) {
                        // Update rate_type and rate fields in the child form
                        frappe.model.set_value(cdt, cdn, 'rate_type', room_details.rate_type);
                        frappe.model.set_value(cdt, cdn, 'rate', room_details.rate);
                    }
                }
            }
        });
    }
}


function fetch_package_clauses(frm) {
    let cities = frm.doc.locations.map(location => location.city_of_stay);
    cities.push('All');

    frappe.call({
        method: "tourism.tourism.doctype.package.GetHotels.fetch_clauses",
        args: { cities: cities },
        callback: function(r) {
            if (r.message) {
                // console.log("r.message :",r.message);

                // Clear existing data in child tables
                frappe.model.clear_table(frm.doc, 'package_includes');
                frappe.model.clear_table(frm.doc, 'package_excludes');

                // Populate new data based on fetched clauses
                r.message.forEach(clause => {
                    const table = clause.type === 'Include' ? 'package_includes' : 'package_excludes';
                    const new_child = frappe.model.add_child(frm.doc, 'Package Clause', table);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'city', clause.city);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'type', clause.type);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'description', clause.description);
                });

                frm.refresh_field('package_includes');
                frm.refresh_field('package_excludes');
            }
        }
    });
}



function fetch_Opt_package_clauses(frm) {
    let cities = frm.doc.locations.map(location => location.city_of_stay);
    cities.push('All');

    frappe.call({
        method: "tourism.tourism.doctype.package.GetHotels.fetch_Opt_clauses",
        args: { cities: cities },
        callback: function(r) {
            if (r.message) {

                // Clear existing data in child tables
                frappe.model.clear_table(frm.doc, 'optional_clauses');

                // Populate new data based on fetched clauses
                r.message.forEach(clause => {
                    const table = 'optional_clauses';
                    const new_child = frappe.model.add_child(frm.doc, 'Package Optional', table);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'city', clause.city);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'description', clause.description);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'rate', clause.rate);

                });

                frm.refresh_field('optional_clauses');
            }
        }
    });
}

function Create_Itinerary(frm) {
    let locations = frm.doc.locations;
    let total_days = 0;
    locations.forEach(location => {
        total_days += location.day; // Correct use of accumulating total days
    });

    // Properly declaring and using the array with a dictionary for total days
    let cities_day = [{ 'All': total_days }]; // Correct initialization and assignment

    let num_of_cities = locations.length;

    // JSON.stringify is applied correctly to cities_day now
    frappe.call({
        method: "tourism.tourism.doctype.package.GetHotels.get_Itinerary",
        args: {
            cities_day: JSON.stringify(cities_day), // Ensure cities_day is an array of objects
            num_of_cities: num_of_cities
        },
        callback: function(r) {
            if (r.message) {
                console.log("Fetched Itinerary : ", r.message);

                // Clear existing data in child tables
                frappe.model.clear_table(frm.doc, 'tour_itinerary');

                // Populate new data based on fetched clauses
                r.message.forEach(clause => {
                    const table = 'tour_itinerary';
                    const new_child = frappe.model.add_child(frm.doc, 'Tour Itinerary', table);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'day', clause.day);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'city', clause.city);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'type', clause.type);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'description', clause.description);
                });

                frm.refresh_field('tour_itinerary');

            } else {
                console.log("No itinerary was fetched.");
            }
        }
    });
}
