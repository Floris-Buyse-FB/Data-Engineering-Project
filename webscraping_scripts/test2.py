from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from datetime import date
import time
import gzip
import io
import json
import csv

DESTINATION_ARRAY = ["kerkyra", "heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
                     "malaga", "palma-de-mallorca", "tenerife"]
HEADERS = ['scrapeDate', 'departureAirportCode', 'departureAirportName', 'departureCountryCode', 'arrivalAirportCode', 'arrivalAirportName', 'arrivalCountryCode',
           'duration', 'aantalTussenstops', 'availableSeats', 'flightNumber', 'carrierCode', 'carrierName', 'departureDate', 'departureTime', 'arrivalDate', 'arrivalTime', 'totalPrice', 'taxIncludedInPrice']

# driver options
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-application-cache')
options.add_argument('--disable-cache')

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.implicitly_wait(25)

stealth(driver,
        languages=["nl-NL", "nl"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# URL's joinen, cookies accepteren, datum / vlucht selecteren


def driver_init(dest):
    # URL's
    url = f"https://www.brusselsairlines.com/lhg/be/nl/o-d/cy-cy/brussel-{dest}"
    driver.get("https://www.google.com")
    time.sleep(2)
    driver.get(url)

    # Cookie accept
    try:
        driver.find_element(By.ID, "cm-acceptAll").click()
    except:
        pass
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "active-hidden").click()
    time.sleep(2)

    # Vlucht kiezen en datum selecteren
    driver.find_element(
        By.XPATH, "//label[contains(text(), 'Alleen enkele vlucht')]").click()
    time.sleep(2)
    driver.find_element(By.ID, "departureDate").click()
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "move-forward").click()
    time.sleep(2)
    driver.find_element(
        By.CSS_SELECTOR, '[data-date="1"][data-month="3"][data-year="2023"]').click()
    time.sleep(2)
    driver.find_element(By.ID, "searchFlights").click()
    time.sleep(10)

# Data ophalen uit network requests


def get_data(datecsv):
    for request in driver.requests:
        if request.response and "air-bounds" in request.path:
            body = request.response.body
            body_str = gzip.GzipFile(
                fileobj=io.BytesIO(body)).read().decode('utf-8')
            body_dict = json.loads(body_str)

            data = body_dict["data"]["airBoundGroups"]
            dictLocatie = body_dict["dictionaries"]["location"]
            dictAirline = body_dict["dictionaries"]["airline"]
            dictFlight = body_dict["dictionaries"]["flight"]

            for vlucht in data:
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

                totalPrice = vlucht["airBounds"][0]["prices"]["totalPrices"][0]["total"] / 100
                taxIncludedInPrice = vlucht["airBounds"][0]["prices"]["totalPrices"][0]["totalTaxes"] / 100

                if carrierCode == 'SN' or carrierCode == 'CITYJET FOR BRUSSELS AIRLINES':
                    data_to_csv([datecsv, departureAirportCode, departureAirportName, departureCountryCode, arrivalAirportCode, arrivalAirportName, arrivalCountryCode,
                                 duration, aantalTussenstops, availableSeats, flightNumber, carrierCode, carrierName, departureDate, departureTime, arrivalDate, arrivalTime, totalPrice, taxIncludedInPrice], datecsv)


def veranderDatum():
    container = driver.find_element(
        By.CSS_SELECTOR, ".carousel:first-of-type")
    items = container.find_elements(By.TAG_NAME, "button")
    innerText4 = items[4].text
    innerText5 = items[5].text
    innerText6 = items[6].text
    if innerText4 == "Geen tarieven" or innerText4 == "Uitverkocht":
        if innerText5 == "Geen tarieven" or innerText5 == "Uitverkocht":
            if innerText6 == "Geen tarieven" or innerText6 == "Uitverkocht":
                # TODO: Als alle 3 geen tarieven zijn, dan moet er een nieuwe datum gekozen worden
                pass
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


def data_to_csv(data, date):
    url = f'./data/bruair/BruAirScrapeData_{date}.csv'
    with open(url, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def start():
    today = date.today()
    init_csv(today)
    time.sleep(2)
    get_data(today)
    time.sleep(5)
    veranderDatum()
    time.sleep(5)
    driver.refresh()
    time.sleep(7)


# TODO : Destination array loopen en range aanpassen
driver_init(DESTINATION_ARRAY[9])
for _ in range(3):
    start()
