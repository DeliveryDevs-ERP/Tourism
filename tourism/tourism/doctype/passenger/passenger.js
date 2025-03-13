frappe.ui.form.on("Passenger", {
    refresh(frm) {
        if (!frm.doc.first_name) {
            frm.add_custom_button(__('Scan Passport'), function() {
                const passportAttachment = frm.doc.attachments.find(attachment => attachment.attachment_type === "Passport");
                
                if (passportAttachment && passportAttachment.attachment) {
                    frappe.call({
                        method: 'ocr.ocr.doctype.file_manager.file_manager.scan_passport',
                        args: {
                            file_url: passportAttachment.attachment
                        },
                        callback: function(r) {
                            if (r.message) {
                                frm.set_value('first_name', r.message.first_name);
                                frm.set_value('last_name', r.message.last_name);
                                frm.set_value('passport_number', r.message.passport_number);
                                frm.set_value('cnic', r.message.cnic);
                                frm.set_value('date_of_birth', r.message.date_of_birth);
                                frm.set_value('nationality', r.message.nationality);
                                frm.set_value('passport_expire_date', r.message.date_of_expiry);
                                frm.set_value('gender', r.message.sex === 'M' ? 'Male' : 'Female'); 

                                frm.refresh_field('first_name');
                                frm.refresh_field('last_name');
                                frm.refresh_field('passport_number');
                                frm.refresh_field('cnic');
                                frm.refresh_field('nationality');
                                frm.refresh_field('date_of_birth');
                                frm.refresh_field('passport_expire_date');
                                frm.refresh_field('gender');

                                frappe.msgprint(__('Passport scanned successfully.'));
                            }
                        },
                        error: function(r) {
                            frappe.msgprint(__('Error scanning passport. Please try again.'));
                        }
                    });
                } else {
                    frappe.msgprint(__('No passport attachment found. Please attach a passport before scanning.'));
                }
            });
        }

    },
});
