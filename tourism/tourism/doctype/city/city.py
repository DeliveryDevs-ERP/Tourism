# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class City(Document):
    def before_save(self):
        """Keep Airport.attached_city in sync with self.airports."""
        self._sync_airports_attached_city()

    def on_trash(self):
        """If the city is deleted, clear attached_city from all linked airports."""
        for row in (self.airports or []):
            if row.airport:
                # only clear if it's pointing to this city
                if frappe.db.get_value("Airport", row.airport, "attached_city") == self.name:
                    frappe.db.set_value("Airport", row.airport, "attached_city", None, update_modified=False)

    def _sync_airports_attached_city(self):
        """Set attached_city for current rows; clear it for removed rows."""
        current_airports = {r.airport for r in (self.airports or []) if r.airport}

        # previous doc state (None on insert)
        prev_doc = self.get_doc_before_save()
        prev_airports = set()
        if prev_doc:
            prev_airports = {r.airport for r in (prev_doc.airports or []) if r.airport}

        # Airports newly added or still present -> ensure attached_city = this city
        for ap in current_airports:
            frappe.db.set_value("Airport", ap, "attached_city", self.name, update_modified=False)

        # Airports removed since last save -> clear if they still point to this city
        removed = prev_airports - current_airports
        for ap in removed:
            if frappe.db.get_value("Airport", ap, "attached_city") == self.name:
                frappe.db.set_value("Airport", ap, "attached_city", None, update_modified=False)
