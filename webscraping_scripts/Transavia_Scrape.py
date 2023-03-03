from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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

driver.get(url)


def delay(waiting_time=5):
    driver.implicitly_wait(waiting_time)


def solve_captcha():
    time.sleep(5)
    delay()
    # main iframe zoeken
    main_iframe = driver.find_element(By.ID, "main-iframe")
    driver.switch_to.frame(main_iframe)

    # eerste div container in iframe zoeken
    delay()
    time.sleep(5)
    container = driver.find_element(
        By.CSS_SELECTOR, ".form_container .g-recaptcha")

    # captcha iframe zoeken in container
    delay()
    time.sleep(5)
    captcha_iframe = container.find_element(By.TAG_NAME, "iframe")

    # switch naar captcha iframe
    driver.switch_to.frame(captcha_iframe)
    delay()
    time.sleep(5)
    # captcha checkbox aanklikken
    driver.find_element(By.CLASS_NAME, "recaptcha-checkbox").click()

    # switch terug naar main iframe
    driver.switch_to.default_content()
    main_iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(main_iframe)
    delay()
    time.sleep(5)

    # wanneer captcha aangeklikt is, switchen naar de captcha iframe
    divs = driver.find_elements(By.TAG_NAME, "div")
    captcha_iframe_div = divs[-1]
    iframe = captcha_iframe_div.find_element(By.CSS_SELECTOR, ":nth-child(1)")
    driver.switch_to.frame(iframe)
    delay()
    time.sleep(5)

    # find solve button
    try:
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
    except:
        print("No solve button found")


solve_captcha()
