from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_ip_rotator import ApiGateway
import requests
import pandas as pd
import time
import gzip
import io
import json
import csv
import datetime

s = ["heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
     "malaga", "palma-de-mallorca", "tenerife"]
DESTINATION_ARRAY = ["kerkyra"]
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

stealth(driver,
        languages=["nl-NL", "nl"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# URL's joinen, cookies accepteren, datum / vlucht selecteren


def driver_init(dest, dag=1, maand=3):
    # URL's
    url = f"https://www.brusselsairlines.com/lhg/be/nl/o-d/cy-cy/brussel-{dest}"

    with ApiGateway(url) as g:
        session = requests.Session()
        session.mount(url, g)

        response = session.get(url=url, headers=HEADERS)
        print(response.status_code)

    # driver.get("https://www.google.com")
    time.sleep(2)
    driver.get(url)

    try:
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
        for _ in range(3, maand):
            driver.find_element(By.CLASS_NAME, "move-forward").click()
            time.sleep(2)
        time.sleep(2)
        hulp_str = f'[data-date="{dag}"][data-month="{maand}"][data-year="2023"]'
        driver.find_element(
            By.CSS_SELECTOR, hulp_str).click()
        time.sleep(2)
        driver.find_element(By.ID, "searchFlights").click()
        time.sleep(5)
    except:
        reset_proces_from_date(dest, date.today())
# Data ophalen uit network requests


def get_data(datecsv):
    for request in driver.requests:
        body_dict = {}
        if request.response and "air-bounds" in request.path and driver.find_element(By.CSS_SELECTOR, ".refx-title.title").text != "Geen vluchten gevonden":
            body = request.response.body
            try:
                body_str = gzip.GzipFile(
                    fileobj=io.BytesIO(body)).read().decode('utf-8')
                body_dict = json.loads(body_str)
            except:
                pass

            if len(list(body_dict)) >= 1 and list(body_dict.keys())[0] != 'errors':
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
                    aantalTussenstops = len(
                        vlucht["boundDetails"]["segments"]) - 1
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
        else:
            pass

# hulp functies


def month_to_number(month_string):
    month_map = {
        'april': 3,
        'mei': 4,
        'juni': 5,
        'juli': 6,
        'augustus': 7,
        'september': 8,
    }
    return month_map[month_string.lower()]


def day_add_validate(day, month):
    if day == 30 and month in [3, 5, 8]:
        return False
    elif day == 31 and month in [2, 4, 6, 7]:
        return False
    return True

# verander datum


def veranderDatum(dest):
    wait = WebDriverWait(driver, 100)
    container = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".carousel:first-of-type")))
    items = container.find_elements(By.TAG_NAME, "button")
    innerText4 = items[4].text
    innerText5 = items[5].text
    innerText6 = items[6].text
    if "Geen tarieven" in innerText4 or "Uitverkocht" in innerText4:
        if "Geen tarieven" in innerText5 or "Uitverkocht" in innerText5:
            if "Geen tarieven" in innerText6 or "Uitverkocht" in innerText6:
                try:
                    full_items = container.find_elements(By.TAG_NAME, "li")
                    dag_str = full_items[6].find_element(
                        By.CSS_SELECTOR, ".refx-body-1.cell-content-bottom .ng-star-inserted span").text.split()
                    dag = int(dag_str[1])
                    time.sleep(2)
                    maand_str = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".selected-date"))).text.split()
                    maand = month_to_number(maand_str[2])
                    if day_add_validate(dag, maand):
                        dag += 1
                    else:
                        dag = 1
                        maand += 1
                    driver_init(dest, dag, maand)
                except:
                    reset_proces_from_date(dest, date.today())
            else:
                items[6].click()
        else:
            items[5].click()
    else:
        items[4].click()
    del items

# csv init


def init_csv(date):
    url = f'data/bruair/BruAirScrapeData_{date}.csv'
    with open(url, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)

# duplicate verwijderen uit csv


def drop_duplicates(date):
    url = f'data/bruair/BruAirScrapeData_{date}.csv'
    df = pd.read_csv(url)
    df.drop_duplicates(inplace=True)
    df.to_csv(url, index=False)

# data naar csv


def data_to_csv(data, date):
    url = f'./data/bruair/BruAirScrapeData_{date}.csv'
    with open(url, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# start (gebeurt 1x)


def start(dest):
    today = date.today()
    init_csv(today)
    driver_init(dest)

# functies die na start komen en meerdere malen in loop worden uitgevoerd


def proces(dest):
    today = date.today()
    time.sleep(5)
    get_data(today)
    time.sleep(5)
    veranderDatum(dest)
    time.sleep(5)
    driver.refresh()
    time.sleep(5)

# bij fouten in proces word de driver gereset en proces gaat verder vanaf de laatste datum in csv


def reset_proces_from_date(dest, date):
    df = pd.read_csv(
        f'./data/bruair/BruAirScrapeData_{date}.csv')
    drop_duplicates(date)
    last_row = df.tail(1)
    last_departure_date = last_row['departureDate'].iloc[0]
    date_object = datetime.datetime.strptime(
        last_departure_date, '%Y-%m-%d')
    driver_init(dest, date_object.day, date_object.month)

# loop


for j in DESTINATION_ARRAY:
    curr_date = date.today()
    start(j)
    try:
        datum = str(driver.find_element(
            By.CSS_SELECTOR, ".selected-date").text)
    except:
        reset_proces_from_date(j, curr_date)
    while datum not in ("maandag 2 oktober 2023", "dinsdag 3 oktober 2023", "woensdag 4 oktober 2023", "donderdag 5 oktober 2023"):
        try:
            proces(j)
        except:
            reset_proces_from_date(j, curr_date)

# drop duplicates op einde van loop
drop_duplicates(date.today())
