# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Costing(Document):
    
    def validate(self):
        self.calculate_GT()
        self.calculate_Final()

    def calculate_GT(self):
        total_extra_cost = sum(row.amount or 0 for row in self.extra)
        total_optional_cost = sum(row.amount or 0 for row in self.optional)

        for hotel_row in self.hotels:
            hotel_city = hotel_row.city

            city_itinerary_cost = sum(
                row.cost or 0 for row in self.tour_itinerary if row.city == hotel_city
            )

            net_total = city_itinerary_cost
            row_cost = hotel_row.cost or 0
            hotel_row.net_cost = net_total + row_cost

    def calculate_Final(self):
        from collections import defaultdict

        grouped_hotels = defaultdict(list)
        for row in self.hotels:
            key = (row.option, row.room_type)
            grouped_hotels[key].append(row)

        total_extra_cost = sum(row.amount or 0 for row in self.extra)
        self.set("final", [])

        for (option, room_type), hotel_rows in grouped_hotels.items():
            total_net_cost = sum(row.net_cost or 0 for row in hotel_rows)

            total_cost = total_net_cost + total_extra_cost + (self.markup or 0)
            grand_total = total_cost + (self.misc or 0) + (self.staff_cost or 0) + (self.final_markup or 0)
            
            hotel_names = ", ".join(filter(None, [row.hotel for row in hotel_rows]))
            stars = ", ".join(filter(None, [row.star for row in hotel_rows]))
            hotel_item = frappe.get_value("Hotel",row.hotel,"item_id")
   
            new_row = self.append("final", {})
            new_row.option = option
            new_row.room_type = room_type
            new_row.hotels = hotel_names
            new_row.stars = stars
            if self.pax_quantity:
                new_row.total_extra = total_extra_cost/ self.pax_quantity
            else:
                new_row.total_extra = 0
                
            new_row.net_cost = total_net_cost
            new_row.item = hotel_item
            new_row.uom = row.rate_type
            new_row.total_cost = total_cost
            new_row.grand_total = grand_total
