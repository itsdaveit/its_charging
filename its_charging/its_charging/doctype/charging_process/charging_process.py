# Copyright (c) 2022, itsdave and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ChargingProcess(Document):
	def autoname(self):
		self.name = "CHRGP-" + str(self.wallbox_mac) + "-" + str(self.wb_timestamp)
