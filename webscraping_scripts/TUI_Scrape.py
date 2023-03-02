from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
# from webdriver_manager.chrome import ChromeDriverManager 
import json, requests, re, datetime, csv

def get_raw_data(url):
        PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument('--ignore-certificate-errors')
        driver_service = Service(executable_path=PATH)
        driver = webdriver.Chrome(service=driver_service,options=options)
        driver.maximize_window()
        driver.implicitly_wait(25)
        driver.get(url)

        driver.find_element(By.CSS_SELECTOR, "#cmCloseBanner").click()

        WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#page div.container footer > script"))
        )

        result = driver.find_element(By.CSS_SELECTOR, "div#page div.container footer > script").get_attribute('innerHTML')
        driver.close()
        if result is None:
            return
        match = re.search(r'window\.dataLayer\.push\(({.*})\);', result)

        if match:
            json_data = match.group(1)
            return json.loads(json_data)

def get_dates():
    dates = []
    for month in range(4, 11):
        for day in range(1, 32):
            try:
                date = datetime.date(2023, month, day)
                if date >= datetime.date(2023, 4, 1) and date <= datetime.date(2023, 10, 1):
                    dates.append(date.strftime("%Y-%m-%d"))
            except ValueError:
                pass
    return dates

def init_csv():
    COLUMNS=['origin','destination','departtime','arrivaltime','duration','price','daysToDeparture','directOrIndirectFlight']
    with open('data/tuiFlyScrapeData.csv', 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(COLUMNS)

def get_useful_data(raw_data, date):
    departureAirportCodes = raw_data["page"]["search"]["departureAirportCodes"]
    arrivalAirportCodes = raw_data["page"]["search"]["arrivalAirportCodes"]
    for flight in raw_data["page"]["search"]["resultList"]["outboundFlights"]:
        if flight["departureDate"] == date:
            departureDate = flight["departureDate"] + "T" + flight["departureTime"] + ":00:000"
            arrivalDate = flight["arrivalDate"] + "T" + flight["arrivalTime"] + ":00:000"
            duration_str = flight["flightDuration"]
            hours, minutes = int(duration_str.split("u ")[0]), int(duration_str.split("u ")[1].replace("m", ""))
            duration_formatted = f"{hours:02}:{minutes:02}"
            price = flight["price"]["currentPrice"]
            directOrIndirectFlight = flight["directOrIndirectFlight"]
            daysToDeparture = flight["daysToDeparture"]
            data_to_csv([departureAirportCodes,arrivalAirportCodes,departureDate,arrivalDate,duration_formatted,price,daysToDeparture,directOrIndirectFlight])

def data_to_csv(data):
    with open('data/tuiFlyScrapeData.csv', 'a', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(data)

def start():
    init_csv()
    ORIGIN = ['BRU', 'OST', 'ANR', 'LGG']
    DESTINATION = ['CFU','HER','RHO','BDS','NAP','PMO','FAO','ALC','IBZ','AGP','SPC','TFS']
    for date in get_dates():
        for origin in ORIGIN:
            for destination in DESTINATION:
                url = f'http://www.tuifly.be/flight/nl/search?flyingFrom%5B%5D={origin}&flyingTo%5B%5D={destination}&depDate={date}&adults=1&children=0&childAge=&choiceSearch=true&searchType=pricegrid&nearByAirports=false&currency=EUR&isOneWay=true'
                raw_data = get_raw_data(url)
                get_useful_data(raw_data, date)

start()