// Copyright (c) 2025, OsamaASidd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visa Charges and Requirements", {
    country: function(frm) {
        update_visa_type_options(frm);
    },
    onload: function(frm) {
        update_visa_type_options(frm);
    }
});


function update_visa_type_options(frm){
        if (frm.doc.country) {
            frappe.call({
                method: "tourism.tourism.doctype.visa_charges_and_requirements.visa_charges_and_requirements.get_visa_types",
                args: {country: frm.doc.country},
                callback: function(r) {
                    if (r.message) {
                        frm.set_df_property("visa_type", "options", r.message.join("\n"));
                    }
                }
            });
        }
    }
