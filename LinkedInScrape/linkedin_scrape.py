import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from lxml.html.soupparser import fromstring

linked_in_links = [url.strip() for url in open("linked_ins_lusha.csv", "r").readlines()]

ns = {"re": "http://exslt.org/regular-expressions"}

df_cookies = pd.read_csv("cookies-www-linkedin-com.txt", sep="\t", header=None)

cookies_list = []

for i in range(df_cookies.shape[0]):
    cookies_list.append({"name": df_cookies.loc[i, 5], "value": df_cookies.loc[i, 6]})

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

driver.get("https://www.linkedin.com")

for cookie in cookies_list:
    driver.add_cookie(cookie)

time.sleep(30)

driver.refresh()

time.sleep(30)

driver.get(linked_in_links[61])

time.sleep(20)

driver.save_screenshot("page61.png")

numbers = open("numbers.txt", "w")

reqs = 0

for i, url in enumerate(linked_in_links[:500]):

    try:
        req = requests.get(url)

        if req.status_code != 999:
            continue

        print(i)

        reqs += 1

        driver.get(url)

        root = fromstring(driver.page_source)

        try:
            href_text = root.xpath(
                  r'//a[re:match(.,"See all \d+.\d+ employees on LinkedIn", "i")]/@href', namespaces=ns)[0]

            last_element = href_text.split("=")[-1]

            numbers.write(f"{last_element}\n")

            print(last_element)
        except:
            driver.save_screenshot(f"{i}_failed.png")
            print("failed")
    except:
        continue

print(reqs)

driver.close()
driver.quit()
