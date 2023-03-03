from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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
    r"C:\Users\buyse\AppData\Local\Google\Chrome\User Data\Default\Extensions\mpbjkejclgfgadiemmefgebjfooflfhl\2.0.1_0.crx")
driver_service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=driver_service, options=options)
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
