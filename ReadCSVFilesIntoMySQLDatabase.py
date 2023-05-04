from datetime import date, timedelta
import os
import csv
from peewee import *

# create the database connection
db = MySQLDatabase('airfares', user='root', password='root', host='localhost', autocommit=True)

# define the models
class Airport(Model):
    airportCode = CharField(max_length=50, unique=True, index=True)
    airportName = CharField(max_length=255)
    city = CharField(max_length=255)
    country = CharField(max_length=255)

    class Meta:
        database = db

class Airline(Model):
    carrierCode = CharField(max_length=50, unique=True, index=True)
    carrierName = CharField(max_length=255)

    class Meta:
        database = db

class Flight(Model):
    flightKey = CharField(max_length=255, unique=True, index=True)
    flightNumber = CharField(max_length=50)
    departureDate = DateField()
    arrivalDate = DateField()
    departureTime = TimeField()
    arrivalTime = TimeField()
    journeyDuration = TimeField()
    totalNumberOfStops = IntegerField()
    carrierCode = ForeignKeyField(Airline, to_field='carrierCode', on_delete='CASCADE', on_update='CASCADE')
    depAirportCode = ForeignKeyField(Airport, to_field='airportCode', on_delete='CASCADE', on_update='CASCADE', backref='departures')
    arrAirportCode = ForeignKeyField(Airport, to_field='airportCode', on_delete='CASCADE', on_update='CASCADE', backref='arrivals')

    class Meta:
        database = db

class Price(Model):
    priceID = AutoField()
    flightKey = ForeignKeyField(Flight, to_field='flightKey', on_delete='CASCADE', on_update='CASCADE')
    scrapeDate = DateField()
    availableSeats = IntegerField()
    adultPrice = FloatField()

    class Meta:
        database = db


# create the tables if they don't exist
db.create_tables([Flight, Price, Airport, Airline])

try:
    # insert the airport records
    with open('./data/csv2/airport.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row == []:
                continue
            else:
                if not Airport.select().where(Airport.airportCode == row[0]).exists():
                    with db.atomic():
                        Airport.create(
                            airportCode=row[0],
                            airportName=row[1],
                            city=row[2],
                            country=row[3]
                        )
                    db.commit()

    # insert the airline records
    with open('./data/csv2/airline.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row == []:
                continue
            else:
                if not Airline.select().where(Airline.carrierCode == row[0]).exists():
                    with db.atomic():
                        Airline.create(
                            carrierCode=row[0],
                            carrierName=row[1]
                        )
                    db.commit()
except Exception as e:
    print("Error while connecting to MySQL", e)

try:
    start_date = date(2023, 4, 6)
    # choose a specific start_date    
    end_date = date.today()
    delta = timedelta(days=1) 
    while start_date <= end_date:
        date_format = start_date.strftime("%Y_%m_%d")
        # for each date and for each airline check if the file exists and copy the file to C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\
        for airline in ('Ryanair', 'Tui', 'Transavia', 'BA'):
            path = "./data/csv2/" + airline + "_" + date_format + ".csv"
            if os.path.exists(path): 
                    # insert the data from the CSV file into the database
                    with open(path, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            if row == []:
                                continue
                            else:
                                with db.atomic():
                                    # check for duplicates
                                    # print(Flight.select().where(Flight.flightKey == row[0]).exists())   
                                    if not Flight.select().where(Flight.flightKey == row[0]).exists():
                                        #flightkey,flightNumber,departureDate,arrivalDate,departureTime,arrivalTime,journeyDuration,totalNumberOfStops,carrierCode,depAirportCode,arrAirportCode,scrapeDate,availableSeats,adultPrice
                                        # insert the flight record
                                        flight = Flight.create(
                                            flightKey=row[0],
                                            flightNumber=row[1],
                                            departureDate=row[2],
                                            arrivalDate=row[3],
                                            departureTime=row[4],
                                            arrivalTime=row[5],
                                            journeyDuration=row[6],
                                            totalNumberOfStops=row[7],
                                            carrierCode=row[8],
                                            depAirportCode=row[9],
                                            arrAirportCode=row[10]
                                        )
                                    else:
                                        flight = Flight.get(Flight.flightKey == row[0])
                                        flight.flightNumber = row[1]
                                        flight.departureDate = row[2]
                                        flight.arrivalDate = row[3]
                                        flight.departureTime = row[4]
                                        flight.arrivalTime = row[5]
                                        flight.journeyDuration = row[6]
                                        flight.totalNumberOfStops = row[7]
                                        flight.carrierCode = row[8]
                                        flight.depAirportCode = row[9]
                                        flight.arrAirportCode = row[10]
                                        flight.save()
                                        
                                
                                    # insert the price record
                                    flight = Flight.get(Flight.flightKey == row[0])
                                    if flight:
                                        price = Price.select().where(
                                            (Price.flightKey == flight) & (Price.scrapeDate == row[11])
                                        ).first()

                                        if price:
                                            # update existing price record
                                            price.availableSeats = row[12]
                                            price.adultPrice = row[13]
                                            price.save()
                                        else:
                                            # create new price record
                                            Price.create(
                                                flightKey=flight,
                                                scrapeDate=row[11],
                                                availableSeats=row[12],
                                                adultPrice=row[13]
                                            )

                                db.commit()
        start_date += delta

except Exception as e:
    print("Error while connecting to MySQL", e)
finally:
    db.close()
    print("MySQL connection is closed")