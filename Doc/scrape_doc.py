import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from lxml.html.soupparser import fromstring

names = []
distances = []
address = []
phone = []


def scrape(driver):
    names_elem = driver.find_elements_by_xpath("//h2")

    distance_elem = driver.find_elements_by_xpath("//div[contains(text(), 'miles away')]")

    addresses_elem = driver.find_elements_by_xpath("//div[@data-cmp = 'address']")

    phone_elem = driver.find_elements_by_xpath("//div[@data-cmp = 'phoneNumber']")

    for name_elemt in names_elem:
        names.append(name_elemt.text)

    for dist_elem in distance_elem:
        distances.append(dist_elem.text)

    for addr_elem in addresses_elem:
        address.append(addr_elem.text)

    for phn_elem in phone_elem:
        phone.append(phn_elem.text)

    return True


url = "https://www.autotrader.com/car-dealers/washington+dc-20002?searchRadius=0&sortBy=relevance&numRecords=100&dma="

options = Options()
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('headless')
# options.add_argument("user-data-dir=/home/chubak/snap/chromium/common/chromium")
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--window-size=1420,1080')
driver = webdriver.Chrome(executable_path="./chromedriver", options=options)

driver.get(url)
time.sleep(50)
driver.save_screenshot("sc.png")
if scrape(driver):
    for i in range(6):
        driver.find_element_by_xpath('//a[@role = "button"]').click()
        time.sleep(40)
        scrape(driver)

df = pd.DataFrame({"names": names, "distances": distances, "addresses": address, "phones": phone})

df.to_csv("stuff.csv")
