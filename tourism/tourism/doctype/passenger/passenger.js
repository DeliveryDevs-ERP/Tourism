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
                                const parsed = r.message[0];
                                const raw_text = r.message[1];

                                frm.set_value('first_name', parsed.first_name);
                                frm.set_value('last_name', parsed.last_name);
                                frm.set_value('passport_number', parsed.passport_number);
                                frm.set_value('cnic', parsed.cnic);
                                frm.set_value('date_of_birth', parsed.date_of_birth);
                                frm.set_value('nationality', parsed.nationality);
                                frm.set_value('passport_expire_date', parsed.date_of_expiry);
                                frm.set_value('gender', parsed.sex === 'M' ? 'Male' : 'Female'); 
                                frm.set_value('text', raw_text); 
                                frm.refresh_fields();

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
