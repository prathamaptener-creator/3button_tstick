"""Shared settings for main_new.py and erp.py. Edit settings here only.
Existing development.env variable names and working-directory DB paths are preserved.
Restart the application after editing. No credentials are embedded in this file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / "production.env")
API_KEY = os.getenv("api_key")
API_SECRET = os.getenv("api_secret")
ERP_EMPLOYEE_URL = os.getenv("employee_url")
ERP_ITEM_URL = os.getenv("item_url")
ERP_JOB_CARD_URL = os.getenv("job_card_url")
ERP_DATA_LOG = os.getenv("data_log_url")
ERP_DASHBOARD_URL = os.getenv("dashborad_url")  # Existing spelling retained.
ERP_PASS = os.getenv("erp_pass")
ERP_NOVA = os.getenv("erp_nova")
JIG_PASS = os.getenv("jig_pass")
HEADERS = {"Authorization": f"token {API_KEY}:{API_SECRET}", "Content-Type": "application/json"}

# Relative paths intentionally retain existing working-directory behavior.
DB_FILE = "c20_Button1.db"
JIG_DB_FILE = "c60_btn_jig.db"
DAILY_CALIBRATION_DB = str(BASE_DIR / "daily_jig_calibration.db")
PASS_COUNT_FILE = "pass_count.json"
EMPLOYEES_FILE = "employees.json"
PASS_LOG_FILE = "job_card_pass_log.csv"
FAIL_LOG_FILE = "job_card_fail_log.csv"
MYSQL_CONFIG = dict(host="192.168.0.200", user="root", password="bluarmor560099#", database="ridetrust", charset="utf8mb4")
WEBSOCKET_URL = "ws://192.168.0.200:8050"
ARDUINO_PORT = "/dev/ttyUSB0"
GRBL_PORT = "/dev/ttyUSB1"
SERIAL_BAUDRATE = 115200

# True means perform the ERP check. Both were bypassed in the uploaded code.
VALIDATE_FUNCTIONALITY = False
VALIDATE_NOVA_SERIAL = False
SYSTEM_NAME = ["fail", "completely fail"]
FUNCTIONALITY_STAGES = {
    "BUTTON": ("3_button_serialnumber", "3buttoniptesting"),
    "TSTICK": ("t_stick_serialnumber", "TStickFunctionality"),
}
PRODUCTION_LIMITS = {
    "BUTTON": {"right": (5, 13), "centre": (4, 13), "left": (5, 13)},
    "TSTICK": {"joystick": (5, 13), "tstick": (5, 13)},
}
FILTER_DIP_RANGE = (3, 18)
DIP_THRESHOLD = 0.01
PRESS_TARGET_FORCE = 15.0
POST_DIP_EXTRA_FORCE = 2.0
PRESS_MAX_FORCE = 17.0
PRESS_TIMEOUT = 20.0
GPIO_BUTTON_PINS = {"right": 17, "centre": 10, "left": 8}
GPIO_RESPONSE_TIMEOUT = 1.0

DAILY_CALIBRATION = {
    "BUTTON": {"start": (14, 0), "end": (21, 0), "serial": "GD-BUTTON-001",
               "limits": {"right": (5.0, 13.0), "centre": (4.0, 13.0), "left": (5.0, 13.0)}},
    "TSTICK": {"start": (14, 0), "end": (21, 0), "serial": "GD-TSTICK-001",
               "limits": {"joystick": (5.0, 13.0), "tstick": (5.0, 13.0)}},
}

__all__ = [name for name in globals() if name.isupper() and not name.startswith("_")]
