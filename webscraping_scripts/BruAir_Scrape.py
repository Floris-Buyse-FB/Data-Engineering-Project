from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import time
import csv
from datetime import date

PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

DESTINATION_ARRAY = ["kerkyra", "heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
                     "malaga", "palma-de-mallorca", "tenerife"]

HEADERS = ["datum", "vertrek-aankomst", "stop_0", "stop_1", "stop_2",
           "aantal_tussenstops", "vluchtduur", "prijs", "stoelen_beschikbaar"]

# alle prijzen array
prijzen = []
totaalData = []

# dag van vandaag
today = date.today()
today = today.strftime("%Y-%m-%d")

# Driver
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
driver_service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=driver_service, options=options)
driver.maximize_window()
driver.implicitly_wait(25)


def driver_init(dest):
    url = f"https://www.brusselsairlines.com/lhg/be/nl/o-d/cy-cy/brussel-{dest}"

    driver.get(url)
    # EERSTE PAGINA, hierna wordt datum veranderd bij de pagina met prijzen
    # Cookie accept
    try:
        driver.find_element(By.ID, "cm-acceptAll").click()
    except:
        pass

    # Doorgaan drukken
    driver.find_element(By.CLASS_NAME, "active-hidden").click()

    # Enkele vluchtaanduiden
    driver.find_element(
        By.XPATH, "//label[contains(text(), 'Alleen enkele vlucht')]").click()

    # Datum selecteren
    driver.find_element(By.ID, "departureDate").click()
    driver.find_element(By.CLASS_NAME, "move-forward").click()
    driver.find_element(
        By.CSS_SELECTOR, '[data-date="1"][data-month="3"][data-year="2023"]').click()

    # "Vlucht zoeken" drukken
    driver.find_element(By.ID, "searchFlights").click()


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


def scrapeOpDatum():
    # arrays om tijdelijke data op te slaan
    prijzenPerDatum = []
    restData = []

    # parent van rijen
    parent_row = driver.find_element(By.CLASS_NAME, "calendarGrid ")

    # rijen met alle data
    rows = parent_row.find_elements(By.CLASS_NAME, "row")

    for i in rows:

        alleText = i.text.splitlines()
        if alleText.__contains__('Brussels Airlines') or alleText.__contains__('CITYJET FOR BRUSSELS AIRLINES'):
            info = i.find_elements(By.CLASS_NAME, "info")
            prijs_en_stoel = i.find_elements(
                By.CSS_SELECTOR, ".cabins .cabin:first-of-type")

            for j in info:

                text = j.text.splitlines()

                # datum toevoegen aan restData
                datum = str(driver.find_element(
                    By.CSS_SELECTOR, ".container.selected .date").get_attribute('innerHTML'))
                pattern = r"\d{2}\.\d{2}\.\d{2}"
                match = re.search(pattern, datum)
                if match:
                    result = match.group()
                    text.insert(0, result)

                restData.append(text)

            for j in prijs_en_stoel:
                text = j.text.splitlines()
                prijzenPerDatum.append(text)

    prijzen.append(prijzenPerDatum)
    totaalData.append(restData)


# SCRAPE DATA
# Alle prijzen van april tot oktober 2023
for j in DESTINATION_ARRAY:
    driver_init(j)
    while str(driver.find_element(By.CSS_SELECTOR, ".container.selected .date").get_attribute('innerHTML')) != "zon 01.10.23":
        # for i in range(10):
        scrapeOpDatum()
        time.sleep(5)
        veranderDatum()
        time.sleep(5)


# DATA CLEANEN

# prijzen cleanen
for j in range(len(prijzen)):
    for i in range(len(prijzen[j])):
        prijzen[j][i][0] = prijzen[j][i][0].replace("EUR", "")
        prijzen[j][i][0] = prijzen[j][i][0].replace("vanaf", "")
        prijzen[j][i][0] = prijzen[j][i][0].strip()

        if len(prijzen[j][i]) == 2:
            aantal_stoelen = re.search(r'\d+', prijzen[j][i][1]).group()
            prijzen[j][i][1] = aantal_stoelen

# rest data cleanen
for j in range(len(totaalData)):
    for i in range(len(totaalData[j])):

        if len(totaalData[j][i]) == 8:
            totaalData[j][i][3] = totaalData[j][i][3].replace(
                "Stop(s)", "").strip()
            del totaalData[j][i][5:8]
            # 0 stops ==> 2x "-" toevoegen
            totaalData[j][i].insert(3, "-")
            totaalData[j][i].insert(4, "-")

        elif len(totaalData[j][i]) == 13 and totaalData[j][i][2] == "+ 1 dag":
            totaalData[j][i][5] = totaalData[j][i][5].replace(
                "Stop(s)", "").strip()
            del totaalData[j][i][7:13]
            # 1 stop ==> 1x "-" toevoegen
            totaalData[j][i].insert(5, "-")
            del totaalData[j][i][2]

        elif len(totaalData[j][i]) == 12:
            totaalData[j][i][4] = totaalData[j][i][4].replace(
                "Stop(s)", "").strip()
            del totaalData[j][i][6:12]
            # 1 stop ==> 1x "-" toevoegen
            totaalData[j][i].insert(4, "-")

        elif len(totaalData[j][i]) == 16:
            totaalData[j][i][5] = totaalData[j][i][5].replace(
                "Stop(s)", "").strip()
            del totaalData[j][i][7:16]

        elif len(totaalData[j][i]) == 17:
            totaalData[j][i][6] = totaalData[j][i][6].replace(
                "Stop(s)", "").strip()
            del totaalData[j][i][8:17]
            del totaalData[j][i][2]

        # prijzen bij rest data toevoegen
        totaalData[j][i].append(prijzen[j][i][0])
        if len(prijzen[j][i]) == 2:
            totaalData[j][i].append(prijzen[j][i][1])
        # aantal stoelen niet gekend ==> "-" toevoegen
        elif len(prijzen[j][i]) == 1:
            totaalData[j][i].append("-")


# DATA IN CSV

# create new csv file with data
path_to_csv = f'data/bruair/bruAirScrapeData-{today}.csv' 
with open(path_to_csv, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(HEADERS)
    for i in range(len(totaalData)):
        writer.writerows(totaalData[i])

driver.close()