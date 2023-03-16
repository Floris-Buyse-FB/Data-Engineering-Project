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


PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

DESTINATION_ARRAY = ["kerkyra", "heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
                     "malaga", "palma-de-mallorca", "tenerife"]

HEADERS = ["datum", "vertrek-aankomst", "stop_0", "stop_1", "stop_2",
           "aantal_tussenstops", "vluchtduur", "prijs", "stoelen_beschikbaar"]

# Instantiate a UserAgent object
user_agent = UserAgent()

# Driver
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'user-agent={user_agent.chrome}')
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
driver_service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=driver_service, options=options)
stealth(driver,
        languages=["nl-NL", "nl"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
options.backend = 'mitmproxy'
options.connection_timeout = None
driver.maximize_window()
driver.implicitly_wait(25)


def driver_init(dest):
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
            print(body_str)


driver_init(DESTINATION_ARRAY[9])
