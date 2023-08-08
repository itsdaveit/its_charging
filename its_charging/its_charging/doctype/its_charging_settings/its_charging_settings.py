# Copyright (c) 2022, itsdave and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class ItsChargingSettings(Document):

	@frappe.whitelist()
	def apply_price_calculation_to_all_processes(self):
		charging_processes = frappe.get_all('Charging Process')

		for process in charging_processes:
			try:
				self.calculate_price_for_process(process.name)

			except Exception as e:
				print(f"Fehler bei der Preisberechnung für Prozess {process.name}: {str(e)}")
			

	
	@frappe.whitelist()
	def calculate_price_for_process(self,doc):
		#doc = "CHRGP-C4:4F:33:7F:A6:01-2085987809"
		cp = frappe.get_doc("Charging Process", doc )
		t_s = cp.wb_timestamp
		rfid_tag = cp.rfid_tag
		print(cp.price)
		print(cp.wb_timestamp)
		dt_object = datetime.fromtimestamp(t_s).date()
		print(dt_object)
		wallbox = cp.wallbox
		print(wallbox)
		wallbox_group_list = [x.name for x in frappe.get_all('Wallbox Group')]
		print(wallbox_group_list)
		wallbox_group = ""
		for el in wallbox_group_list:
			wb_exists_dict = self.check_wallbox_in_group(el,wallbox)
			if wb_exists_dict["exists"]:
				wallbox_group = wb_exists_dict["group"]
		print(wallbox_group)
		rfid_tag =cp.rfid_tag 
		rfid_group_list = [x.name for x in frappe.get_all('Wallbox RFID Group')]
		rfid_group = ""
		for el in rfid_group_list:
			rfid_exists_dict = self.check_rfid_tag_in_group(el,rfid_tag)
			if rfid_exists_dict["exists"]:
				rfid_group = rfid_exists_dict["group"]
		print(rfid_group)

		price = get_price(dt_object,wallbox_group, rfid_group )
		print(price)
		print(price*100)
		cp.price = round(price * 100,0)
		cp.costs = round(price*cp.energy,2)
		cp.save()
		frappe.db.commit()
	
	

	@frappe.whitelist()
	def check_wallbox_in_group(self,wallbox_group, wallbox):
		exists = False
		group_name = None
		wallbox_group_doc = frappe.get_doc("Wallbox Group", wallbox_group)
		wallbox_group_boxes = wallbox_group_doc.wallbox
		wb_list = [x.wallboxes for x in wallbox_group_boxes]
		print(wb_list)	
		if wallbox_group_doc and wallbox in wb_list:
			print(wallbox_group_doc, wallbox_group_doc.wallbox)
			exists = True
			group_name = wallbox_group_doc.name
		exists_dict = {"exists": exists, "group": group_name}
		return exists_dict
	
	@frappe.whitelist()
	def check_rfid_tag_in_group(self,rfid_tag_group, rfid_tag):
		exists = False
		group_name = None

		rfid_tag_group_doc = frappe.get_doc("Wallbox RFID Group", rfid_tag_group)
		rfid_tags = rfid_tag_group_doc.wallbox_rfids
		rft_list = [x.rfid_tags for x in rfid_tags]
		print(rft_list)	
		if rfid_tag_group_doc and rfid_tag in rft_list:
			exists = True
			group_name = rfid_tag_group_doc.name
		exists_dict = {"exists": exists, "group": group_name}
		return exists_dict
	
def get_price(date, wallbox_group, rfid_group):
#Suche nach Preisdefinitionen basierend auf dem Zeitraum
	print(date)
	valid_from_condition = ('<=', date)

	# Abfrage für Einträge mit 'valid_to' größer oder gleich 'date'
	valid_to_condition = ('>=', date)
	valid_to_price_list = frappe.get_all('Energy Price',
										filters={'valid_from': valid_from_condition,
												'valid_to': valid_to_condition})

	# Abfrage für Einträge ohne 'valid_to'
	valid_to_empty_price_list = frappe.get_all('Energy Price',
											filters={'valid_from':valid_from_condition,
														'valid_to': ("is", "not set")})

	# Kombiniere die Ergebnisse beider Abfragen
	price_list = valid_to_price_list + valid_to_empty_price_list

	print(price_list)
	if not price_list:
		# Wenn keine Preisliste gefunden wurde, gebe einen Fehler aus
		raise ValueError('Keine Preisliste gefunden')

	if len(price_list) == 1:
		price_list_doc = frappe.get_doc('Energy Price', price_list[0]['name'])
		price = price_list_doc.cost
	else:
		price = None
		for el in price_list:
			wallbox_groups = price_list_doc.wallbox_groups
			rfid_groups = price_list_doc.rfid_groups
			wb_list = [x.wallbox_groups for x in wallbox_groups]
			rfid_list = [x.wallbox_rfid_groups for x in rfid_groups]
			if wallbox_group in wb_list and rfid_group in rfid_list:
				price = price_list_doc.cost
				break

	if price is None:
		raise ValueError('Keine eindeutige Zuordnung zu einer Preisliste möglich')

	return price



# def get_price(date, wallbox_group, rfid_group):
#     #Suche nach Preisdefinitionen basierend auf dem Zeitraum
# 	print(date)
# 	valid_from_condition = ('<=', date)

# 	# Abfrage für Einträge mit 'valid_to' größer oder gleich 'date'
# 	valid_to_condition = ('>=', date)
# 	valid_to_price_list = frappe.get_all('Energy Price',
# 										filters={'valid_from': valid_from_condition,
# 											'valid_to': valid_to_condition})

# 	# Abfrage für Einträge ohne 'valid_to'
# 	valid_to_empty_price_list = frappe.get_all('Energy Price',
# 											filters={'valid_from':valid_from_condition,
# 												'valid_to': ("is", "not set")})

# 	# Kombiniere die Ergebnisse beider Abfragen
# 	price_list = valid_to_price_list + valid_to_empty_price_list
		
# 	print(price_list)
# 	if not price_list:
#         # Wenn keine Preisliste gefunden wurde, gebe einen Fehler aus
# 		raise ValueError('Keine Preisliste gefunden')
	
# 	if len(price_list) == 1:
# 		for el in price_list:
# 			price_list_doc = frappe.get_doc('Energy Price', el)
# 			wallbox_groups = price_list_doc.wallbox_groups
# 			wb_list = [x.wallbox_groups for x in wallbox_groups]
# 			rfid_groups = price_list_doc.rfid_groups
# 			rfid_list = [x.wallbox_rfid_groups for x in rfid_groups]
# 			if wallbox_group in wb_list and rfid_group in rfid_list:
# 				price = price_list_doc.cost
# 			else:
# 				raise ValueError('Keine eindeutige Zuordnung zu einer Preisliste möglich')
			

# 	price_list_name = price_list[0]['name']

#     # Suche nach dem Preis basierend auf der Preisliste, dem Datum und der Gruppe
# 	price = frappe.get_doc('Energy Price', price_list_name).cost
                                            
# 	if not price:
#         # Wenn kein Preis gefunden wurde, gebe einen Fehler aus oder handle es entsprechend
# 		raise ValueError('Kein Preis gefunden')

# 	return price

# # Beispielaufruf der Funktion
# start_date = '2023-06-01'
# end_date = '2023-06-30'
# customer_group = 'VIP Customers'

# try:
#     price = get_price(start_date, end_date, customer_group)
#     print('Der Preis beträgt:', price)
# except ValueError as e:
#     print('Fehler:', str(e))
