from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium_stealth import stealth


PATH = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"


# Driver
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("detach", True)
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_extension(
    r"C:\Users\buyse\AppData\Local\Google\Chrome\User Data\Default\Extensions\mpbjkejclgfgadiemmefgebjfooflfhl\2.0.1_0.crx")
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
# navigeren naar home page

DESTINATIONS_ARRAY = ["Heraklion", "Faro", "Rhodos", "Alicante", "Ibiza",
                      "Malaga", "Palma-de-mallorca", "Tenerife"]

MONTH_ARRAY = ['april 2023', 'mei 2023', 'juni 2023',
               'juli 2023', 'augustus 2023', 'september 2023', 'oktober 2023']


def navigate_excessive_search():
    driver.get(url="https://www.transavia.com/nl-BE/home/")
    link = driver.find_element(By.PARTIAL_LINK_TEXT, "Uitgebreid")
    link.click()

    # Brussel selecteren als start
    time.sleep(5)
    parent = driver.find_element(
        By.CSS_SELECTOR, ".HV-gs-type-e--bp0 .HV-gc .HV-gs-type-e--bp0 .textfield")
    bestemming = parent.find_element(
        By.TAG_NAME, "input")
    time.sleep(5)
    bestemming.clear()
    bestemming.send_keys("brussel")
    time.sleep(2)
    bestemming.send_keys(Keys.ARROW_DOWN)
    bestemming.send_keys(Keys.ENTER)
    time.sleep(2)

    # Bestemmingen toevoegen
    # add_dest_button = driver.find_element(
    #     By.XPATH, '//*[@id="alternativesearch"]/div[2]/div[2]/div/div[2]/div/button')
    # for _ in range(10):
    #     add_dest_button.click()
    #     time.sleep(2)

    # parent voor bestemmingen
    # parent = driver.find_element(
    #     By.XPATH, '//*[@id="alternativesearch"]/div[2]/div[2]/div/div[2]/div')
    # children = parent.find_elements(By.CLASS_NAME, "HV-gs-type-e--bp0")
    # print(children)
    # print(f"\n\n{len(children)}")
    # for i in range(0, len(children)):
    #     print(children[i].get_attribute("innerHTML"))
    #     time.sleep(5)
    #     children[i].click()
    #     time.sleep(5)
    #     bestemming = children[i].find_element(By.CLASS_NAME, "textfield")
    #     time.sleep(5)
    #     bestemming.send_keys(DESTINATIONS_ARRAY[i])
    #     time.sleep(4)
    #     bestemming.send_keys(Keys.ARROW_DOWN)
    #     bestemming.send_keys(Keys.ENTER)
    #     time.sleep(2)

    for element in DESTINATIONS_ARRAY:
        # bestemming kiezen
        parent = driver.find_element(
            By.CSS_SELECTOR, ".HV-gs-type-e--bp0 .HV-gc .HV-gs-type-e--bp0:nth-of-type(2)")
        bestemming = parent.find_element(
            By.XPATH, '//*[@id="countryStationSelection_Destination-input"]')
        time.sleep(5)
        bestemming.clear()
        time.sleep(2)
        bestemming.send_keys(element)
        time.sleep(2)
        bestemming.send_keys(Keys.ARROW_DOWN)
        bestemming.send_keys(Keys.ENTER)
        time.sleep(2)

        # enkele vlucht aanduiden
        if element == 'Heraklion':
            driver.find_element(
                By.XPATH, '//*[@id="alternativesearch"]/div[4]/div[1]/div[2]/h3').click()
        time.sleep(5)
        enkele = driver.find_element(By.NAME, 'timeFrameSelection.FlightType')
        time.sleep(2)
        enkele.click()
        time.sleep(2)
        enkele.send_keys(Keys.ARROW_DOWN)
        enkele.send_keys(Keys.ENTER)

        # maand aanduiden
        for maand in MONTH_ARRAY:
            time.sleep(5)
            month = Select(driver.find_element(
                By.ID, "timeFrameSelection_SingleFlight_SpecificMonth"))
            month.select_by_visible_text(maand)
            time.sleep(5)
            driver.find_element(
                By.XPATH, '//*[@id="alternativesearch"]/div[6]/div[2]/button').click()
            time.sleep(5)
            driver.find_element(By.XPATH, '//*[@id="HER"]/button[1]').click()
            time.sleep(5)

        data = driver.find_element(
            By.CSS_SELECTOR, ".bulletless.list.AS-destinations-list")
        print(data.__getattribute__("innerHTML"))


navigate_excessive_search()

driver.close()
