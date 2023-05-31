# Copyright (c) 2022, itsdave and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from its_charging.evse_api import evse_wallbox
from datetime import datetime, timedelta
from frappe import DuplicateEntryError


class Wallbox(Document):

	@frappe.whitelist()
	def get_log(self):
		wb = evse_wallbox(self.endpoint_url,"","")
		log = wb.get_log()
		for entry in log:
			print(entry)
			#skip entrys which are still in progress:
			if "rEnd" in entry.keys():
				continue
			#calculate costs for charging process
			costs = entry["price"] * entry["energy"] / 100
			#get start datetime from timestamp
			charging_start = datetime.fromtimestamp(entry["timestamp"])
			#validate charging_start, and replace it if its greate then now
			replaced_charging_start = None
			if charging_start >= datetime.now():
				print(charging_start)
				replaced_charging_start = datetime.now()
			#validate Duration and set to max int, if larger
			if entry["duration"] > 2147483647:
				entry["duration"] = 2147483647
			#calculate charging_end
			charging_end = charging_start + timedelta(seconds = entry["duration"] / 1000)
			#calculate average charging speed
			average_charging_speed = entry["energy"] / (entry["duration"] / 1000 / 60 / 60) if entry["duration"] != 0 else 0
			#get rfid tag for linking
			rfid_tag = self.insert_rfid(entry["uid"], entry["username"])
			#Prepare doctype meta data
			meta = {"doctype": "Charging Process",
					"wallbox": self.name,
					"wallbox_mac": self.mac,
					"wb_timestamp": entry["timestamp"],
					"costs": costs,
					"charging_start": charging_start,
					"replaced_charging_start": replaced_charging_start,
					"charging_end": charging_end,
					"average_charging_speed": average_charging_speed,
					"rfid_tag": rfid_tag.name,
					"licence_plate": rfid_tag.licence_plate}
			
			if rfid_tag.employee:
				meta["employee"] = rfid_tag.employee
			
			if rfid_tag.vehicle:
				meta["vehicle"] = rfid_tag.vehicle
			
			cp = frappe.get_doc(**meta, **entry)
			try:
				cp.save()
			except DuplicateEntryError:
				continue
	
	@frappe.whitelist()
	def get_evse(self):
		wb = evse_wallbox(self.endpoint_url,"","")
		hi = wb.get_evse()
		for k in hi.keys():
			setattr(self, str(k).lower(), hi[k])
		self.save()

	@frappe.whitelist()
	def get_parameters(self):
		wb = evse_wallbox(self.endpoint_url,"","")
		hi = wb.get_parameters()
		for k in hi.keys():
			setattr(self, str(k).lower(), hi[k])
		self.save()
	
	def insert_rfid(self, rfid, username):
		rfids = frappe.get_all("RFID Tag", filters = {"rfid": rfid})
		if not rfids:
			rfid_doc = frappe.get_doc({
				"doctype": "RFID Tag",
				"rfid": rfid,
				"username": username})
			rfid_doc.insert()
			return rfid_doc
		else:
			return frappe.get_doc("RFID Tag", rfids[0]["name"])
		
