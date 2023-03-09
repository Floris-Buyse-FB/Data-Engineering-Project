import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv
from datetime import date

#URL = f"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateIn=2023-03-14&DateOut=2023-03-02&Destination=TRF&Disc=0&INF=0&Origin=BRU&TEEN=0&promoCode=&IncludeConnectingFlights=false&FlexDaysBeforeOut=2&FlexDaysOut=2&FlexDaysBeforeIn=2&FlexDaysIn=2&RoundTrip=true&ToUs=AGREED"

#"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateOut=2023-03-26&Destination=CFU&Disc=0&INF=0&Origin=CRL&TEEN=0&promoCode=&RoundTrip=false&ToUs=AGREED"

ORIGINS = ['BRU','CRL']
DESTINATIONS = ['CFU','HER','RHO','BDS','NAP','PMO','FAO','ALC','IBZ','AGP','SPC','TFS']
COLUMNS=['flightNumber','departureAirportCode','departureAirportName','arrivalAirportCode','arrivalAirportName','departureDate','arrivalDate','carrierCode','duration_formatted','price','originalPrice','hasDiscount','hasPromoDiscount','discountAmount','fareType','availableSeats','flightKey']

#write the column of the cvs file
def init_csv(date):
    url = f'data/ryanair/ryanairScrapeData_{date}.csv'
    with open(url, 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(COLUMNS)  

#append a row of data to the csv file
def data_to_csv(data,date):
    url = f'data/ryanair/ryanairScrapeData_{date}.csv'
    with open(url, 'a', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(data)            

def get_data(datecsv):
    #loop over dates between 2023-04-01 AND 2023-10-31
    for single_date in pd.date_range('2023-04-01','2023-10-31'):
        date =single_date.strftime("%Y-%m-%d")

        #loop over all departure airports
        for departureAirportCode in ORIGINS:
            #loop over all arrival airports
            for arrivalAirportCode in DESTINATIONS:

                URL = f"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateOut={date}&Destination={arrivalAirportCode}&Disc=0&INF=0&Origin={departureAirportCode}&TEEN=0&promoCode=&RoundTrip=false&ToUs=AGREED"

                page = requests.get(URL)
                soup = BeautifulSoup(page.content, "lxml")
                result = soup.find("p").text

                #convert string to  object
                json_object = json.loads(result)
                departureAirportName = json_object["trips"][0]["originName"]
                arrivalAirportName = json_object["trips"][0]["destinationName"]

                #select flights from json object that was received
                flights = json_object["trips"][0]["dates"][0]["flights"]

                #if the object contains flight data then we select all wanted info
                if flights:
                    flightNumber = flights[0]["flightNumber"]
                    departureDate = flights[0]['segments'][0]['time'][0]
                    arrivalDate = flights[0]['segments'][0]['time'][1]
                    carrierCode = flights[0]["operatedBy"]
                    duration_formatted = flights[0]['segments'][0]['duration']
                    price = flights[0]['regularFare']['fares'][0]['amount']
                    originalPrice = flights[0]['regularFare']['fares'][0]['publishedFare']
                    hasDiscount = flights[0]['regularFare']['fares'][0]["hasDiscount"]
                    hasPromoDiscount = flights[0]['regularFare']['fares'][0]["hasPromoDiscount"]
                    discountAmount = flights[0]['regularFare']['fares'][0]["discountAmount"]
                    availableSeats = flights[0]['faresLeft']
                    fareType = flights[0]['regularFare']['fares'][0]["type"]
                    flightKey = flights[0]["flightKey"]

                    #put the scraped data in csv file
                    data_to_csv([flightNumber,departureAirportCode,departureAirportName,arrivalAirportCode,arrivalAirportName,
                    departureDate,arrivalDate,carrierCode,duration_formatted,price,originalPrice,hasDiscount,hasPromoDiscount,discountAmount,fareType,availableSeats,flightKey],datecsv)

def start():
    today = date.today()
    init_csv(today)
    get_data(today)

start()
# raw data {'faresLeft': 4, 'flightKey': 'FR~2923~ ~~BRU~03/26/2023 09:55~AGP~03/26/2023 12:50~~', 'infantsLeft': 13, 'regularFare': {'fareKey': 'BRS4IK66UVTAORXBUNPKZCBVNFJYSREAYHVKE6XH7SWRQ3UHROY377UTMYV3WY6IFIPAJXYQT7YHMKEV2ZTJJ3TKRFXWVZYVNOXBTOGLXPPF43MUK4DLPJLGSC52HCXXRZCPXBK4VBGW44FI55ATHRXATHQTGWURCGIFOJAVZEHJEHUS2SNUHI67CRCWV5ANY43HCEDA2MWDWMR2B7D4ZI3NCC43CYXELDWUZLQ', 'fareClass': 'C', 'fares': [{'type': 'ADT', 'amount': 90.73, 'count': 1, 'hasDiscount': False, 'publishedFare': 90.73, 'discountInPercent': 0, 'hasPromoDiscount': False, 'discountAmount': 0.0, 'hasBogof': False}]}, 'operatedBy': '', 'segments': [{'segmentNr': 0, 'origin': 'BRU', 'destination': 'AGP', 'flightNumber': 'FR 2923', 'time': ['2023-03-26T09:55:00.000', '2023-03-26T12:50:00.000'], 'timeUTC': ['2023-03-26T07:55:00.000Z', '2023-03-26T10:50:00.000Z'], 'duration': '02:55'}], 'flightNumber': 'FR 2923', 'time': ['2023-03-26T09:55:00.000', '2023-03-26T12:50:00.000'], 'timeUTC': ['2023-03-26T07:55:00.000Z', '2023-03-26T10:50:00.000Z'], 'duration': '02:55'}