from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import csv
from csv import DictReader

DESTINATION_ARRAY = ["kerkyra", "heraklion", "rhodes", "brindisi", "napels", "palermo", "faro", "alicante", "ibiza",
                     "malaga", "palma-de-mallorca", "tenerife"]

HEADERS = ["datum", "vertrek-aankomst", "stop_0", "stop_1", "stop_2",
           "aantal_tussenstops", "vluchtduur", "prijs", "stoelen_beschikbaar"]


def init_csv():
    with open('data/transaviaScrapeData.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)


### CAPTCHA CODE EERST HIERONDER
#aanmaken webdriver + ophale website
driver = webdriver.Chrome()
driver.get('https://www.google.com/recaptcha/api2/demo')

#acces cookies
def get_cookies_values(file):
    with open(file, encoding='utf-8-sig') as f:
        dict_reader = DictReader(f)
        list_of_dicts = list(dict_reader)
    return list_of_dicts

#store cookies van transavia webpagina
cookies = get_cookies_values("test_cookies.csv")

#pass cookies into browser
for i in cookies:
    driver.add_cookie(i)

#refresh browser
driver.refresh()
