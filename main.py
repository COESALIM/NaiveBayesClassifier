import psycopg2 as psql

import time
import datetime

from product_id import products

# Database information:
user = input("Enter Username: ")
dbname = input("Enter database name: ")
password = input("Enter Password:")
port = 5432
# Set start time
start_time = datetime.datetime.now()
start_time = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")

products(dbname, user, password, port)
# Set end time
end_time = datetime.datetime.now()
end_time = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")

print("Start at:", start_time)
print("End at:", end_time)
