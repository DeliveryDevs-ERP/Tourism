# Copyright (c) 2025, OsamaASidd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Costing(Document):
	
	def validate(self):
		self.calculate_GT()

	def calculate_GT(self):
		total_itinerary_cost = sum(row.cost or 0 for row in self.tour_itinerary)
		total_extra_cost = sum(row.amount or 0 for row in self.extra)
		total_optional_cost = sum(row.amount or 0 for row in self.optional)

		net_total = total_itinerary_cost + total_extra_cost + total_optional_cost

		for hotel_row in self.hotels:
			row_cost = hotel_row.cost or 0
			hotel_row.net_cost = net_total + row_cost
			hotel_row.total_cost = hotel_row.net_cost + self.markup
			hotel_row.grand_total = hotel_row.total_cost + self.misc + self.staff_cost + self.final_markup

   
