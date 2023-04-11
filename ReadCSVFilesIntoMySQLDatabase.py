import pandas as pd
import mysql.connector as mysql
from mysql.connector import Error
from datetime import date, timedelta
import shutil
import os

try:
    # autocommit is zéér belangrijk.
    conn = mysql.connect(host='localhost', database='airfares', user='root', password='passwoord', autocommit=True)

    if conn.is_connected():
        # choose a specific start_date    
        start_date = date(2023, 4, 6)
        end_date = date.today()
        delta = timedelta(days=1) 
        while start_date <= end_date:

            date_format = start_date.strftime("%Y_%m_%d")

            # for each date and for each airline check if the file exists and copy the file to C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\
            for airline in ('Ryanair', 'Tui', 'Transavia', 'BA'):
                old_path = "./data/csv2/" + airline + "_" + date_format + ".csv" 
                new_path = "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\" + airline + ".csv"
                # Remove file if it already exists
                if os.path.exists(new_path):
                    os.remove(new_path)
                if os.path.exists(old_path):    
                    shutil.copy(old_path, new_path)


            # conn.reconnect is important, otherwise error
            conn.reconnect()
            cursor = conn.cursor()  

            # Execute commands in file LoadFiles.sql to import data into database airfares
            with open('./LoadFiles.sql', 'r') as f:
                cursor.execute(f.read(), multi=True)    
            cursor.close()
            
            start_date += delta
    
    conn.close()       


except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (conn.is_connected()):
        cursor.close()
        conn.close()
        print("MySQL connection is closed")


import csv
from peewee import *

# create the database connection
db = MySQLDatabase('airfares', user='root', password='passwoord', host='localhost')

# define the models
class Flight(Model):
    flightKey = CharField(max_length=255, unique=True)
    departureDate = DateField()
    departureTime = TimeField()
    depAirportCode = CharField(max_length=50)
    arrAirportCode = CharField(max_length=50)
    carrierCode = CharField(max_length=50)
    flightNumber = CharField(max_length=50)
    arrivalDate = DateField()
    arrivalTime = TimeField()
    journeyDuration = TimeField()
    totalNumberOfStops = IntegerField()

    class Meta:
        database = db

class Price(Model):
    priceID = AutoField()
    flightKey = ForeignKeyField(Flight, backref='prices')
    scrapeDate = DateField()
    availableSeats = IntegerField()
    adultPrice = FloatField()

    class Meta:
        database = db

# create the tables if they don't exist
db.create_tables([Flight, Price])

# specify the path to the CSV file
filename = '/path/to/your/csv/file.csv'

# insert the data from the CSV file into the database
with open(filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # check for duplicates
        if not Flight.select().where(Flight.flightKey == row[0]).exists():
            # insert the flight record
            flight = Flight.create(
                flightKey=row[0],
                departureDate=row[1],
                departureTime=row[2],
                depAirportCode=row[3],
                arrAirportCode=row[4],
                carrierCode=row[5],
                flightNumber=row[6],
                arrivalDate=row[7],
                arrivalTime=row[8],
                journeyDuration=row[9],
                totalNumberOfStops=row[10]
            )
        # insert the price record
        Price.create(
            flightKey=flight,
            scrapeDate=row[11],
            availableSeats=row[12],
            adultPrice=row[13]
        )
