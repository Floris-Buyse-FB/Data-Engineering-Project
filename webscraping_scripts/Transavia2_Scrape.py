import http.client, urllib.request, urllib.parse, urllib.error, base64, datetime,csv,json
from datetime import date

DESTINATIONS = ['FAO','HER','ALC','IBZ','AGP','TFS']
COLUMNS=['scrapeDate', 'departAirport', 'arrivalAirport', 'marketingAirline', "departureDate", "arrivalDate", "flightNumber", "totalPrice", "baseFare", "taxSurcharge" ]



headers = {

    # Request headers

    'apikey': '17c5625ff4424000b95a0ae6f3a23586',

}

def start():
    scrapeDate = date.today()
    init_csv(scrapeDate)
    start_date = datetime.date(2023, 4, 1)
    end_date = datetime.date(2023, 10, 1)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")

        for element in DESTINATIONS:
            getData(element,date_str,scrapeDate)

        current_date += datetime.timedelta(days=1)
    



def getData(element,date,scrapeDate):
    params = urllib.parse.urlencode({

    # Request parameters

    'origin': 'BRU',

    'destination': element,
    
    'originDepartureDate': date,

    })

    try:

        conn = http.client.HTTPSConnection('api.transavia.com')

        conn.request("GET", "/v1/flightoffers/?%s" % params, "{body}", headers)

        response = conn.getresponse()

        data = response.read()
        print(data)
        if len(data) != 0:
            string = data.decode('utf-8')
            
            jsonData = json.loads(string)
            clean_data(jsonData,scrapeDate)


        conn.close()

    except Exception as e:

        print("[Errno {0}] {1}".format(e.errno, e.strerror))


def init_csv(date):
    url = f'data/transavia/transaviaScrapeData_{date}.csv'
    with open(url, 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(COLUMNS)  

#append a row of data to the csv file
def data_to_csv(data,date):
    url = f'data/transavia/transaviaScrapeData_{date}.csv'
    with open(url, 'a', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(data)       


def clean_data(json,scrapeDate):
        print(json['flightOffer'])
        for f in json["flightOffer"]:
            outboundFlight = f["outboundFlight"]
            pricingInfoSum = f["pricingInfoSum"]
            departAirport= outboundFlight["departureAirport"]["locationCode"]
            arrivalAirport = outboundFlight["arrivalAirport"]["locationCode"]
            marketingAirline = outboundFlight['marketingAirline']['companyShortName']
            departureDateTime = outboundFlight["departureDateTime"]
            arrivalDateTime = outboundFlight["arrivalDateTime"]
            flightNumber = outboundFlight["flightNumber"]
            totalPriceOnePassenger = pricingInfoSum["totalPriceOnePassenger"]
            baseFare = pricingInfoSum["baseFare"]
            taxSurcharge = pricingInfoSum["taxSurcharge"]
            data_to_csv([scrapeDate, departAirport, arrivalAirport, marketingAirline, departureDateTime, arrivalDateTime, flightNumber, totalPriceOnePassenger, baseFare, taxSurcharge],scrapeDate)

start()