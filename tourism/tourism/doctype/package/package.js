// Copyright (c) 2025, OsamaASidd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Package', {

    validate: function(frm) {
        if (frm.doc.locations.length > 0 && frm.doc.visa_types.length === 0){
            let cities = frm.doc.locations.map(location => location.city_of_stay);
            frappe.call({
                method: "tourism.tourism.doctype.package.GetHotels.fetch_countries",
                args: { cities: cities },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.clear_table(frm.doc, 'visa_types');
        
                        r.message.forEach(clause => {
                            const new_child = frappe.model.add_child(frm.doc, visa_types);
                            frappe.model.set_value(new_child.doctype, new_child.name, 'country', clause.country);
                        });
        
                        frm.refresh_field('visa_types');
                    }
                }
            });
        }
        else if (frm.doc.locations.length > 0 && frm.doc.visa_types.length > 0){
            let cities = frm.doc.locations.map(location => location.city_of_stay);
            frappe.call({
                method: "tourism.tourism.doctype.package.GetHotels.fetch_countries",
                args: { cities: cities },
                callback: function(r) {
                    if (r.message) {
                        // Extract existing countries in the visa_types table to avoid duplicates
                        let existingCountries = frm.doc.visa_types.map(row => row.country);
        
                        r.message.forEach(clause => {
                            // Check if the country is already in the table
                            if (!existingCountries.includes(clause.country)) {
                                const new_child = frappe.model.add_child(frm.doc, 'visa_types');
                                frappe.model.set_value(new_child.doctype, new_child.name, 'country', clause.country);
                            }
                        });
        
                        frm.refresh_field('visa_types');
                    }
                }
            });
        }
    },


    refresh(frm) {
        frm.get_field('visa_types').grid.cannot_add_rows = true; 
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

    // fetch_optional_package_clauses: function (frm) {
	// 	fetch_Opt_package_clauses(frm);
	// },

    create_itinerary: function (frm) {
		Create_Itinerary(frm);
	},

    fetch_visa_requirements: function (frm) {
		fetch_visa_details(frm);
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

frappe.ui.form.on('Package loc visa cdt', {
    country: function(frm, cdt, cdn) {
        // console.log("Country Trigger");
        set_visa_query(frm, cdt, cdn);
    },
    visa_types_remove: function(frm, cdt, cdn) {
        // console.log("Country Trigger");
        set_visa_query(frm, cdt, cdn);
    },

});



function set_visa_query(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.country) {
        frappe.call({
            method: "tourism.tourism.doctype.package.GetHotels.fetch_country_visa_types",
            args: {
                country: child.country,
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    // Parse the response to get just the visa types as an array of strings
                    var visa_types = r.message.map(function(item) { return item; });

                    // Use the update_docfield_property method to set the options for the visa_type field in the visa_types grid
                    frm.fields_dict['visa_types'].grid.update_docfield_property('visa_type', 'options', [""].concat(visa_types));

                    frm.refresh_field('visa_types');
                }
            }
        });
    }
}



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



// function fetch_Opt_package_clauses(frm) {
//     let cities = frm.doc.locations.map(location => location.city_of_stay);
//     cities.push('All');

//     frappe.call({
//         method: "tourism.tourism.doctype.package.GetHotels.fetch_Opt_clauses",
//         args: { cities: cities },
//         callback: function(r) {
//             if (r.message) {

//                 // Clear existing data in child tables
//                 frappe.model.clear_table(frm.doc, 'optional_clauses');

//                 // Populate new data based on fetched clauses
//                 r.message.forEach(clause => {
//                     const table = 'optional_clauses';
//                     const new_child = frappe.model.add_child(frm.doc, 'Package Optional', table);
//                     frappe.model.set_value(new_child.doctype, new_child.name, 'city', clause.city);
//                     frappe.model.set_value(new_child.doctype, new_child.name, 'description', clause.description);
//                     frappe.model.set_value(new_child.doctype, new_child.name, 'rate', clause.rate);

//                 });

//                 frm.refresh_field('optional_clauses');
//             }
//         }
//     });
// }

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



function fetch_visa_details(frm) {
    let countryVisaMap = {};

    frm.doc.visa_types.forEach(function(obj) {
        countryVisaMap[obj.country] = obj.visa_type;
    });

    console.log("countryVisaMap ",countryVisaMap);
    frappe.call({
        method: "tourism.tourism.doctype.package.GetHotels.fetch_visa_details",
        args: { countryVisaMap: countryVisaMap },
        callback: function(r) {
            if (r.message) {
                console.log("r.message :",r.message);

                frappe.model.clear_table(frm.doc, 'requirements');
                frappe.model.clear_table(frm.doc, 'charges');

                r.message.forEach(Obj => {
                    // console.log("Obj ", Obj);
                    
                    // Add a single row for country, visa_type, and requirements
                    let req_row = frm.add_child("requirements");
                    req_row.country = Obj.country;
                    req_row.visa_type = Obj.visa_type;
                    req_row.requirements = Obj.requirements;
                    
                    // Add multiple rows for each charge
                    Obj.charges.forEach(charge => {
                        let charge_row = frm.add_child("charges");
                        charge_row.country = Obj.country
                        charge_row.type = charge.name1;
                        charge_row.rate_type = charge.rate_type;
                        charge_row.amount = charge.amount;
                    });
                });

                frm.refresh_field('requirements');
                frm.refresh_field('charges');
            }
        }
    });
}