import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from lxml.html.soupparser import fromstring

linked_in_links = [url.strip() for url in open("linked_ins_lusha.csv", "r").readlines()]



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

link = "https://www.linkedin.com/company/atlantis-computing"

driver.get("https://www.linkedin.com")

time.sleep(10)

df_cookies = pd.read_csv("cookies-www-linkedin-com.txt", sep="\t", header=None)

cookies_list = []

unlist = [

'li_rm',
'li_at',
]

unchecklist = ['bscookie', 'visit', 'trkCode', 'trkInfo', 'g_state', 'G_ENABLED_IDPS', 'JSESSIONID']


unlist_unremoved = ['bscookie',
'visit',
'trkCode',
'trkInfo',
'g_state',
'trkCode',
'trkInfo',
'G_ENABLED_IDPS',
'li_rm',
'li_at',
'JSESSIONID',
'UserMatchHistory']


driver.delete_all_cookies()

for i in range(df_cookies.shape[0]):
    if df_cookies.loc[i, 5] not in unlist:
        print(df_cookies.loc[i, 5])
        continue
    cookies_list.append({"name": df_cookies.loc[i, 5], "value": df_cookies.loc[i, 6]})


for cookie in cookies_list:
    driver.add_cookie(cookie)

driver.refresh()

time.sleep(20)

driver.get(link)

time.sleep(30)

driver.save_screenshot("lon.png")


driver.close()
driver.quit()
