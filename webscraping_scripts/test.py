from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import time
import csv
from datetime import date
from fake_useragent import UserAgent
from selenium_stealth import stealth
import gzip
import io
import datetime
import json

PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

DESTINATION_ARRAY = ["kerkyra", "heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
                     "malaga", "palma-de-mallorca", "tenerife"]

HEADERS = ['scrapeDate', 'departureAirportCode', 'departureAirportName', 'departureCountryCode', 'arrivalAirportCode', 'arrivalAirportName', 'arrivalCountryCode',
           'duration', 'aantalTussenstops', 'availableSeats', 'flightNumber', 'carrierCode', 'carrierName', 'departureDate', 'departureTime', 'arrivalDate', 'arrivalTime', 'totalPrice', 'taxIncludedInPrice']

# Instantiate a UserAgent object
user_agent = UserAgent()

# Driver
selenium_wire_options = {
    'verify_ssl': False,
    'accept_insecure_certs': True,
}

options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'user-agent={user_agent.chrome}')
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
driver_service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=driver_service,
                          options=options, seleniumwire_options=selenium_wire_options)
stealth(driver,
        languages=["nl-NL", "nl"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
driver.maximize_window()
driver.implicitly_wait(25)


def driver_init(datecsv, dest):
    url = f"https://www.brusselsairlines.com/lhg/be/nl/o-d/cy-cy/brussel-{dest}"

    driver.get("https://www.google.com")
    time.sleep(2)
    driver.get(url)
    # EERSTE PAGINA, hierna wordt datum veranderd bij de pagina met prijzen
    # Cookie accept
    try:
        driver.find_element(By.ID, "cm-acceptAll").click()
    except:
        pass

    time.sleep(2)

    # Doorgaan drukken
    driver.find_element(By.CLASS_NAME, "active-hidden").click()

    time.sleep(2)

    # Enkele vluchtaanduiden
    driver.find_element(
        By.XPATH, "//label[contains(text(), 'Alleen enkele vlucht')]").click()

    time.sleep(2)

    # Datum selecteren
    driver.find_element(By.ID, "departureDate").click()
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "move-forward").click()
    time.sleep(2)
    driver.find_element(
        By.CSS_SELECTOR, '[data-date="1"][data-month="3"][data-year="2023"]').click()

    time.sleep(2)

    # "Vlucht zoeken" drukken
    driver.find_element(By.ID, "searchFlights").click()

    # Nework request opvangen
    time.sleep(10)
    for i in driver.requests:
        if "air-bounds" in i.path:
            body = i.response.body
            body_str = gzip.GzipFile(
                fileobj=io.BytesIO(body)).read().decode('utf-8')
            body_dict = json.loads(body_str)
            print(body_dict)

            data = body_dict["data"]["airBoundGroups"]
            dictLocatie = body_dict["dictionaries"]["location"]
            dictAirline = body_dict["dictionaries"]["airline"]
            dictFlight = body_dict["dictionaries"]["flight"]

            for vlucht in data:
                # print(vlucht)
                departureAirportCode = vlucht["boundDetails"]["originLocationCode"]
                departureAirportName = dictLocatie[departureAirportCode]["airportName"]
                departureCountryCode = dictLocatie[departureAirportCode]["countryCode"]

                arrivalAirportCode = vlucht["boundDetails"]["destinationLocationCode"]
                arrivalAirportName = dictLocatie[arrivalAirportCode]["airportName"]
                arrivalCountryCode = dictLocatie[arrivalAirportCode]["countryCode"]

                hours = vlucht["boundDetails"]["duration"] // 3600
                minutes = (vlucht["boundDetails"]["duration"] % 3600) // 60
                duration = f"{hours:02d}:{minutes:02d}"
                aantalTussenstops = len(vlucht["boundDetails"]["segments"]) - 1
                availableSeats = vlucht["airBounds"][0]["availabilityDetails"][0]["quota"]
                departureFlightId = vlucht["boundDetails"]["segments"][0]["flightId"]
                # print(departureFlightId)
                print(dictFlight[departureFlightId])
                print()

                if "operatingAirlineName" in dictFlight[departureFlightId]:
                    carrierCode = 'SN'
                    carrierName = dictFlight[departureFlightId]["operatingAirlineName"]
                else:
                    carrierCode = dictFlight[departureFlightId]["operatingAirlineCode"]
                    carrierName = dictAirline[carrierCode]
                flightNumber = carrierCode + \
                    dictFlight[departureFlightId]["marketingFlightNumber"]
                departureDate, departureTime = dictFlight[departureFlightId]["departure"]["dateTime"].split(
                    "T")

                arrivalflightId = vlucht["boundDetails"]["segments"][-1]["flightId"]
                arrivalDate, arrivalTime = dictFlight[arrivalflightId]["arrival"]["dateTime"].split(
                    "T")

                # if carrierCode == 'CITYJET FOR BRUSSELS AIRLINES':
                #     carrierName = 'CITYJET FOR BRUSSELS AIRLINES'
                # else:
                #     carrierName = dictAirline[carrierCode]
                # departureDate = datetime.datetime.strptime(
                #     flightId[-15:], "%Y-%m-%d-%H%M").strftime("%Y-%m-%dT%H:%M:%S")
                totalPrice = vlucht["airBounds"][0]["prices"]["totalPrices"][0]["total"] / 100
                taxIncludedInPrice = vlucht["airBounds"][0]["prices"]["totalPrices"][0]["totalTaxes"] / 100

                if carrierCode == 'SN' or carrierCode == 'CITYJET FOR BRUSSELS AIRLINES':
                    data_to_csv([datecsv, departureAirportCode, departureAirportName, departureCountryCode, arrivalAirportCode, arrivalAirportName, arrivalCountryCode,
                                 duration, aantalTussenstops, availableSeats, flightNumber, carrierCode, carrierName, departureDate, departureTime, arrivalDate, arrivalTime, totalPrice, taxIncludedInPrice], datecsv)


def veranderDatum():
    tabList = driver.find_element(By.CLASS_NAME, "tabList")
    items = tabList.find_elements(By.CLASS_NAME, "calendarItem")
    if items[4].get_attribute("class") == "calendarItem noAvail ng-star-inserted":
        if items[5].get_attribute("class") == "calendarItem noAvail ng-star-inserted":
            if items[6].get_attribute("class") == "calendarItem noAvail ng-star-inserted":
                driver.find_element(
                    By.CSS_SELECTOR, ".container.smile .label").click()
                current = int(driver.find_element(
                    By.CSS_SELECTOR, ".day.starting").get_attribute('innerHTML'))
                current += 4
                driver.find_element(
                    By.CSS_SELECTOR, f".day.day{current}").click()
                driver.find_element(
                    By.CSS_SELECTOR, ".newSearchButton.secondary.ng-tns-c63-0").click()
            else:
                items[6].click()
        else:
            items[5].click()
    else:
        items[4].click()
    del items


def init_csv(date):
    url = f'data/bruair/BruAirScrapeData_{date}.csv'
    with open(url, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)

# append a row of data to the csv file


def data_to_csv(data, date):
    url = f'./data/bruair/BruAirScrapeData_{date}.csv'
    with open(url, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def start():
    today = date.today()
    init_csv(today)
    driver_init(today, DESTINATION_ARRAY[9])
    veranderDatum()


start()

# driver_init(DESTINATION_ARRAY[9])
