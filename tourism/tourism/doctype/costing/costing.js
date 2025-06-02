// Copyright (c) 2025, OsamaASidd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Costing', {

    // markup: update_final_totals,
    // final_markup: update_final_totals,
    // staff_cost: update_final_totals,
    // misc: update_final_totals,

    onload: function(frm) {
    if (frm.doc.opportunity) {
        frm.set_value("currency", 'USD');
            if (frm.is_new()) {
                if (frm.doc.hotels && frm.doc.hotels.length === 0) {
                    calculate_pax(frm);
                    create_hotel_rows(frm);
                    fetch_package_clauses(frm);
                    Create_Itinerary(frm);
                }

                if (frm.doc.proposal) {
                    frm.set_value("proposal", null);
                }
            }
        }
        // console.log("on load called");
        // frm.fields_dict['tour_itinerary'].grid.get_field('city').get_query = function(doc, cdt, cdn) {
        //     let cities = [];
        //     if (doc.locations && doc.locations.length > 0) {
        //         cities = doc.locations.map(function(location) {
        //             return location.city_of_stay;
        //         });
        //     }
        //     return {
        //         query: 'tourism.tourism.doctype.costing.GetHotels.get_hotels_based_on_city',
        //         filters: { 
        //             'cities':cities
        //         }
        //     };
        // };

    },

    by_vendor_: function(frm) {
    (frm.doc.tour_itinerary || []).forEach(row => {
        row.amount = 0;
        row.cost = 0;
    });
    const is_by_vendor = frm.doc.by_vendor_ === 1;
    frm.set_df_property('create_itinerary', 'hidden', is_by_vendor);
    frm.refresh_field('tour_itinerary');
    frm.refresh_field('create_itinerary');
},


    onload_post_render: function(frm) {
        bind_hotel_room_type_click_handler(frm);
    },

    validate: function(frm) {
        if (frm.doc.locations.length > 0 && frm.doc.visa_types.length === 0){
            let cities = frm.doc.locations.map(location => location.city_of_stay);
            frappe.call({
                method: "tourism.tourism.doctype.costing.GetHotels.fetch_countries",
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
                method: "tourism.tourism.doctype.costing.GetHotels.fetch_countries",
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

        if (frm.doc.opportunity) {
            frm.add_custom_button(__('Proposal'), function() {
                frappe.call({
                    method: "tourism.tourism.doctype.costing.utils.make_quotation_from_costing",
                    args: {
                        source_name: frm.doc.opportunity,
                        costing_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
            }, __('Create'));
    }

            // console.log("on refresh called");

            // frm.fields_dict['tour_itinerary'].grid.get_field('city').get_query = function(doc, cdt, cdn) {
            //     let cities = [];

            //     if (doc.locations && doc.locations.length > 0) {
            //         cities = doc.locations.map(location => location.city_of_stay).filter(Boolean);
            //     }

            //     return {
            //         filters: [
            //             ['name', 'in', cities]
            //         ]
            //     };
            // };


        if (frm.doc.opportunity) {
            bind_hotel_room_type_click_handler(frm);
        }
        frm.get_field('visa_types').grid.cannot_add_rows = true; 
        frm.fields_dict['hotels'].grid.get_field('hotel').get_query = function(doc, cdt, cdn) {
            let cities = [];
            if (doc.locations && doc.locations.length > 0) {
                cities = doc.locations.map(function(location) {
                    return location.city_of_stay;
                });
            }
            return {
                query: 'tourism.tourism.doctype.costing.GetHotels.get_hotels_based_on_city',
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

frappe.ui.form.on('Costing Hotel cdt', {
    hotel: function(frm, cdt, cdn) {
        set_room_query(frm, cdt, cdn);
        const row = locals[cdt][cdn];
        if (row.city) {
            const matched_location = frm.doc.locations.find(loc => loc.city_of_stay === row.city);
            if (matched_location) {
                frappe.model.set_value(cdt, cdn, 'days', matched_location.day);
            }
        }
    },

    days: function(frm, cdt, cdn) {
        set_room_query(frm, cdt, cdn);
    },

    rate: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const rate = parseFloat(row.rate) || 0;
        const days = parseFloat(row.days) || 0;
        const cost = rate * days;
        frappe.model.set_value(cdt, cdn, 'cost', cost);
        // update_final_totals(frm);
    },

    margin: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const rate = parseFloat(row.rate) || 0;
        const margin = parseFloat(row.margin) || 0;
        const days = parseFloat(row.days) || 0;
        const cost = rate * days * (1 + margin/100);
        frappe.model.set_value(cdt, cdn, 'cost', cost);
        // update_final_totals(frm);
    },

    room_type: function(frm, cdt, cdn) {
        fetch_rate_type_amount(frm, cdt, cdn);
    }
});

frappe.ui.form.on('Costing clause cdt', {
    package_includes_add: function(frm, cdt, cdn){
        // let row = locals[cdt][cdn];
        // console.log(row);
        frappe.model.set_value(cdt, cdn, 'type', 'Include');
        },
    package_excludes_add: function(frm, cdt, cdn){
        // let row = locals[cdt][cdn];
        // console.log(row);
        frappe.model.set_value(cdt, cdn, 'type', 'Exclude');
        },
});

frappe.ui.form.on('Costing Extra cdt', {

    amount: function(frm, cdt, cdn){

        const row = frappe.get_doc(cdt, cdn);

        if (row.amount && row.pax) {
            row.per_person_amount = row.amount /  row.pax;
        }

        frm.refresh_field("extra");
    },

    per_person_amount: function(frm, cdt, cdn){

        const row = frappe.get_doc(cdt, cdn);

        if (row.per_person_amount && row.pax) {
            row.amount = row.per_person_amount * row.pax;
        }

        frm.refresh_field("extra");
    },

    extra_add: function(frm, cdt, cdn){

        const row = frappe.get_doc(cdt, cdn);

        if (frm.doc.pax_quantity) {
            row.pax = frm.doc.pax_quantity;
        }

        frm.refresh_field("extra");
    }
});

frappe.ui.form.on('Costing Itinerary cdt', {
    amount: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const amount = parseFloat(row.amount) || 0;
        const margin = parseFloat(row.margin) || 0;
        const cost = amount * (1 + margin/100);
        frappe.model.set_value(cdt, cdn, 'cost', cost);
        // update_final_totals(frm);
    },

    margin: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const amount = parseFloat(row.amount) || 0;
        const margin = parseFloat(row.margin) || 0;
        const cost = amount * (1 + margin/100);
        frappe.model.set_value(cdt, cdn, 'cost', cost);
        // update_final_totals(frm);
    }
});

frappe.ui.form.on('Package loc visa cdt', {
    country: function(frm, cdt, cdn) {
        set_visa_query(frm, cdt, cdn);
    },
    visa_types_remove: function(frm, cdt, cdn) {
        set_visa_query(frm, cdt, cdn);
    },
});



function set_visa_query(frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.country) {
        frappe.call({
            method: "tourism.tourism.doctype.costing.GetHotels.fetch_country_visa_types",
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
            method: "tourism.tourism.doctype.costing.GetHotels.fetch_hotel_room_details",
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
            method: "tourism.tourism.doctype.costing.GetHotels.fetch_hotel_room_details",
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
        method: "tourism.tourism.doctype.costing.GetHotels.fetch_clauses",
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
                    const new_child = frappe.model.add_child(frm.doc, 'Costing Clause', table);
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
//         method: "tourism.tourism.doctype.costing.GetHotels.fetch_Opt_clauses",
//         args: { cities: cities },
//         callback: function(r) {
//             if (r.message) {

//                 // Clear existing data in child tables
//                 frappe.model.clear_table(frm.doc, 'optional_clauses');

//                 // Populate new data based on fetched clauses
//                 r.message.forEach(clause => {
//                     const table = 'optional_clauses';
//                     const new_child = frappe.model.add_child(frm.doc, 'Costing Optional', table);
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

    // Build a dictionary of city-day pairs
    let cities_day = {};
    let locations = frm.doc.locations || [];

    locations.forEach((location, index) => {
        if (location.city_of_stay) {
            let day = location.day || 0;

            // If it's the last city, add +1 to the day
            if (index === locations.length - 1) {
                day += 1;
            }

            cities_day[location.city_of_stay] = day;
        }
    });

    frappe.call({
        method: "tourism.tourism.doctype.costing.GetHotels.get_Itinerary",
        args: {
            cities_day: JSON.stringify(cities_day)
        },
        callback: function(r) {
            if (r.message) {
                console.log("Fetched Itinerary : ", r.message);

                frappe.model.clear_table(frm.doc, 'tour_itinerary');

                r.message.forEach(clause => {
                    const new_child = frappe.model.add_child(frm.doc, 'Tour Itinerary', 'tour_itinerary');
                    frappe.model.set_value(new_child.doctype, new_child.name, 'day', clause.day);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'city', clause.city);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'type', clause.type);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'description', clause.description);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'amount', clause.amount);
                    frappe.model.set_value(new_child.doctype, new_child.name, 'cost', clause.amount);
                });

                frm.refresh_field('tour_itinerary');
            } else {
                console.log("No itinerary was fetched.");
            }
        }
    });
}



function create_hotel_rows(frm) { 
    let hotels = frm.doc.locations
        .filter(location => location.hotel && location.star) // only keep if both exist
        .map(location => {
            return {
                city: location.city_of_stay,
                hotel: location.hotel,
                star: location.star,
                day: location.day
            };
        });

    // console.log("hotels", hotels);

    if (hotels.length > 0) {
        frm.clear_table('hotels');

        hotels.sort(function(a, b) {
            return a.idx - b.idx;
        });

        hotels.forEach(function(hotel) {
            var child = frm.add_child('hotels');
            frappe.model.set_value(child.doctype, child.name, 'option', 1);
            frappe.model.set_value(child.doctype, child.name, 'hotel', hotel.hotel);
            frappe.model.set_value(child.doctype, child.name, 'star', hotel.star);
            frappe.model.set_value(child.doctype, child.name, 'days', hotel.day);
            frappe.model.set_value(child.doctype, child.name, 'city', hotel.city);
            frappe.model.set_value(child.doctype, child.name, 'onload_', 1);
        });

        frm.refresh_field('hotels');
    }
}

function fetch_visa_details(frm) {
    let countryVisaMap = {};

    frm.doc.visa_types.forEach(function(obj) {
        countryVisaMap[obj.country] = obj.visa_type;
    });

    console.log("countryVisaMap ",countryVisaMap);
    frappe.call({
        method: "tourism.tourism.doctype.costing.GetHotels.fetch_visa_details",
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



function bind_hotel_room_type_click_handler(frm) {
    const grid = frm.fields_dict['hotels'].grid;

    grid.wrapper.off('focus.room_type_click');

    grid.wrapper.on('focus.room_type_click', 'input[data-fieldname="room_type"]', function (e) {
        const $input = $(this);
        const $row = $input.closest('.grid-row');
        const rowname = $row.attr('data-name');

        const row = locals['Costing Hotel cdt'] && locals['Costing Hotel cdt'][rowname];
        // if (!row) {
        //     // console.warn('Row not found:', rowname);
        //     return;
        // }

        if (row.hotel && row.star) {
            frappe.call({
                method: "tourism.tourism.doctype.costing.GetHotels.fetch_hotel_room_details",
                args: {
                    hotel_name: row.hotel,
                    star: row.star
                },
                callback: function (r) {
                    if (r.message) {
                        const grid_row = grid.get_row(rowname);
                        const options = r.message.map(room => room.room_type);
                        grid_row.get_field('room_type').get_query = function () {
                            return {
                                filters: [['name', 'in', options]]
                            };
                        };
                        grid.refresh_row(rowname);
                        setTimeout(() => {
                            if (grid_row.grid_form) {
                                const field = grid_row.grid_form.fields_dict['room_type'];
                                if (field && field.refresh) {
                                    field.refresh(); 
                                }
                            }
                        }, 5); 
                    }
                }
            });
        }
    });
}


function update_final_totals(frm) {
    let grouped = {};

    frm.doc.final.forEach(row => {
        grouped[`${row.option}||${row.room_type}`] = row;
    });

    let extra_total = (frm.doc.extra || []).reduce((acc, row) => acc + (parseFloat(row.amount) || 0), 0);

    const hotel_grouped = {};
    (frm.doc.hotels || []).forEach(hotel => {
        const key = `${hotel.option}||${hotel.room_type}`;
        if (!hotel_grouped[key]) hotel_grouped[key] = [];
        hotel_grouped[key].push(hotel);
    });

    for (let key in grouped) {
        const [option, room_type] = key.split("||");
        const final_row = grouped[key];
        const hotel_rows = hotel_grouped[key] || [];

        let net_cost = hotel_rows.reduce((sum, row) => sum + (parseFloat(row.net_cost) || 0), 0);
        let total_cost = net_cost + extra_total + (parseFloat(frm.doc.markup) || 0);
        let grand_total = total_cost + (parseFloat(frm.doc.final_markup) || 0) + (parseFloat(frm.doc.staff_cost) || 0) + (parseFloat(frm.doc.misc) || 0);

        final_row.net_cost = net_cost;
        final_row.total_cost = total_cost;
        final_row.grand_total = grand_total;
        final_row.total_extra = frm.doc.pax_quantity ? extra_total / frm.doc.pax_quantity : 0;
    }

    frm.refresh_field("final");
}

function calculate_pax(frm) {
    if (!frm.doc.opportunity) return;

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Opportunity",
            name: frm.doc.opportunity
        },
        callback: function(r) {
            if (r.message) {
                const opp = r.message;
                const passengers = parseInt(opp.custom_no_of_passengers) || 0;
                const infants = parseInt(opp.custom_no_of_infants) || 0;
                const children = parseInt(opp.custom_no_of_childs) || 0;

                const total_pax = passengers + infants + children;

                frm.set_value('pax_quantity', total_pax);
            }
        }
    });
}
