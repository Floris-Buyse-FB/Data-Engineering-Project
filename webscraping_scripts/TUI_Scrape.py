from selenium import webdriver
from datetime import date, datetime
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager 
import json, re, csv, pandas as pd

def init_csv(today):
    COLUMNS=["flightKey","flightNumber", "scrapeDate", "departureAirportCode", "departureAirportName", "departureCountryCode", "departureDate", "departureTime", "arrivalAirportCode", "arrivalAirportName", "arrivalCountryCode", "arrivalDate", "arrivalTime", "adultPrice", "originalAdultPrice", "journeyType", "journeyDuration", "totalNumberOfStops", "carrierCode", "carrierName", "availableSeats", "isCheapest", "airportTax", "originalAirportTax", "bookingFee", "originalBookingFee", "isOriginalBooking"]
    url = f'data/tuifly/tuiFlyScrapeData_{today}.csv'
    with open(url, 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(COLUMNS)

def data_to_csv(data, today):
    url = f'../data/tuifly/tuiFlyScrapeData_{today}.csv'
    with open(url, 'a', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(data)

def get_raw_data(url):
        PATH = "../../.cache/selenium/chromedriver/linux64/111.0.5563.64/chromedriver"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument('--ignore-certificate-errors')
        driver_service = Service(executable_path=PATH)
        driver = webdriver.Chrome(service=driver_service,options=options)
        driver.maximize_window()
        driver.implicitly_wait(25)
        driver.get(url)

        driver.find_element(By.CSS_SELECTOR, "#cmCloseBanner").click()
        try: 
            WebDriverWait(driver, 50).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#page div.container > :nth-child(3)"))
            )

            result = driver.find_element(By.CSS_SELECTOR, "div#page div.container > :nth-child(3)").get_attribute('innerHTML')
        except:
            print("An error has occured in get_raw_data()")

        driver.close()
        match = re.search(r"var searchResultsJson = ({.*});", result)
        if match:
            json_data = match.group(1)
            return json.loads(json_data)

def get_useful_data(raw_data, today):
    for flight in raw_data["flightViewData"]:
        try:
            date_parts = flight["departureDate"].split('-')
            if str(flight["journeySummary"]["departAirportCode"]) in("BRU", "LGG", "OST", "ANR") and date(2023, 4, 1) <= date(2023, int(date_parts[1]), int(date_parts[2])) and date(2023, int(date_parts[1]), int(date_parts[2])) <= date(2023, 10, 1):
                departureCountryCode = raw_data["depAirportData"][0]["countryCode"]
                arrivalCountryCode = raw_data["arrAirportData"][0]["countryCode"]
                departureAirportCode = flight["journeySummary"]["departAirportCode"]
                departureAirportName = flight["flightsectors"][0]["departureAirport"]["name"]
                departureDate = flight["departureDate"]
                departureTime = flight["flightsectors"][0]["schedule"]["depTime"]
                arrivalAirportCode = flight["journeySummary"]["arrivalAirportCode"]
                arrivalAirportName = flight["flightsectors"][0]["arrivalAirport"]["name"]
                arrivalDate = flight['journeySummary']["arrivalDate"]
                arrivalTime = flight["flightsectors"][0]["schedule"]["arrTime"]
                adultPrice = flight["adultPrice"]
                originalAdultPrice = flight["originalAdultPrice"]
                journeyType = flight["journeySummary"]["journeyType"]
                journeyDuration = flight["journeySummary"]["journeyDuration"]
                hours, minutes = int(journeyDuration.split("u ")[0]), int(journeyDuration.split("u ")[1].replace("m", ""))
                journeyDuration = f"{hours:02}:{minutes:02}"
                totalNumberOfStops = flight["journeySummary"]["totalNumberOfStops"]
                carrierCode = flight["journeySummary"]["carrierCode"]
                carrierName = flight["journeySummary"]["carrierName"]
                number = flight['flightsectors'][0]['flightNumber']
                flightNumber = f"{carrierCode} {number}"
                availableSeats = flight["journeySummary"]["availableSeats"]
                isCheapest = flight["isCheapest"]
                airportTax = flight["airportTax"]
                originalAirportTax = flight["originalAirportTax"]
                bookingFee = flight["bookingFee"]
                originalBookingFee = flight["originalBookingFee"]
                isOriginalBooking = flight["isOriginalBooking"]
                flightKey = f"{flightNumber}_{departureDate}"
                data_to_csv([
                    flightKey,
                    flightNumber,
                    today,
                    departureAirportCode,
                    departureAirportName,
                    departureCountryCode,
                    departureDate,
                    departureTime,
                    arrivalAirportCode,
                    arrivalAirportName,
                    arrivalCountryCode,
                    arrivalDate,
                    arrivalTime,
                    adultPrice,
                    originalAdultPrice,
                    journeyType,
                    journeyDuration,
                    totalNumberOfStops,
                    carrierCode,
                    carrierName,
                    availableSeats,
                    isCheapest,
                    airportTax,
                    originalAirportTax,
                    bookingFee,
                    originalBookingFee,
                    isOriginalBooking
                    ], today)
        except:
            print("An error has occured in get_useful_data()") 

def start():
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    init_csv(today)
    DESTINATION = ['CFU','HER','RHO','BDS','NAP','PMO','FAO','ALC','IBZ','AGP','PMI','TFS']
    for depDate in pd.date_range(start='2023-04-01', end='2023-10-1', freq='7D'):
        for destination in DESTINATION:
            url = f'http://www.tuifly.be/flight/nl/search?flyingFrom%5B%5D=BRU&flyingTo%5B%5D={destination}&depDate={depDate.strftime("%Y-%m-%d")}&adults=1&children=0&childAge=&choiceSearch=true&searchType=pricegrid&nearByAirports=true&currency=EUR&isOneWay=true'
            raw_data = get_raw_data(url)
            if raw_data:
                get_useful_data(raw_data, today)

start()