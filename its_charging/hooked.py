import frappe

def fetch_data():
    settings = frappe.get_single("Its Charging Settings")
    if settings.enable_background_fetch:
        print("Fetching wallbox data.")
        wbs = frappe.get_all("Wallbox", filters= {"fetch_data": 1})
        for wb in wbs:
            print("processing " + wb["name"])
            wb_doc = frappe.get_doc("Wallbox", wb["name"])
            wb_doc.get_log()
            frappe.db.commit()
    else:
        print("Background fetching wallbox data is diabled.")
