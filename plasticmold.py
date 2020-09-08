import requests
from bs4 import BeautifulSoup
import pandas as pd

urls_file = open("plastic_urls", "r")

urls_unparsed = urls_file.readlines()

urls = [url.strip().split("/")[-2] for url in urls_unparsed]

logos = []
sites = []
titles = []
phones = []
addresses = []
infos = []
profile_urls = []

print(urls)

for url in urls:

    print(f"https://www.iqsdirectory.com/profile/{url}/")

    profile_urls.append(f"https://www.iqsdirectory.com/profile/{url}/")

    req = requests.get(f"https://www.iqsdirectory.com/profile/{url}/")

    soup = BeautifulSoup(req.content, 'html.parser')


    try:
        logo = soup.find('img', {'class': 'logo'})['src']
        logo_path = logo.split("/")[-1]
        logos.append(logo_path)
    except:
        logos.append("")



    try:
        site = soup.find('a', {'class': 'DPFCompanyResource1'})['href']
        sites.append(site)
    except:
        sites.append("")

    try:
        title = soup.h1.get_text()
        titles.append(title)
    except:
        titles.append("")

    try:
        phone = soup.find('div', {'id': 'divPhone'}).span.get_text()
        phones.append(phone)
    except:
        phones.append("")

    try:
        address_a = soup.find('a', {'class': 'iframe coproviewmap'})['href']
        address = address_a.split("?")[-1].replace("address=", "").split("&")[0]
        addresses.append(address)
    except:
        addresses.append("")

    try:
        desc = soup.find('div', {'itemprop': 'description'}).get_text()
        infos.append(desc)
    except:
        infos.append("")

df = pd.DataFrame({"Title": titles,
                   "Site": sites,
                   "Description": infos,
                   "Address": addresses,
                   "PhoneNumber": phones,
                    "ProfileUrl": profile_urls})

df.to_csv("plastic_data.csv")



