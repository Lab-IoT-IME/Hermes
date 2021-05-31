# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database
import json
from urllib.parse import quote_plus

with open('sql_server.json') as f:
  sql_con = json.load(f)

odbc_str = f"DRIVER={sql_con['driver']};SERVER={sql_con['server']};PORT={sql_con['port']};UID={sql_con['username']};DATABASE={sql_con['database']};PWD={sql_con['password']}"
connect_str = 'mssql+pyodbc:///?odbc_connect=' + quote_plus(odbc_str)

SQLALCHEMY_DATABASE_URI = connect_str
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"