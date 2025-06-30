# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Passenger(Document):
    def validate(self):
        names = [self.first_name.strip() if self.first_name else ""]

        if self.middle_name:
            names.append(self.middle_name.strip())

        if self.last_name:
            names.append(self.last_name.strip())

        self.full_name = " ".join(names)
        
        if self.passport_number:
            self.full_name_pass = self.full_name + " | " + self.passport_number
        else:
            self.full_name_pass = self.full_name