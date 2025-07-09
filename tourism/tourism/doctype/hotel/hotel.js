// Copyright (c) 2025, OsamaASidd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotel", {

    onload(frm) {
        if (frm.is_new() && (!frm.doc.room_details || frm.doc.room_details.length === 0)) {
            const room_types = [
                'Single Room',
                'Double/Twin',
                'Child with Extra Bed'
            ];

            room_types.forEach(type => {
                const row = frm.add_child('room_details');
                row.room_type = type;
            });

            frm.refresh_field('room_details');
        }
    },

	refresh(frm) {

	},
});


frappe.ui.form.on('Hotel Detail cdt', {
    room_rate: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);

        if (row.room_type) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Room Type",
                    name: row.room_type
                },
                callback: function(r) {
                    if (r.message) {
                        const room_doc = r.message;
                        if (room_doc.pax_quantity === 0) {
                            frappe.throw(`Room Type "${row.room_type}" has a Pax Quantity of 0. Please update it.`);
                        } else {
                            row.rate = row.room_rate / room_doc.pax_quantity;
                            frm.refresh_field("room_details");
                        }
                    }
                }
            });
        }
    }
});
