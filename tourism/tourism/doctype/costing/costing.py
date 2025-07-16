# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Costing(Document):
    
    def validate(self):
        # Commented for client req for allowing hotel rate in by vendor tick
        # if self.by_vendor_:
        #     for row in self.hotels:
        #         row.rate = 0
        #         row.cost = 0
        iterary_sum = sum(row.cost or 0 for row in self.tour_itinerary)
        # if iterary_sum == 0 and not self.by_vendor_:
        #     # frappe.msgprint("WARNING: Iternary cost sum is 0")
        total_cities = len(self.locations)
        vendor_sum = sum(row.amount or 0 for row in self.vendor_cost)
        # if vendor_sum == 0 and self.by_vendor_:
        #     # frappe.msgprint("WARNING: Vendor cost sum is 0")
            
        self.calculate_GT(iterary_sum, total_cities)
        self.calculate_Final()

    def calculate_GT(self, iterary_sum, total_cities): 
        total_extra_cost = sum(row.amount or 0 for row in self.extra)
        total_optional_cost = sum(row.amount or 0 for row in self.optional)

        for hotel_row in self.hotels:
            hotel_city = hotel_row.city
            hotel_room_type = hotel_row.room_type
            city_itinerary_cost = 0
            hotel_sum = 0  # added for client req for allowing hotel rate in by vendor tick
            if not self.by_vendor_:
                city_itinerary_cost = sum(
                row.cost or 0 for row in self.tour_itinerary if row.city == hotel_city
                )
                net_total = city_itinerary_cost
                row_cost = hotel_row.cost or 0
                hotel_row.net_cost = net_total + row_cost
            else:
                # city_itinerary_cost = sum(row.amount or 0 for row in self.vendor_cost if row.city == hotel_city) + sum( row.cost or 0 for row in self.tour_itinerary if row.city == hotel_city)
                # per city room type rate = vendor room type wise cost / city count + iterary_sum / city count
                # matching against room type then allot net_total
                hotel_sum += hotel_row.cost if hotel_row.cost else 0 # added for client req for allowing hotel rate in by vendor tick
                room_type_rate = (sum(row.amount or 0 for row in self.vendor_cost if row.room_type == hotel_room_type) / total_cities) + (iterary_sum / total_cities)
                hotel_row.net_cost =  room_type_rate
        hotel_row.net_cost = hotel_row.net_cost + hotel_sum  # added for client req for allowing hotel rate in by vendor tick

    def calculate_Final(self):
        from collections import defaultdict

        grouped_hotels = defaultdict(list)
        for row in self.hotels:
            key = (row.option, row.room_type)
            grouped_hotels[key].append(row)
        if len(self.extra) > 0:
            total_extra_cost = sum(row.per_person_amount or 0 for row in self.extra)
        else:
            total_extra_cost = 0
        self.set("final", [])

        for (option, room_type), hotel_rows in grouped_hotels.items():
            total_net_cost = sum(row.net_cost or 0 for row in hotel_rows)
            total_hotel_cost = sum(row.cost or 0 for row in hotel_rows) # sum of hotel_cost after group by

            total_cost = total_net_cost + total_extra_cost
            grand_total = total_cost + (self.final_markup or 0)
            
            hotel_names = ", ".join(filter(None, [row.hotel for row in hotel_rows]))
            stars = ", ".join(filter(None, [row.star for row in hotel_rows]))
            hotel_item = frappe.get_value("Hotel",row.hotel,"item_id")
   
            new_row = self.append("final", {})
            new_row.option = option
            new_row.room_type = room_type
            new_row.hotels = hotel_names
            new_row.stars = stars
            if self.pax_quantity:
                new_row.total_extra = total_extra_cost
            else:
                new_row.total_extra = 0
                
            new_row.net_cost = total_net_cost
            new_row.total_hotel = total_hotel_cost
            new_row.total_itinerary = total_net_cost - total_hotel_cost
            new_row.item = hotel_item
            new_row.uom = row.rate_type
            new_row.total_cost = total_cost
            new_row.grand_total = grand_total

    def on_trash(self):
        frappe.delete_doc("Costing", self.name, ignore_permissions=True, ignore_missing=True, force=True, ignore_on_trash=True, ignore_links=True)
