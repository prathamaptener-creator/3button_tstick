# import requests
# import json
# import datetime
# import sqlite3
# from enum import Enum
# import logging
# import os
# import csv
# from flask import Flask,request,jsonify
# from dotenv import load_dotenv
# import websocket

# load_dotenv(dotenv_path='development.env')

# API_KEY = os.getenv("api_key")
# API_SECRET = os.getenv("api_secret")
# ERP_EMPLOYEE_URL =os.getenv("employee_url")
# ERP_ITEM_URL = os.getenv("item_url")
# ERP_JOB_CARD_URL = os.getenv("job_card_url")
# ERP_DATA_LOG=os.getenv("data_log_url")
# ERP_DASHBOARD_URL = os.getenv("dashborad_url")
# ERP_PASS=os.getenv("erp_pass")
# app = Flask(__name__)
# DB_FILE="c20_Button1.db"
# PASS_COUNT_FILE = "pass_count.json"
# HEADERS = {
# 	"Authorization": f"token {API_KEY}:{API_SECRET}",
# 	"Content-Type": "application/json",
# }

# def init_db():
# 	try:
# 		logging.info("Initializing database...")
# 		start_time = datetime.datetime.now()
# 		with sqlite3.connect(DB_FILE) as conn:
# 			cursor = conn.cursor()
# 			cursor.execute("""
# 				CREATE TABLE IF NOT EXISTS job_card_pass (
# 					id INTEGER PRIMARY KEY AUTOINCREMENT,
# 					device_serial_number TEXT,
# 				  	batch TEXT,
# 					employee_id TEXT,
# 					job_card_id TEXT,
# 					qc_system TEXT,
# 					system TEXT,
# 					status TEXT,
# 				  	dips TEXT,
# 					timestamp TEXT
# 				)
# 			""")
# 			cursor.execute("""
# 				CREATE TABLE IF NOT EXISTS job_card_fail (
# 					id INTEGER PRIMARY KEY AUTOINCREMENT,
# 					device_serial_number TEXT,
# 					batch TEXT,
# 					employee_id TEXT,
# 					job_card_id TEXT,
# 					qc_system TEXT,
# 					system TEXT,
# 					issue TEXT,
# 					status TEXT,
# 					dips TEXT,
# 					timestamp TEXT
# 				)
# 			""")
# 			conn.commit()
# 		end_time = datetime.datetime.now()
# 		logging.info(f"Database initialized successfully. Time taken: {end_time - start_time}")
# 	except Exception as e:
# 		logging.error(f"Error initializing database: {e}")
        
# def fetch_employees():
# 	employees = []
# 	page = 1
# 	page_size = 50  # adjust if needed

# 	try:
# 		# logging.info("📡 Fetching employees from ERP...")
# 		start_time = datetime.datetime.now()

# 		while True:
# 			url = f"{ERP_EMPLOYEE_URL}?fields=[\"name\", \"employee_name\"]&limit_page_length={page_size}&limit_start={(page - 1) * page_size}"
# 			response = requests.get(url, headers=HEADERS)

# 			if response.status_code == 200:
# 				data = response.json().get("data", [])
# 				# logging.info(f"🔍 Page {page} → {len(data)} employees fetched")

# 				if not data:
# 					# logging.info("No more data available. Ending fetch process.")
# 					break

# 				employees.extend(data)
# 				page += 1
# 			else:
# 				logging.error(f"❌ Error: {response.status_code} - {response.text}")
# 				break

# 		if employees:
# 			# Save to local JSON
# 			try:
# 				with open("employees.json", "w") as f:
# 					json.dump(employees, f)
# 				logging.info(f"✅ Fetched total {len(employees)} employees from ERP and saved to 'employees.json'.")
# 			except Exception as e:
# 				logging.error(f"❌ Error saving employees to JSON: {e}")
# 		else:
# 			# Try local fallback
# 			try:
# 				with open("employees.json", "r") as f:
# 					employees = json.load(f)
# 				logging.info("📂 Loaded employees from local 'employees.json' file.")
# 			except Exception as e:
# 				logging.error("❌ No employee data found in ERP or local file.")
# 				logging.error(f"❌ Error loading employees from local file: {e}")

# 		end_time = datetime.datetime.now()
# 		logging.info(f"⏱️ Time taken for fetching employees: {end_time - start_time}")

# 		# Return in format: EMP001 - John Doe
# 		return [f'{emp["name"]}' for emp in employees]

# 	except Exception as e:
# 		logging.error(f"❌ Exception during fetch_employees: {e}")
# 		return []

# def is_valid_employee(employee_id):
# 	try:
# 		with open('employees.json', 'r') as file:
# 			employees = json.load(file)  # Load the data from the JSON file
# 		for employee in employees:
# 			if employee['name'].startswith(employee_id):
# 				value= employee['name']
# 		logging.warning(f"Invalid employee ID: {employee_id}")
# 		return value
# 	except Exception as e:
# 		logging.error(f"Error reading employee data: {e}")
# 		return False
# def log_to_csv(filename, data_row):
# 	"""
# 	Logs data to a CSV file. If the file does not exist, it creates one with headers.

# 	Args:
# 		filename (str): Name of the CSV file.
# 		data_row (list): List containing the row data to write.
# 	"""
# 	file_exists = os.path.isfile(filename)
# 	try:
# 		with open(filename, mode="a", newline="") as file:
# 			writer = csv.writer(file)

# 			# Write headers if the file does not exist
# 			if not file_exists:
# 				writer.writerow(["Serial Number", "Employee ID", "System", "Status", "Issue", "Timestamp"])

# 			writer.writerow(data_row)

# 		logging.info(f"✅ Logged data to CSV: {data_row}")

# 	except Exception as e:
# 		logging.error(f"⚠️ Error logging to CSV: {e}")
# # 🔹 Fetch Job Card for Employee & Production Item
# def fetch_job_card_for_employee(employee, production_item):
# 	try:
# 		logging.info(f"📦 Fetching Job Card for Employee: {employee}, Production Item: {production_item}")
# 		start_time = datetime.datetime.now()

# 		# Step 1: Search for matching job cards
# 		job_card_url = f'{ERP_JOB_CARD_URL}/api/resource/Job Card'
# 		filters = {
# 			"custom_employee_": employee,
# 			"production_item": production_item,
# 			"status": ["in", ["Open", "Work In Progress"]]
# 		}
# 		params = {"filters": json.dumps(filters)}

# 		response = requests.get(job_card_url, headers=HEADERS, params=params)
# 		if response.status_code != 200:
# 			logging.error(f"❌ Failed to fetch Job Card list. Status: {response.status_code}, Response: {response.text}")
# 			return None

# 		job_cards = response.json().get("data", [])
# 		if not job_cards:
# 			logging.warning(f"⚠️ No active Job Card found for Employee: {employee}, Production Item: {production_item}")
# 			return None

# 		# Step 2: Extract job card ID and get full details
# 		job_card_id = job_cards[0].get("name")
# 		full_url = f'{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card_id}'
# 		full_response = requests.get(full_url, headers=HEADERS)
# 		if full_response.status_code != 200:
# 			logging.error(f"❌ Failed to fetch full Job Card data. Status: {full_response.status_code}")
# 			return None

# 		job_card_data = full_response.json().get("data", {})
# 		job_card_status = job_card_data.get("status")

# 		# Fallback: if status is missing, use docstatus
# 		if not job_card_status:
# 			docstatus = job_card_data.get("docstatus")
# 			if docstatus == 0:
# 				job_card_status = "Open"
# 			elif docstatus == 1:
# 				job_card_status = "Submitted"
# 			elif docstatus == 2:
# 				job_card_status = "Cancelled"
# 			else:
# 				job_card_status = "Unknown"

# 		logging.info(f"✅ Found Job Card: {job_card_id} with status: {job_card_status} for Employee: {employee}")
# 		print(f"✅ Found Job Card: {job_card_id} with status: {job_card_status} for Employee: {employee}")
# 		# Step 3: If status is Open, start the job card
# 		if job_card_status == "Open":
# 			start_result = start_jobcard(employee, job_card_id)
# 			if not start_result.get("success"):
# 				logging.error(f"❌ Failed to start Job Card: {start_result.get('error')}")
# 				return None
# 			logging.info(f"🚀 Job Card {job_card_id} started successfully (WIP)")

# 		else:
# 			logging.info(f"ℹ️ Job Card {job_card_id} already in status '{job_card_status}', skipping start.")

# 		logging.info(f"🕒 fetch_job_card_for_employee completed in {datetime.datetime.now() - start_time} seconds.")
# 		return job_card_id

# 	except Exception as e:
# 		logging.error(f"⚠️ Exception in fetch_job_card_for_employee: {e}")
# 		return None


# def start_jobcard(employee_id, job_card):
# 	"""
# 	Start a job card for the given employee

# 	Args:
# 		job_card (str): Job card ID
# 		employee_id (str): Employee ID

# 	Returns:
# 		dict: Result with success/error status
# 	"""
# 	print(employee_id)

# 	try:
# 		url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
# 		response = requests.get(url, headers=HEADERS)

# 		if response.status_code != 200:
# 			return {"error": "Job Card not found", "status_code": 404}

# 		job_data = response.json().get("data", {})
# 		time_logs = job_data.get("time_logs", [])

# 		if not time_logs:
# 			new_time_log = {
# 				"employee": employee_id,
# 				"from_time": datetime.datetime.now().isoformat(),
# 				"completed_qty": 0
# 			}
# 			time_logs = [new_time_log]
# 		else:
# 			time_logs[0]["from_time"] = datetime.datetime.now().isoformat()

# 		payload = {
# 			"status": "Work In Progress",
# 			"time_logs": time_logs
# 		}

# 		update_url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
# 		put_response = requests.put(update_url, headers=HEADERS, json=payload)

# 		if put_response.status_code == 200:
# 			# ✅ Set initial pass count to 0 in JSON
            
# 			return {"message": "Job Card started successfully!", "success": True}
# 		else:
# 			return {"error": put_response.text, "status_code": 500, "success": False}

# 	except Exception as e:
# 		return {"error": str(e), "success": False} 
# # class System(Enum):
# #     Programming1="halobitProgramming1"
# #     Programming2="halobitProgramming2"
# #     preFunctionality1="halobitPreFunctionality1"
# #     preFunctionality2="halobitPreFunctionality2"
# #     mapping1="halobitMapping1"
# #     funtionality1="halobitFunctionality1"
# #     functionality2="halobitFunctionality2"
# #     button="halobitButton"
# #     photobooth1="halobitPhotobooth1"
# #     photobooth2="haloitPhotobooth2"


# def retry_records():
# 	"""Retries sending 'pass' and 'fail' records from the database to ERPNext."""
# 	try:
# 		logging.info("🔄 Starting retry process for pending records...")
# 		start_time = datetime.datetime.now()

# 		with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
# 			cursor = conn.cursor()

# 			# 1️⃣ Process "Pass" Records
# 			cursor.execute("""
# 				SELECT device_serial_number,batch,job_card_id, employee_id,qc_system, system, status,dips, timestamp 
# 				FROM job_card_pass 
# 				WHERE status = 'pass' AND job_card_id IS NOT NULL
# 			""")
# 			pass_records = cursor.fetchall()
# 			logging.info(f"📄 Found {len(pass_records)} pending 'pass' records to process.")

# 			for record in pass_records:
# 				serial_number, batch,job_card_id, employee_id,qc_system, system, status,dips, timestamp = record
# 				current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 				payload = {
# 					"device_serialnumber": serial_number,
# 					"batch":batch,
# 					"job_card_id": job_card_id,
# 					"employee_name": employee_id,
# 					"qc_system": qc_system,
# 					"system":system,
# 					"status": status,
# 					"date": current_timestamp,
# 					"button_status":json.loads(dips) if dips else {}
# 				}

# 				response = requests.post(ERP_PASS, json=payload, headers=HEADERS)
# 				print("response",response)
# 				if response.status_code == 200:
# 					cursor.execute("UPDATE job_card_pass SET status = 'pass-send' WHERE device_serial_number = ?", (serial_number,))
# 					conn.commit()

# 					# ✅ Log "Pass" records to CSV (No issue details)
# 					log_to_csv("job_card_pass_log.csv", [serial_number, employee_id, system, status, "", "", timestamp])

# 					logging.info(f"✅ Successfully sent pass record for Serial: {serial_number}")
# 				else:
# 					logging.error(f"❌ Failed to send pass record {serial_number}. Status: {response.status_code}, Response: {response.text}")

# 			# 2️⃣ Process "Fail" Records
# 			# Process "Fail" Records
# 		cursor.execute("""
# 			SELECT serial_number, batch, issue, employee_id, job_card_id,
# 				qc_system,system, status, dips, timestamp
# 			FROM job_card_fail
# 			WHERE status = 'fail'
# 		""")

# 		fail_records = cursor.fetchall()
# 		logging.info(f"📄 Found {len(fail_records)} pending 'fail' records to process.")

# 		for record in fail_records:
# 				serial_number, batch,issue,job_card_id, employee_id,qc_system,system, status,dips, timestamp = record
# 				current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 				payload = {
# 					"device_serialnumber": serial_number,
# 					"batch": batch,
# 					"issue": issue,
# 					"job_card": job_card_id,
# 					"employee": employee_id,
# 					"qc_system":qc_system,
# 					"system": system,
# 					"status": status,
# 					"button_status": dips or "",
# 					"date": current_timestamp,
# 				}

# 				response = requests.post(ERP_DASHBOARD_URL, json=payload, headers=HEADERS)
# 				print("response",response)
# 				if response.status_code == 200:
# 					cursor.execute("UPDATE job_card_fail SET status = 'fail-send' WHERE device_serial_number = ?", (serial_number,))
# 					conn.commit()

# 						# ✅ Log "Fail" records to CSV (No issue details)
# 					log_to_csv("job_card_fail_log.csv", [serial_number, employee_id,qc_system,system, status, "", "", timestamp])

# 					logging.info(f"✅ Successfully sent fail record for Serial: {serial_number}")
# 				else:
# 					logging.error(f"❌ Failed to send fail record {serial_number}. Status: {response.status_code}, Response: {response.text}")


# 	except Exception as e:
# 		logging.error(f"⚠️ Critical error in retry_records function: {e}")
        
# def is_duplicate(serial_number):
# 	with sqlite3.connect(DB_FILE) as conn:
# 		cursor = conn.cursor()
# 		cursor.execute("""
# 				SELECT COUNT(*) FROM job_card_pass 
# 				WHERE device_serial_number = ?
# 			""", (serial_number,))
            
# 		count = cursor.fetchone()[0]
# 		return count > 0 

# def insert_pass_record(device_serial_number,batch,employee_id,job_card_id,dips):
    
# 	if not employee_id or not job_card_id:
# 		print("❌ Error: Employee ID or Job Card ID is missing. Set them first using /save_ids.")
# 		return False
# 	serial_number=device_serial_number
# 	qc_system="MWAVEX2Button"
# 	system="MWAVEX2Button"
# 	status="pass"
    
# 	try:
# 		timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 		with sqlite3.connect(DB_FILE) as conn:
# 			cursor = conn.cursor()
# 			cursor.execute("""
# 				INSERT INTO job_card_pass (device_serial_number,batch, employee_id, job_card_id,qc_system, system, status,dips, timestamp) 
# 				VALUES (?, ?, ?, ?, ?, ?,?,?,?)
# 			""", (serial_number,batch, employee_id, job_card_id,qc_system, system, status,json.dumps(dips), timestamp))
# 			conn.commit()
# 		print(f"✅ Data Inserted into job_card_pass: {serial_number}, {employee_id}, {job_card_id}")
# 		retry_records()
# 		return True
# 	except Exception as e:
# 		print(f"❌ Error inserting pass record: {e}")
# 		return False



# def insert_fail_record(device_serial_number, batch, employee_id, job_card_id, dips):
# 	"""Insert fail record with clean DIP extraction, proper fail logic, and correct DB insert."""

# 	if not employee_id or not job_card_id:
# 		print("❌ Error: Employee ID or Job Card ID is missing.")
# 		return False

# 	system = "MWAVEX2ButtonDisplacement"
# 	status = "fail"

# 	# -------------------------------
# 	# 1️⃣ Normalize DIP values safely
# 	# -------------------------------
# 	def get_dip(key):
# 		v = dips.get(key)
# 		if isinstance(v, list):
# 			return v[0] if v else None
# 		return v

# 	right_dip  = get_dip("right")
# 	centre_dip = get_dip("centre") or get_dip("center")  # support both spellings
# 	left_dip   = get_dip("left")
# 	tstick_dip=get_dip("tstick")
# 	joystick_dip=get_dip("joystick")

# 	# -------------------------------
# 	# 2️⃣ Apply correct FAIL rules
# 	# -------------------------------
# 	issue = None
# 	failed_key = None
# 	failed_value = None

# 	# Right PASS range: 18–22 N → FAIL outside this range
# 	if right_dip is not None and not (5 <= right_dip <= 13):
# 		issue = "Right Button Failed"
# 		failed_key = "right"
# 		failed_value = right_dip

# 	# Centre PASS range: 6–8 N
# 	elif centre_dip is not None and not (5 <= centre_dip <= 13):
# 		issue = "Centre Button Failed"
# 		failed_key = "centre"
# 		failed_value = centre_dip

# 	# Left PASS range: 18–22 N
# 	elif left_dip is not None and not (5 <= left_dip <= 13):
# 		issue = "Left Button Failed"
# 		failed_key = "left"
# 		failed_value = left_dip
        
# 	elif tstick_dip is not None and not (5 <= left_dip <= 13):
# 		issue = "Tstick Button Failed"
# 		failed_key = "left"
# 		failed_value = tstick_dip
        
# 	elif joystick_dip is not None and not (5 <= left_dip <= 13):
# 		issue = "Joystick Button Failed"
# 		failed_key = "left"
# 		failed_value = joystick_dip

# 	else:
# 		issue = "Unknown Button Failure"
# 		failed_key = "unknown"
# 		failed_value = dips  # store full dips

# 	# -------------------------------
# 	# 3️⃣ Store dips cleanly
# 	# -------------------------------
# 	dips_json = f"Dip: {failed_value}"

# 	# -------------------------------
# 	# 4️⃣ Insert into SQLite
# 	# -------------------------------
# 	try:
# 		timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 		with sqlite3.connect(DB_FILE) as conn:
# 			cursor = conn.cursor()

# 			cursor.execute("""
# 				INSERT INTO job_card_fail
# 				(device_serial_number, batch, employee_id, job_card_id, system, issue, status, dips, timestamp)
# 				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
# 			""", (
# 				device_serial_number,
# 				batch,
# 				employee_id,
# 				job_card_id,
# 				system,
# 				issue,
# 				status,
# 				dips_json,
# 				timestamp
# 			))

# 			conn.commit()

# 		print(f"❌ FAIL RECORDED → {device_serial_number} | {issue} | DIP = {failed_value}")
# 		retry_records()
# 		return True

# 	except Exception as e:
# 		print(f"❌ Error inserting fail record: {e}")
# 		return False


# def increment_pass_count(employee_id, job_card_id):
# 	try:
# 		count = 0
# 		data = {}
# 		key = f"{employee_id}-{job_card_id}"

# 		if os.path.exists(PASS_COUNT_FILE):
# 			with open(PASS_COUNT_FILE, "r") as f:
# 				data = json.load(f)
# 				count = data.get(key, 0)

# 		count += 1
# 		data[key] = count

# 		with open(PASS_COUNT_FILE, "w") as f:
# 			json.dump(data, f, indent=4)

# 		return count

# 	except Exception as e:
# 		print(f"Error incrementing count: {e}")
# 		return 0
    
# def clear_pass_count(employee_id, job_card_id):
# 	try:
# 		if not os.path.exists(PASS_COUNT_FILE):
# 			return

# 		with open(PASS_COUNT_FILE, "r") as f:
# 			data = json.load(f)

# 		key = f"{employee_id}-{job_card_id}"
# 		if key in data:
# 			data[key] = 0

# 		with open(PASS_COUNT_FILE, "w") as f:
# 			json.dump(data, f, indent=4)

# 	except Exception as e:
# 		print(f"Error clearing count: {e}")

# def get_pass_count(employee_id, job_card_id):
# 	try:
# 		if not os.path.exists(PASS_COUNT_FILE):
# 			return 0

# 		with open(PASS_COUNT_FILE, "r") as f:
# 			data = json.load(f)

# 		key = f"{employee_id}-{job_card_id}"
# 		return data.get(key, 0)
# 	except Exception as e:
# 		print(f"Error getting count: {e}")
# 		return 0

# def check_serial(serial_number): 
#     server_url = "ws://192.168.0.200:8050"

#     try:
#         ws = websocket.create_connection(server_url)
#         print("Connected to WebSocket server (Fetch Data)")

#         message = {
#             "type": "sleepcurrent",
#             "serial": serial_number
#         }
#         ws.send(json.dumps(message))

#         response = ws.recv()
#         print(response)
#         ws.close()
#         print("Connection closed\n")

       
#         data = json.loads(response)
#         print(data)

        
#         if data.get("status") == "success" :
#             first_entry = data["data"][0]  
#             batch = first_entry.get("batch")
#             if batch:
#                 return batch

#             else:
#                 print("BATCH not found in response.")
#         else:
#             print("Unexpected or error response:", data)

#     except Exception as e:
#         print(f"Error fetching data for serial '{serial_number}':", e)
# def send_jig_pass(employee,qc_system, dips, status):
#     print("🚀 Sending jig calibration to ERP")

#     payload = {
#         "data": {
#             "calibrate_by": employee,
#             "values": json.dumps(dips),
#             "qc_system":qc_system,
#             "calibration_status": status
#         }
#     }

#     print("➡️ URL:", JIG_PASS)
#     print("📦 Payload:", json.dumps(payload, indent=2))

#     try:
#         response = requests.post(
#             JIG_PASS,
#             headers=HEADERS,
#             json=payload,
#             timeout=10
#         )

#         print("📡 Status:", response.status_code)
#         print("📨 Response:", response.text)

#         return response.status_code in (200, 201)

#     except Exception as e:
#         print("❌ ERP Exception:", e)
#         return False




import requests
import json
import datetime
import sqlite3
from enum import Enum
import logging
import os
import csv
from flask import Flask,request,jsonify
from dotenv import load_dotenv
import websocket

load_dotenv(dotenv_path='development.env')

API_KEY = os.getenv("api_key")
API_SECRET = os.getenv("api_secret")
ERP_EMPLOYEE_URL =os.getenv("employee_url")
ERP_ITEM_URL = os.getenv("item_url")
ERP_JOB_CARD_URL = os.getenv("job_card_url")
ERP_DATA_LOG=os.getenv("data_log_url")
ERP_DASHBOARD_URL = os.getenv("dashborad_url")
ERP_PASS=os.getenv("erp_pass")
ERP_NOVA=os.getenv("erp_nova")
JIG_PASS=os.getenv("jig_pass")
app = Flask(__name__)
DB_FILE="c20_Button1.db"
PASS_COUNT_FILE = "pass_count.json"
HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
}
def filter_dips_by_model(model, dips):

    if model == "BUTTON":
        return {
            "right": dips.get("right"),
            "centre": dips.get("centre"),
            "left": dips.get("left")
        }

    elif model == "TSTICK":
        return {
            "tstick": dips.get("tstick"),
            "joystick": dips.get("joystick")
        }

    elif model in ["BUTTONPLUS", "BUTTONPRO"]:
        return dips

    return dips
def init_db():
    try:
        logging.info("Initializing database...")
        start_time = datetime.datetime.now()
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_card_pass (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_serial_number TEXT,
                    model TEXT,
                    batch TEXT,
                    employee_id TEXT,
                    job_card_id TEXT,
                    qc_system TEXT,
                    system TEXT,
                    status TEXT,
                    dips TEXT,
                    timestamp TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_card_fail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_serial_number TEXT,
                    model TEXT,
                    batch TEXT,
                    employee_id TEXT,
                    job_card_id TEXT,
                    qc_system TEXT,
                    system TEXT,
                    issue TEXT,
                    status TEXT,
                    dips TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()
        end_time = datetime.datetime.now()
        logging.info(f"Database initialized successfully. Time taken: {end_time - start_time}")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        
def fetch_employees():
    employees = []
    page = 1
    page_size = 50  # adjust if needed

    try:
        # logging.info("📡 Fetching employees from ERP...")
        start_time = datetime.datetime.now()

        while True:
            url = f"{ERP_EMPLOYEE_URL}?fields=[\"name\", \"employee_name\"]&limit_page_length={page_size}&limit_start={(page - 1) * page_size}"
            response = requests.get(url, headers=HEADERS)

            if response.status_code == 200:
                data = response.json().get("data", [])
                # logging.info(f"🔍 Page {page} → {len(data)} employees fetched")

                if not data:
                    # logging.info("No more data available. Ending fetch process.")
                    break

                employees.extend(data)
                page += 1
            else:
                logging.error(f"❌ Error: {response.status_code} - {response.text}")
                break

        if employees:
            # Save to local JSON
            try:
                with open("employees.json", "w") as f:
                    json.dump(employees, f)
                logging.info(f"✅ Fetched total {len(employees)} employees from ERP and saved to 'employees.json'.")
            except Exception as e:
                logging.error(f"❌ Error saving employees to JSON: {e}")
        else:
            # Try local fallback
            try:
                with open("employees.json", "r") as f:
                    employees = json.load(f)
                logging.info("📂 Loaded employees from local 'employees.json' file.")
            except Exception as e:
                logging.error("❌ No employee data found in ERP or local file.")
                logging.error(f"❌ Error loading employees from local file: {e}")

        end_time = datetime.datetime.now()
        logging.info(f"⏱️ Time taken for fetching employees: {end_time - start_time}")

        # Return in format: EMP001 - John Doe
        return [f'{emp["name"]}' for emp in employees]

    except Exception as e:
        logging.error(f"❌ Exception during fetch_employees: {e}")
        return []

def is_valid_employee(employee_id):
    try:
        with open('employees.json', 'r') as file:
            employees = json.load(file)  # Load the data from the JSON file
        for employee in employees:
            if employee['name'].startswith(employee_id):
                value= employee['name']
        logging.warning(f"Invalid employee ID: {employee_id}")
        return value
    except Exception as e:
        logging.error(f"Error reading employee data: {e}")
        return False
def log_to_csv(filename, data_row):
    """
    Logs data to a CSV file. If the file does not exist, it creates one with headers.

    Args:
        filename (str): Name of the CSV file.
        data_row (list): List containing the row data to write.
    """
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Write headers if the file does not exist
            if not file_exists:
                writer.writerow(["Serial Number", "Employee ID", "System", "Status", "Issue", "Timestamp"])

            writer.writerow(data_row)

        logging.info(f"✅ Logged data to CSV: {data_row}")

    except Exception as e:
        logging.error(f"⚠️ Error logging to CSV: {e}")
# 🔹 Fetch Job Card for Employee & Production Item
def fetch_job_card_for_employee(employee, production_item):
    try:
        logging.info(f"📦 Fetching Job Card for Employee: {employee}, Production Item: {production_item}")
        start_time = datetime.datetime.now()

        # Step 1: Search for matching job cards
        job_card_url = f'{ERP_JOB_CARD_URL}/api/resource/Job Card'
        filters = {
            "custom_employee_": employee,
            "production_item": production_item,
            "status": ["in", ["Open", "Work In Progress"]]
        }
        params = {"filters": json.dumps(filters)}

        response = requests.get(job_card_url, headers=HEADERS, params=params)
        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch Job Card list. Status: {response.status_code}, Response: {response.text}")
            return None

        job_cards = response.json().get("data", [])
        if not job_cards:
            logging.warning(f"⚠️ No active Job Card found for Employee: {employee}, Production Item: {production_item}")
            return None

        # Step 2: Extract job card ID and get full details
        job_card_id = job_cards[0].get("name")
        full_url = f'{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card_id}'
        full_response = requests.get(full_url, headers=HEADERS)
        if full_response.status_code != 200:
            logging.error(f"❌ Failed to fetch full Job Card data. Status: {full_response.status_code}")
            return None

        job_card_data = full_response.json().get("data", {})
        job_card_status = job_card_data.get("status")

        # Fallback: if status is missing, use docstatus
        if not job_card_status:
            docstatus = job_card_data.get("docstatus")
            if docstatus == 0:
                job_card_status = "Open"
            elif docstatus == 1:
                job_card_status = "Submitted"
            elif docstatus == 2:
                job_card_status = "Cancelled"
            else:
                job_card_status = "Unknown"

        logging.info(f"✅ Found Job Card: {job_card_id} with status: {job_card_status} for Employee: {employee}")
        print(f"✅ Found Job Card: {job_card_id} with status: {job_card_status} for Employee: {employee}")
        # Step 3: If status is Open, start the job card
        if job_card_status == "Open":
            start_result = start_jobcard(employee, job_card_id)
            if not start_result.get("success"):
                logging.error(f"❌ Failed to start Job Card: {start_result.get('error')}")
                return None
            logging.info(f"🚀 Job Card {job_card_id} started successfully (WIP)")

        else:
            logging.info(f"ℹ️ Job Card {job_card_id} already in status '{job_card_status}', skipping start.")

        logging.info(f"🕒 fetch_job_card_for_employee completed in {datetime.datetime.now() - start_time} seconds.")
        return job_card_id

    except Exception as e:
        logging.error(f"⚠️ Exception in fetch_job_card_for_employee: {e}")
        return None


def start_jobcard(employee_id, job_card):
    """
    Start a job card for the given employee

    Args:
        job_card (str): Job card ID
        employee_id (str): Employee ID

    Returns:
        dict: Result with success/error status
    """
    print(employee_id)

    try:
        url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            return {"error": "Job Card not found", "status_code": 404}

        job_data = response.json().get("data", {})
        time_logs = job_data.get("time_logs", [])

        if not time_logs:
            new_time_log = {
                "employee": employee_id,
                "from_time": datetime.datetime.now().isoformat(),
                "completed_qty": 0
            }
            time_logs = [new_time_log]
        else:
            time_logs[0]["from_time"] = datetime.datetime.now().isoformat()

        payload = {
            "status": "Work In Progress",
            "time_logs": time_logs
        }

        update_url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
        put_response = requests.put(update_url, headers=HEADERS, json=payload)

        if put_response.status_code == 200:
            # ✅ Set initial pass count to 0 in JSON
            
            return {"message": "Job Card started successfully!", "success": True}
        else:
            return {"error": put_response.text, "status_code": 500, "success": False}

    except Exception as e:
        return {"error": str(e), "success": False} 
# class System(Enum):
#     Programming1="halobitProgramming1"
#     Programming2="halobitProgramming2"
#     preFunctionality1="halobitPreFunctionality1"
#     preFunctionality2="halobitPreFunctionality2"
#     mapping1="halobitMapping1"
#     funtionality1="halobitFunctionality1"
#     functionality2="halobitFunctionality2"
#     button="halobitButton"
#     photobooth1="halobitPhotobooth1"
#     photobooth2="haloitPhotobooth2"


def retry_records():
    return True
    """Retries sending 'pass' and 'fail' records from the database to ERPNext."""
    try:
        logging.info("🔄 Starting retry process for pending records...")
        start_time = datetime.datetime.now()

        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
            cursor = conn.cursor()

            # 1️⃣ Process "Pass" Records
            cursor.execute("""
                SELECT device_serial_number,model,batch,job_card_id, employee_id,qc_system, system, status,dips, timestamp 
                FROM job_card_pass 
                WHERE status = 'pass' AND job_card_id IS NOT NULL
            """)
            pass_records = cursor.fetchall()
            logging.info(f"📄 Found {len(pass_records)} pending 'pass' records to process.")

            for record in pass_records:
                serial_number,model, batch,job_card_id, employee_id,qc_system, system, status,dips, timestamp = record
                current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if model == "BUTTON":
                    payload = {
                        "3_button_serialnumber": serial_number,
                        "model":model,
                        "batch":batch,
                        "job_card_id": job_card_id,
                        "employee_name": employee_id,
                        "qc_system": qc_system,
                        "system":system,
                        "status": status,
                        "date": current_timestamp,
                        "button_status":dips or "",
                    }
                elif model == "TSTICK":
                    payload = {
                        "t_stick_serialnumber": serial_number,
                        "model":model,
                        "batch":batch,
                        "job_card_id": job_card_id,
                        "employee_name": employee_id,
                        "qc_system": qc_system,
                        "system":system,
                        "status": status,
                        "date": current_timestamp,
                        "button_status":dips or "",
                    }
                response = requests.post(ERP_PASS, json=payload, headers=HEADERS)
                print("response",response)
                if response.status_code == 200:
                    cursor.execute("UPDATE job_card_pass SET status = 'pass-send' WHERE device_serial_number = ?", (serial_number,))
                    conn.commit()

                    # ✅ Log "Pass" records to CSV (No issue details)
                    log_to_csv("job_card_pass_log.csv", [serial_number, employee_id, system, status, "", "", timestamp])

                    logging.info(f"✅ Successfully sent pass record for Serial: {serial_number}")
                else:
                    logging.error(f"❌ Failed to send pass record {serial_number}. Status: {response.status_code}, Response: {response.text}")

            # 2️⃣ Process "Fail" Records
            # Process "Fail" Records
        cursor.execute("""
            SELECT device_serial_number,model, batch, issue, employee_id, job_card_id,
                qc_system,system, status, dips, timestamp
            FROM job_card_fail
            WHERE status = 'fail'
        """)

        fail_records = cursor.fetchall()
        logging.info(f"📄 Found {len(fail_records)} pending 'fail' records to process.")

       
        for record in fail_records:

            serial_number, model, batch, issue, job_card_id, employee_id, qc_system, system, status, dips, timestamp = record

            current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # =====================================================
            # SERIAL FIELD BASED ON MODEL
            # =====================================================

            if model == "TSTICK":
                serial_payload = {
                    "t_stick_serialnumber": serial_number
                }

            else:
                # BUTTON / BUTTONPLUS / BUTTONPRO etc.
                serial_payload = {
                    "3_button_serialnumber": serial_number
                }

            # =====================================================
            # ERP FAIL PAYLOAD
            # =====================================================

            payload = {
                **serial_payload,
                "model": model,
                "batch": batch,
                "issue": issue,
                "job_card": job_card_id,
                "employee": employee_id,
                "qc_system": qc_system,
                "system": system,
                "status": status,
                "button_status": dips,
                "date": current_timestamp,
            }

            response = requests.post(
                ERP_DASHBOARD_URL,
                json=payload,
                headers=HEADERS
            )

            print("response", response)

            if response.status_code == 200:

                cursor.execute(
                    "UPDATE job_card_fail SET status = 'fail-send' "
                    "WHERE device_serial_number = ?",
                    (serial_number,)
                )

                conn.commit()

                log_to_csv(
                    "job_card_fail_log.csv",
                    [
                        serial_number,
                        employee_id,
                        qc_system,
                        system,
                        status,
                        "",
                        "",
                        timestamp
                    ]
                )

                logging.info(
                    f"✅ Successfully sent fail record for Serial: {serial_number}"
                )

            else:

                logging.error(
                    f"❌ Failed to send fail record {serial_number}. "
                    f"Status: {response.status_code}, "
                    f"Response: {response.text}"
                )


    except Exception as e:
        logging.error(f"⚠️ Critical error in retry_records function: {e}")
        
def is_duplicate(serial_number):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT COUNT(*) FROM job_card_pass 
                WHERE device_serial_number = ?
            """, (serial_number,))
            
        count = cursor.fetchone()[0]
        return count > 0 

def insert_pass_record(device_serial_number,model,batch,employee_id,job_card_id,dips):
    
    if not employee_id or not job_card_id:
        print("❌ Error: Employee ID or Job Card ID is missing. Set them first using /save_ids.")
        return False
    serial_number=device_serial_number
    status="pass"
    
    model= model.strip()
    if model == "BUTTON":
        system="3BUTTONButtonDisplacement"
        qc_system="CASSINI"
    elif model == "TSTICK":
        system="TSTICKButtonDisplacement"
        qc_system="CASSINI"
    elif model =="BUTTONPLUS":
        system="BUTTONPlusButtonDisplacement"
        qc_system="MARS"
    elif model == "BUTTONPRO":
        system="BUTTONProButtonDisplacement"
        qc_system="MARS"
    else:
         raise ValueError(f"❌ Unsupported model_name: {model}")


    
    # system="c50ProButton"
    # qc_system="c50ProButton1"
   
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            dips=filter_dips_by_model(model,dips)
            cursor.execute("""
                INSERT INTO job_card_pass (device_serial_number,model,batch, employee_id, job_card_id,qc_system, system, status,dips, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?,?,?,?,?)
            """, (serial_number,model,batch, employee_id, job_card_id,qc_system, system, status,json.dumps(dips), timestamp))
            conn.commit()
        print(f"✅ Data Inserted into job_card_pass: {serial_number}, {employee_id}, {job_card_id}")
        retry_records()
        return True
    except Exception as e:
        print(f"❌ Error inserting pass record: {e}")
        return False



# def insert_fail_record(device_serial_number, model, batch,
#                        employee_id, job_card_id, dips):

#     if not employee_id or not job_card_id:
#         print("❌ Error: Employee ID or Job Card ID is missing.")
#         return False

#     model = model.strip()
#     status = "fail"

#     if model == "BUTTON":
#         system = "BUTTONButtonDisplacement"
#         qc_system = "BUTTONFamilyBDTJ01"
#     elif model == "BUTTONPLUS":
#         system = "BUTTONPlusButtonDisplacement"
#         qc_system = "BUTTONFamilyBDTJ01"
#     elif model == "BUTTONPRO":
#         system = "BUTTONProButtonDisplacement"
#         qc_system = "BUTTONFamilyBDTJ01"
#     else:
#         raise ValueError(f"❌ Unsupported model_name: {model}")

#     # -------------------------------------------------
#     # ✅ TRUST UI — DO NOT RE-COMPUTE FAILURE
#     # -------------------------------------------------
#     if not dips.get("left"):
#         issue = "Left Button Failed"
#     elif not dips.get("centre"):
#         issue = "Centre Button Failed"
#     elif not dips.get("right"):
#         issue = "Right Button Failed"
#     elif model in ["BUTTONPLUS", "BUTTONPRO"] and not dips.get("tstick"):
#         issue = "T-Stick Failed"
#     elif model in ["BUTTONPLUS", "BUTTONPRO"] and not dips.get("joystick"):
#         issue = "Joystick Failed"
#     else:
#         issue = "Button Failure"

#     dips=filter_dips_by_model(model,dips)

#     dips_json = json.dumps(dips)

#     try:
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         with sqlite3.connect(DB_FILE) as conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 INSERT INTO job_card_fail
#                 (device_serial_number, batch, employee_id, job_card_id,
#                  qc_system, system, issue, status, dips, timestamp)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 device_serial_number,
#                 batch,
#                 employee_id,
#                 job_card_id,
#                 qc_system,
#                 system,
#                 issue,
#                 status,
#                 dips_json,
#                 timestamp
#             ))
#             conn.commit()

#         print(f"❌ FAIL RECORDED → {device_serial_number} | {issue}")
#         retry_records()
#         return True

#     except Exception as e:
#         print(f"❌ Error inserting fail record: {e}")
#         return False


        system="TSTICKButtonDisplacement"
def insert_fail_record(device_serial_number, model, batch, employee_id, job_card_id, dips, ble_fail=False,ble_side=None, gpio_responses=None):
    """Insert fail record with clean DIP extraction, proper fail logic, and correct DB insert."""

    if not employee_id or not job_card_id:
        print("❌ Error: Employee ID or Job Card ID is missing.")
        return False
    serial_number=device_serial_number
    status="fail"
    model = model.strip()
  

    if model == "BUTTON":
        system = "3BUTTONButtonDisplacement"
        qc_system = "MARS"
    elif model == "TSTICK":
        system="TSTICKButtonDisplacement"
        qc_system="MARS"
    elif model == "BUTTONPLUS":
        system = "BUTTONPlusButtonDisplacement"
        qc_system = "MARS"
    elif model == "BUTTONPRO":
        system = "BUTTONProButtonDisplacement"
        qc_system = "MARS"
    else:
        raise ValueError(f"❌ Unsupported model_name: {model}")

    # Use the same button issue for GPIO and DIP failures.
    keys = (["tstick", "joystick"] if model == "TSTICK" else
            ["right", "centre", "left", "tstick", "joystick"]
            if model in ("BUTTONPLUS", "BUTTONPRO") else
            ["right", "centre", "left"])
    names = {"right": "Right Button", "centre": "Centre Button",
             "left": "Left Button", "tstick": "Tstick", "joystick": "Joystick"}
    failed = []
    for key in keys:
        value = dips.get(key, dips.get("center") if key == "centre" else None)
        if isinstance(value, list):
            value = value[0] if value else None
        lower = 4 if model == "BUTTON" and key == "centre" else 5
        dip_failed = value is None or not (lower <= value <= 13)
        gpio_failed = (gpio_responses is not None and key in ("right", "centre", "left")
                       and not gpio_responses.get(key, False))
        if dip_failed or gpio_failed:
            failed.append(names[key] + " Not Functioning")
    issue = "; ".join(failed) if failed else (ble_side if ble_fail else "Unknown Button Failure")
    failed_value = filter_dips_by_model(model, dips)
    dips_json = json.dumps({"dips": failed_value, "gpio": gpio_responses}) if gpio_responses is not None else json.dumps(failed_value)


    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO job_card_fail
                (device_serial_number, model, batch, employee_id, job_card_id,
                qc_system, system, issue, status, dips, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_serial_number,
                model,
                batch,
                employee_id,
                job_card_id,
                qc_system,
                system,
                issue,
                status,
                dips_json,
                timestamp
            ))

            conn.commit()

        print(f"❌ FAIL RECORDED → {device_serial_number} | {issue} | DIP = {failed_value}")
        retry_records()
        return True

    except Exception as e:
        print(f"❌ Error inserting fail record: {e}")
        return False

def increment_pass_count(employee_id, job_card_id):
    try:
        count = 0
        data = {}
        key = f"{employee_id}-{job_card_id}"

        if os.path.exists(PASS_COUNT_FILE):
            with open(PASS_COUNT_FILE, "r") as f:
                data = json.load(f)
                count = data.get(key, 0)

        count += 1
        data[key] = count

        with open(PASS_COUNT_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return count

    except Exception as e:
        print(f"Error incrementing count: {e}")
        return 0
    
def clear_pass_count(employee_id, job_card_id):
    try:
        if not os.path.exists(PASS_COUNT_FILE):
            return

        with open(PASS_COUNT_FILE, "r") as f:
            data = json.load(f)

        key = f"{employee_id}-{job_card_id}"
        if key in data:
            data[key] = 0

        with open(PASS_COUNT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error clearing count: {e}")

def get_pass_count(employee_id, job_card_id):
    try:
        if not os.path.exists(PASS_COUNT_FILE):
            return 0

        with open(PASS_COUNT_FILE, "r") as f:
            data = json.load(f)

        key = f"{employee_id}-{job_card_id}"
        return data.get(key, 0)
    except Exception as e:
        print(f"Error getting count: {e}")
        return 0

# def check_serial(serial_number): 
#     server_url = "ws://192.168.0.200:8050"

#     try:
#         ws = websocket.create_connection(server_url)
#         print("Connected to WebSocket server (Fetch Data)")

#         message = {
#             "type": "electricaljig",
#             "serial": serial_number
#         }
#         ws.send(json.dumps(message))

#         response = ws.recv()
#         print(response)
#         ws.close()
#         print("Connection closed\n")

       
#         data = json.loads(response)
#         print(data)

        
#         if data.get("status") == "success" :
            
#             return "mac"

#             # else:
#             # 	print("MAC address not found in response.")
#         else:
#             print("Unexpected or error response:", data)

#     except Exception as e:
#         print(f"Error fetching data for serial '{serial_number}':", e)


def send_jig_pass(employee,qc_system, dips, status):
    print("🚀 Sending jig calibration to ERP")

    payload = {
        "data": {
            "calibrate_by": employee,
            "values": json.dumps(dips),
            "qc_system":qc_system,
            "calibration_status": status
        }
    }

    print("➡️ URL:", JIG_PASS)
    print("📦 Payload:", json.dumps(payload, indent=2))

    try:
        response = requests.post(
            JIG_PASS,
            headers=HEADERS,
            json=payload,
            timeout=10
        )

        print("📡 Status:", response.status_code)
        print("📨 Response:", response.text)

        return response.status_code in (200, 201)

    except Exception as e:
        print("❌ ERP Exception:", e)
        return False

SYSTEM_NAME =["fail","completely fail"]
def check_serial_existss(serial_number: str) -> bool:
    """
    Check if serial number exists in ERP under the given system.
    Returns True if exists, False if not.
    """
    filters = [
        ["3_button_serialnumber", "=", serial_number.strip()],
        ["status", "in", SYSTEM_NAME]
    ]

    try:
        response = requests.get(
            ERP_DASHBOARD_URL,
            headers=HEADERS,
            params={"filters": json.dumps(filters)}
        )

        if response.status_code != 200:
            print(f"❌ ERP Error: Status code {response.status_code}")
            return False  # Treat error as not found (or handle as needed)

        data = response.json()
        results = data.get("data", [])

        if results:
            print(f"❌ Serial number '{serial_number}' already exists in '{SYSTEM_NAME}'")
            return True
        else:
            print(f"✅ Serial number '{serial_number}' is new in '{SYSTEM_NAME}'")
            return False

    except Exception as e:
        print(f"⚠️ Exception connecting to ERP: {e}")
        return False


def check_serial_existss_nova(serial_number: str) -> bool:
    return True
    """
    Check if serial number exists in ERP under the given system.
    Returns True if exists, False if not.
    """
    filters = [
        ["device_serialnumber", "=", serial_number.strip()],
        ["status", "in", SYSTEM_NAME]
    ]

    try:
        response = requests.get(
            ERP_NOVA,
            headers=HEADERS,
            params={"filters": json.dumps(filters)}
        )

        if response.status_code != 200:
            print(f"❌ ERP Error: Status code {response.status_code}")
            return False  # Treat error as not found (or handle as needed)

        data = response.json()
        results = data.get("data", [])

        if results:
            print(f"❌ Serial number '{serial_number}' already exists in '{SYSTEM_NAME}'")
            return True
        else:
            print(f"✅ Serial number '{serial_number}' is new in '{SYSTEM_NAME}'")
            return False

    except Exception as e:
        print(f"⚠️ Exception connecting to ERP: {e}")
        return False

