import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv

#URL = f"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateIn=2023-03-14&DateOut=2023-03-02&Destination=TRF&Disc=0&INF=0&Origin=BRU&TEEN=0&promoCode=&IncludeConnectingFlights=false&FlexDaysBeforeOut=2&FlexDaysOut=2&FlexDaysBeforeIn=2&FlexDaysIn=2&RoundTrip=true&ToUs=AGREED"

#"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateOut=2023-03-26&Destination=CFU&Disc=0&INF=0&Origin=CRL&TEEN=0&promoCode=&RoundTrip=false&ToUs=AGREED"

ORIGINS = ['BRU','CRL']
DESTINATIONS = ['CFU','HER','RHO','BDS','NAP','PMO','FAO','ALC','IBZ','AGP','SPC','TFS']
COLUMNS=['origin','destination','departtime','arrivaltime','duration','price','faresLeft']


def init_csv():
    with open('data/ryanairScrapeData.csv', 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(COLUMNS)  

def data_to_csv(data):
    with open('data/ryanairScrapeData.csv', 'a', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(data)            

def get_data():
    #loop over dates between 2023-04-01 AND 2023-10-31
    for single_date in pd.date_range('2023-04-01','2023-10-31'):
        date =single_date.strftime("%Y-%m-%d")

        for origin in ORIGINS:
            for destination in DESTINATIONS:

                URL = f"https://www.ryanair.com/api/booking/v4/nl-nl/availability?ADT=1&CHD=0&DateOut={date}&Destination={destination}&Disc=0&INF=0&Origin={origin}&TEEN=0&promoCode=&RoundTrip=false&ToUs=AGREED"

                page = requests.get(URL)
                soup = BeautifulSoup(page.content, "lxml")
                result = soup.find("p").text

                #convert string to  object
                json_object = json.loads(result)
                
                flights = json_object["trips"][0]["dates"][0]["flights"]
                if flights:
                    faresleft = flights[0]['faresLeft']
                    amount = flights[0]['regularFare']['fares'][0]['amount']
                    departtime = flights[0]['segments'][0]['time'][0]
                    arrivaltime = flights[0]['segments'][0]['time'][1]
                    duration = flights[0]['segments'][0]['duration']
                    #count = flights[0]['regularFare']['fares'][0]['count']
                    #print(origin, departtime, destination, arrivaltime ,faresleft, amount, duration,count)
                    data_to_csv([origin,destination,departtime,arrivaltime,duration,amount,faresleft])

def start():
    init_csv()
    get_data()

start()
# raw data {'faresLeft': 4, 'flightKey': 'FR~2923~ ~~BRU~03/26/2023 09:55~AGP~03/26/2023 12:50~~', 'infantsLeft': 13, 'regularFare': {'fareKey': 'BRS4IK66UVTAORXBUNPKZCBVNFJYSREAYHVKE6XH7SWRQ3UHROY377UTMYV3WY6IFIPAJXYQT7YHMKEV2ZTJJ3TKRFXWVZYVNOXBTOGLXPPF43MUK4DLPJLGSC52HCXXRZCPXBK4VBGW44FI55ATHRXATHQTGWURCGIFOJAVZEHJEHUS2SNUHI67CRCWV5ANY43HCEDA2MWDWMR2B7D4ZI3NCC43CYXELDWUZLQ', 'fareClass': 'C', 'fares': [{'type': 'ADT', 'amount': 90.73, 'count': 1, 'hasDiscount': False, 'publishedFare': 90.73, 'discountInPercent': 0, 'hasPromoDiscount': False, 'discountAmount': 0.0, 'hasBogof': False}]}, 'operatedBy': '', 'segments': [{'segmentNr': 0, 'origin': 'BRU', 'destination': 'AGP', 'flightNumber': 'FR 2923', 'time': ['2023-03-26T09:55:00.000', '2023-03-26T12:50:00.000'], 'timeUTC': ['2023-03-26T07:55:00.000Z', '2023-03-26T10:50:00.000Z'], 'duration': '02:55'}], 'flightNumber': 'FR 2923', 'time': ['2023-03-26T09:55:00.000', '2023-03-26T12:50:00.000'], 'timeUTC': ['2023-03-26T07:55:00.000Z', '2023-03-26T10:50:00.000Z'], 'duration': '02:55'}