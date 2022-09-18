# Copyright (c) 2022, itsdave and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import pytz
import requests
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth

class IstChargingFunc(Document):
	@frappe.whitelist()
	def get_request(self,url,end):

		#wb_password = self.get_password('password')
		#self.auth = HTTPBasicAuth(password)
		reg_url = url+end
		response = requests.get(reg_url)
		# response.raise_for_status()
		# session = requests.Session()
		# session.auth = HTTPDigestAuth(password)
		#print(response.text)
		return response.json()
	
	@frappe.whitelist()
	def get_data(self):
		wallbox_list = frappe.get_all("Wallbox")
		for el in wallbox_list:
			wallbox_doc = frappe.get_doc("Wallbox",el["name"])
			url = wallbox_doc.endpoint_url
			end = "getLog"
			wallbox_name = wallbox_doc.name
			data = self.get_request(url,end)
			for el in data["list"]:

				date = datetime.fromtimestamp(el["timestamp"])-timedelta(hours=1)
				print(date)

				duration = timedelta(milliseconds =el["duration"])
				energy = el["energy"]
				costs = round(el["price"]*el["energy"]/100,2)
				print(date,duration,costs)
				logfile_list = frappe.get_all("Charging process", filters={"date": date})
				if not logfile_list:

					logfile_doc = frappe.get_doc({
							"doctype": "Charging process",
							"user": el["username"],
							"user_id" : el["uid"],
							"date": date,
							"duration": duration,
							"energy" : energy,
							"costs" : costs,
							"wallbox_name": wallbox_name
							})
					logfile_doc.save()
		
	@frappe.whitelist()
	def get_wallbox(self):
		
		wallbox_list = frappe.get_all("Wallbox")
		print(wallbox_list)
		for el in wallbox_list:
			wallbox_doc = frappe.get_doc("Wallbox",el["name"])
			url = wallbox_doc.endpoint_url
			end = "getParameters"
			parameters = self.get_request(url,end)
			print(parameters["list"])
			if parameters["list"][0]["vehicleState"] == 1:
				veh_st = "ready"
			elif parameters["list"][0]["vehicleState"] == 2:
				veh_st = "Vehicle detected"
			elif parameters["list"][0]["vehicleState"] == 3:
				veh_st = "Vehicle charging"
			elif parameters["list"][0]["vehicleState"] == 5:
				veh_st = "Error"
			if parameters["list"][0]["evseState"] == True:
				evse_st = "Charging station unlocked"
			elif parameters["list"][0]["evseState"] == False:
				evse_st = "Charging station locked"
			
			wallbox_doc.vehicle_state = veh_st
			wallbox_doc.evse_state = evse_st
			wallbox_doc.duration = timedelta(milliseconds =parameters["list"][0]["duration"])
			wallbox_doc.max_current = parameters["list"][0]["maxCurrent"]
			wallbox_doc.actual_current_in_a = parameters["list"][0]["actualCurrent"]
			wallbox_doc.actual_power = parameters["list"][0]["actualPower"]
			wallbox_doc.always_active =  parameters["list"][0]["alwaysActive"]
			wallbox_doc.last_action_user = parameters["list"][0]["lastActionUser"]
			wallbox_doc.last_action_uid = parameters["list"][0]["lastActionUID"]
			wallbox_doc.energy = parameters["list"][0]["energy"]
			wallbox_doc.mileage = parameters["list"][0]["mileage"]
			wallbox_doc.meter_reading = parameters["list"][0]["meterReading"]
			wallbox_doc.save()
		
		
		 				
		
		

	 	


		

	


