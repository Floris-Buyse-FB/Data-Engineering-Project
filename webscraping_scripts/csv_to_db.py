import csv
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    user="root",
    password="root",
    database="DE_project",
    ssl_disabled=True
)

today = datetime.today().strftime('%Y-%m-%d')

def convert_to_date(date_string):
    return date_string if date_string in ["scrapeDate", "departureDate", "arrivalDate"] else datetime.strptime(date_string, '%Y-%m-%d').date()

def convert_to_time(time_string):
    return time_string.split('+')[0] 

def subtract_times(arr, dep):
    datetime1 = datetime.strptime(arr, '%H:%M')
    datetime2 = datetime.strptime(dep, '%H:%M')
    time_diff = datetime1 - datetime2

    total_seconds = int(time_diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    formatted_result = f"{hours:02d}:{minutes:02d}"

    return formatted_result

def tui_insertion():
    with open(f'/home/vicuser/Data-Engineering-Project/data/tuifly/tuiFlyScrapeData_{today}.csv') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            flightKey = row[0]
            flightNumber = row[1]
            scrapeDate = row[2]
            departureAirportCode = row[3]
            departureAirportName = row[4]
            departureCountryCode = row[5]
            departureDate = convert_to_date(row[6])
            departureTime = convert_to_time(row[7])
            arrivalAirportCode = row[8]
            arrivalAirportName = row[9]
            arrivalCountryCode = row[10]
            arrivalDate = convert_to_date(row[11])
            arrivalTime = convert_to_time(row[12])
            adultPrice = float(row[13])
            journeyType = row[15]
            journeyDuration = row[16]
            totalNumberOfStops = row[17]
            if totalNumberOfStops == "":
                totalNumberOfStops = 0
            carrierCode = row[18]
            carrierName = row[19]
            availableSeats = row[20]
            
            mycursor = db.cursor()
            
            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if departureAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode, airportName, countryCode) VALUES (%s, %s, %s)"
                valDepAirport = (departureAirportCode, departureAirportName, departureCountryCode)
                mycursor.execute(sqlAirport, valDepAirport)
                db.commit()
            
            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if arrivalAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode, airportName, countryCode) VALUES (%s, %s, %s)"
                valArrAirport = (arrivalAirportCode, arrivalAirportName, arrivalCountryCode)
                mycursor.execute(sqlAirport, valArrAirport)
                db.commit()

            mycursor.execute("SELECT carrierCode FROM Airline")
            result = mycursor.fetchall()
            list_of_airlines = [item[0] for item in result]
            if carrierCode not in list_of_airlines:
                sqlAirline = "INSERT INTO Airline (carrierCode, carrierName) VALUES (%s, %s)"
                valAirline = (carrierCode, carrierName)
                mycursor.execute(sqlAirline, valAirline)
                db.commit()
            
            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey not in list_of_flights:
                sqlFlight = "INSERT INTO Flight (flightKey, carrierCode, depAirportCode, arrAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                valFlight = (flightKey, carrierCode, departureAirportCode, arrivalAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType)
                mycursor.execute(sqlFlight, valFlight)
                db.commit()

            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey in list_of_flights:
                sqlPrice = "INSERT INTO Price (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice) values (%s, %s, %s, %s, %s, %s)"
                valPrice = (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice)
                mycursor.execute(sqlPrice, valPrice)
                db.commit()

def ryanair_insertion():
    with open(f'/home/vicuser/Data-Engineering-Project/data/ryanair/ryanairScrapeData_{today}.csv') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            scrapeDate = convert_to_date(row[0])
            flightKey = row[1]
            flightNumber = row[2]
            departureAirportCode = row[3]
            departureAirportName = row[4]
            arrivalAirportCode = row[5]
            arrivalAirportName = row[6]
            departureDate = convert_to_date(row[7])
            departureTime = convert_to_time(row[8])
            arrivalDate = convert_to_date(row[9])
            arrivalTime = convert_to_time(row[10])
            carrierCode = row[11]
            carrierName = row[12]
            journeyDuration = row[13]
            adultPrice = float(row[14])
            journeyType = row[19]
            availableSeats = row[20]
            totalNumberOfStops = 0
            mycursor = db.cursor()

            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if departureAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode, airportName) VALUES (%s, %s)"
                valDepAirport = (departureAirportCode, departureAirportName)
                mycursor.execute(sqlAirport, valDepAirport)
                db.commit()
            
            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if arrivalAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode, airportName, countryCode) VALUES (%s, %s)"
                valArrAirport = (arrivalAirportCode, arrivalAirportName)
                mycursor.execute(sqlAirport, valArrAirport)
                db.commit()

            mycursor.execute("SELECT carrierCode FROM Airline")
            result = mycursor.fetchall()
            list_of_airlines = [item[0] for item in result]
            if carrierCode not in list_of_airlines:
                sqlAirline = "INSERT INTO Airline (carrierCode, carrierName) VALUES (%s, %s)"
                valAirline = (carrierCode, carrierName)
                mycursor.execute(sqlAirline, valAirline)
                db.commit()
            
            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey not in list_of_flights:
                sqlFlight = "INSERT INTO Flight (flightKey, carrierCode, depAirportCode, arrAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                valFlight = (flightKey, carrierCode, departureAirportCode, arrivalAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType)
                mycursor.execute(sqlFlight, valFlight)
                db.commit()

            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey in list_of_flights:
                sqlPrice = "INSERT INTO Price (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice) values (%s, %s, %s, %s, %s, %s)"
                valPrice = (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice)
                mycursor.execute(sqlPrice, valPrice)
                db.commit()

def transavia_insertion():
    with open(f'/home/vicuser/Data-Engineering-Project/data/transavia/transaviaScrapeData_{today}.csv') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            scrapeDate = convert_to_date(row[0])
            flightKey = row[1]
            departureAirportCode = row[2]
            arrivalAirportCode = row[3]
            carrierCode = row[4]
            carrierName = row[5]
            departureDate = convert_to_date(row[6])
            departureTime = row[7][0:5]
            arrivalDate = convert_to_date(row[8])
            arrivalTime = row[9][0:5]
            flightNumber = row[10]
            adultPrice = float(row[11])
            journeyDuration = subtract_times(arrivalTime, departureTime) 
            availableSeats = None
            totalNumberOfStops = 0
            journeyType = 'Direct'
            mycursor = db.cursor()

            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if departureAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode) VALUES (%s)"
                valDepAirport = departureAirportCode
                mycursor.execute(sqlAirport, valDepAirport)
                db.commit()
            
            mycursor.execute("SELECT airportCode FROM Airport")
            result = mycursor.fetchall()
            list_of_airports = [item[0] for item in result]
            if arrivalAirportCode not in list_of_airports:
                sqlAirport = "INSERT INTO Airport (airportCode) VALUES (%s)"
                valArrAirport = arrivalAirportCode
                mycursor.execute(sqlAirport, valArrAirport)
                db.commit()

            mycursor.execute("SELECT carrierCode FROM Airline")
            result = mycursor.fetchall()
            list_of_airlines = [item[0] for item in result]
            if carrierCode not in list_of_airlines:
                sqlAirline = "INSERT INTO Airline (carrierCode, carrierName) VALUES (%s, %s)"
                valAirline = (carrierCode, carrierName)
                mycursor.execute(sqlAirline, valAirline)
                db.commit()
            
            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey not in list_of_flights:
                sqlFlight = "INSERT INTO Flight (flightKey, carrierCode, depAirportCode, arrAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                valFlight = (flightKey, carrierCode, departureAirportCode, arrivalAirportCode, flightNumber, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops, journeyType)
                mycursor.execute(sqlFlight, valFlight)
                db.commit()
                
            mycursor.execute("SELECT flightKey FROM Flight")
            result = mycursor.fetchall()
            list_of_flights = [item[0] for item in result]
            if flightKey in list_of_flights:
                sqlPrice = "INSERT INTO Price (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice) values (%s, %s, %s, %s, %s, %s)"
                valPrice = (flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice)
                mycursor.execute(sqlPrice, valPrice)
                db.commit()

def start():
    # bruair_insertion()
    tui_insertion()
    ryanair_insertion()
    transavia_insertion()

start()


# def convert_to_duration(duration_string):
#     if duration_string == "duration":
#         return duration_string
#     else:
#         hours, minutes = duration_string.split(':')
#         return int(hours) * 60 + int(minutes)    

# def bruair_insertion():
#     with open('/home/vicuser/Data-Engineering-Project/data/bruair/BruAirScrapeData_2023-03-23.csv') as file:
#         reader = csv.reader(file)
#         next(reader) 
#         for row in reader:
#             scrapeDate = convert_to_date(row[0])
#             departureAirportCode = row[1]
#             departureAirportName = row[2]
#             departureCountryCode = row[3]
#             arrivalAirportCode = row[4]
#             arrivalAirportName = row[5]
#             arrivalCountryCode = row[6]
#             duration = convert_to_duration(row[7])
#             aantalTussenstops = row[8]
#             availableSeats = row[9]
#             flightNumber = row[10]
#             carrierCode = row[11]
#             carrierName = row[12]
#             departureDate = convert_to_date(row[13])
#             departureTime = convert_to_time(row[14])
#             arrivalDate = convert_to_date(row[15])
#             arrivalTime = convert_to_time(row[16])
#             totalPrice = row[17]
#             taxIncludedInPrice = row[18]
#             mycursor = db.cursor()
#             mycursor.execute(f'INSERT INTO Airport(airportCode, airportName, countryCode) VALUES ({departureAirportCode}, {departureAirportName}, {departureCountryCode}) ')
#             mycursor.execute(f'INSERT INTO Airport(airportCode, airportName, countryCode) VALUES ({arrivalAirportCode}, {arrivalAirportName}, {arrivalCountryCode}) ')
#             mycursor.execute(f'INSERT INTO Airline(carrierCode, carrierName) VALUES ({carrierCode}, {carrierName})')
#             mycursor.execute(f'INSERT INTO Flight(flightKey, carrierCode, depAirportCode, arrAirportCode, departureDate, departureTime, arrivalDate, arrivalTime, journeyDuration, totalNumberOfStops) values ({flightNumber}, {carrierCode}, {departureAirportCode}, {arrivalAirportCode}, {departureDate}, {departureTime}, {arrivalDate}, {arrivalTime}, {duration}, {aantalTussenstops})')
#             mycursor.execute(f'INSERT INTO Price(flightKey, departureDate, departureTime, scrapeDate, availableSeats, adultPrice, airportTax) values ({flightNumber}, {departureDate}, {departureTime}, {scrapeDate}, {availableSeats}, {totalPrice}, {taxIncludedInPrice})')
#             db.commit()