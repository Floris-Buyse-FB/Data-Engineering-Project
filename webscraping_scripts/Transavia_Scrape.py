from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import time
import random

PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"

# Driver
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_extension(
    r"C:\Users\emmad\AppData\Local\Google\Chrome\User Data\Default\Extensions\mpbjkejclgfgadiemmefgebjfooflfhl\2.0.1_0.crx")
driver_service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=driver_service, options=options)
action = ActionChains(driver)
driver.maximize_window()
driver.implicitly_wait(25)

url = "https://www.transavia.com/nl-BE/boek-een-vlucht/vluchten/zoeken/"


driver.get("https://www.gmail.com")
time.sleep(5)
driver.get(url)


def delay(waiting_time=5):
    driver.implicitly_wait(waiting_time)
    time.sleep(5)


def acces_main_i_frame():
    delay()
    main_iframe = driver.find_element(By.ID, "main-iframe")
    driver.switch_to.frame(main_iframe)



# CAPTCHA OPLOSSEN
def check_captcha():
    # main iframe zoeken
    acces_main_i_frame()

    # eerste div container in iframe zoeken
    delay()
    container = driver.find_element(
        By.CSS_SELECTOR, ".form_container .g-recaptcha")

    # captcha iframe zoeken in container
    delay()
    captcha_iframe = container.find_element(By.TAG_NAME, "iframe")

    # switch naar captcha iframe
    driver.switch_to.frame(captcha_iframe)
    delay()

    # captcha checkbox aanklikken
    driver.find_element(By.CLASS_NAME, "recaptcha-checkbox").click()
    driver.switch_to.default_content()


def acces_captcha_i_frame():

    # switch terug naar main iframe
    acces_main_i_frame()

    divs = driver.find_elements(By.TAG_NAME, "div")
    captcha_iframe_div = divs[-1]
    iframe = captcha_iframe_div.find_element(By.CSS_SELECTOR, ":nth-child(1)")
    driver.switch_to.frame(iframe)
    delay()


def click_solve_button():

    # boolean om te checken of captcha opgelost is
    captcha_solved = False

    # find solve button

    time.sleep(5)
    container = driver.find_element(By.ID, "rc-imageselect")
    controls = container.find_element(By.CLASS_NAME, "rc-controls")
    primary = controls.find_element(By.CLASS_NAME, "primary-controls")
    rc_buttons = primary.find_element(By.CLASS_NAME, "rc-buttons")
    time.sleep(5)
    help_button_holder = rc_buttons.find_element(
        By.CLASS_NAME, "help-button-holder")
    time.sleep(5)
    help_button_holder.click()
    time.sleep(5)
    try:
        if driver.find_element(By.CSS_SELECTOR, ".h3").get_attribute("innerHTML") == "Waar wil je heen?":
            captcha_solved = True
            print("captcha solved")
            return captcha_solved
    except:
        pass

    return captcha_solved


def solve_captcha():
    check_captcha()
    acces_captcha_i_frame()
    click_solve_button()


solve_captcha()



# DATA SCRAPEN
#navigeren naar home page

DESTINATIONS_ARRAY = ["Heraklion", "Rhodos", "Brindisi", "Napels", "Palermo", "Faro", "Alicante", "Ibiza",
                     "Malaga", "Palma-de-mallorca", "Tenerife"]

MONTH_ARRAY= ['april 2023', 'mei 2023', 'juni 2023', 'juli 2023', 'augustus 2023', 'september 2023', 'oktober 2023']

def navigate_excessive_search():
    driver.get(url="https://www.transavia.com/nl-BE/home/")
    link= driver.find_element(By.PARTIAL_LINK_TEXT, "Uitgebreid")
    link.click()
    
   
    for element in DESTINATIONS_ARRAY:
        #bestemming kiezen
        parent = driver.find_element(By.CSS_SELECTOR, ".HV-gs-type-e--bp0 .HV-gc .HV-gs-type-e--bp0:nth-of-type(2)")
        parent2 = parent.find_element(By.CSS_SELECTOR, '.textfield')
        bestemming = parent2.find_element(By.ID, "countryStationSelection_Destination-input")
        time.sleep(5)
        bestemming.send_keys(element)
        time.sleep(2)
        bestemming.send_keys(Keys.ARROW_DOWN)
        bestemming.send_keys(Keys.ENTER)
        time.sleep(2)
        #button=driver.find_element(By.XPATH, '//*[@id="alternativesearch"]/div[2]/div[2]/div/div[2]/div/button')
        #button.click()

        #enkele vlucht aanduiden
        driver.find_element(By.XPATH, '//*[@id="alternativesearch"]/div[4]/div[1]/div[2]/h3').click()
        time.sleep(5)
        enkele = driver.find_element(By.NAME, 'timeFrameSelection.FlightType')
        time.sleep(2)
        enkele.click()
        time.sleep(2)
        enkele.send_keys(Keys.ARROW_DOWN)
        enkele.send_keys(Keys.ENTER)

        #url_array
        urls_per_bestemming = []

        #maand aanduiden
        for maand in MONTH_ARRAY:
            time.sleep(5)
            month = Select(driver.find_element(By.ID, "timeFrameSelection_SingleFlight_SpecificMonth"))
            month.select_by_visible_text(maand)
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@id="alternativesearch"]/div[6]/div[2]/button').click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@id="HER"]/button[1]').click()
            time.sleep(5)


       
            #idee was om per bestemming url van vluchten te krijgen > die afgaan elke url volgen > via beautifoulsoup ding proberen p elementen om te zetten in json object
            #alle info is te vinden in die url (beetje gebaseerd op ryanair)
            #zit dus vast tho"
            #elements = [driver.find_elements(By.CSS_SELECTOR, 'p.text-align-right--bp25 > a')]
            #print(elements)
            #for element in elements:
             #   urls_per_bestemming += [element.__getattribute__('href')]
            #print(urls_per_bestemming)
          
            #print([my_elem.get_attribute("href") for my_elem in driver.find_elements(By.XPATH, '//*[@id="top"]/div/div/div[2]/div/div[2]/div/div/section/ol/li/div/div/section/ol/li[2]/div[3]/div/ol/li/div/div[1]/div/div[2]/div/div[2]/p/a')])

        #for link in urls_per_bestemming:



navigate_excessive_search()