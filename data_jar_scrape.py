import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
import string
import pyodbc

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def run_datajar_scrape():
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "tcp:chubak-sql.database.windows.net,1433"
    database = "marketing_scrape"
    username = "chubak"
    password = "LAsvegas11"

    connection_string = 'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}' \
        .format(driver=driver, server=server, database=database, username=username, password=password)

    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()

    print("Connection made")

    try:
        cursor.execute("""CREATE TABLE DataJarScrapeFin(
                       CompanyTitle text,
                       CompanyEmployeeNum text,
                       CompanyIndustry text,
                       CompanyLocation text,
                       CompanyLogoUrl text,
                       CompanySite text,
                       CompanyTechUsed text,
                       CompanyTopTechs text,
                       CompanyContacts text,
                       CompanySocial text,
                       CompanyDataJarUrl text)""")
        cnxn.commit()
    except:
        print("Table already exists.")
    else:
        print("Table created.")

    index_url = "https://drive.google.com/uc?export=download&id=11RPDXkQvY7WT-COVtaOEj-DDVoVe5vU_"

    req_index = requests.get(index_url)
    letter_index = req_index.content.decode("utf-8").split(";")[0]
    num_index = req_index.content.decode("utf-8").split(";")[1]

    alphabet = {}
    uppercase_letters = string.ascii_uppercase

    for char in uppercase_letters[uppercase_letters.index(letter_index):]:
        alphabet[char] = char

    for alpha in alphabet:
        for i in range(int(num_index), 80):
            print(f"Checking {alpha}-{i}")

            try:
                req = requests.get(f"http://datajar.io/directory/companies/{alpha}-{i}", verify=False)
            except:
                print(f"{alpha}-{i} failed. Continuing")
                continue

            if req.status_code == 200:
                print("Gotcha!")
                soup = BeautifulSoup(req.content, 'html.parser')

                ul = None
                lis = None

                try:
                    ul = soup.find('ul', {'class': 'name_nav'})

                    lis = ul.find_all('li')
                except:
                    print("Failed to find name_nav")
                    continue

                urls = []

                for li in lis:
                    try:
                        urls.append(li.a['href'])
                    except:
                        continue

                for url in urls:
                    try:
                        req_url = requests.get("https://datajar.io" + url, verify=False)
                    except:
                        print('Url get failed')
                        continue

                    soup_url = BeautifulSoup(req_url.content, 'html.parser')

                    company_info = soup_url.find('div', {'class': 'people_detail_body'})

                    img = ""
                    company_title = ""
                    ps = None
                    employee_count = ""
                    industry = ""
                    location = ""
                    company_url = ""
                    tech_used = ""

                    try:
                        img = soup_url.find('img', {'class': 'profile_pic'})['src']
                        company_title = company_info.h6.get_text()
                        ps = company_info.find_all('p')
                        employee_count = ps[0].get_text()
                        industry = ps[1].get_text()
                        location = ps[2].get_text()
                        company_url = ps[3].get_text()
                        tech_used = ps[4].get_text()
                    except:
                        print("Some info scrape failed")

                    tech_p = []

                    social_str = ""

                    try:

                        socials_div = soup_url.find('div', {'class': 'social_icons'})

                        social_as = socials_div.find_all('a')

                        social = [a['href'] for a in social_as]

                        social_str = ", ".join(social)

                    except:
                        print("No social URLs")

                    try:
                        company_top_techs = soup_url.find('div', {'class': 'company_info_container'})

                        tech_containers = company_top_techs.find_all('div', {'class': 'tect_icon_div_container'})

                        for tech in tech_containers:
                            tech_p.append(tech.find('p').get_text())
                    except:
                        print('No techs')
                        continue

                    contact_names = []

                    try:
                        other_details = soup_url.find('div', {'class': 'others_detail_container'})

                        contact_ul = other_details.find('ul')

                        contact_lis = contact_ul.find_all('li')

                        for li in contact_lis:
                            name = li.span.a.get_text()
                            title = li.p.get_text()

                            contact_names.append((name, title))

                    except:
                        print("Contacts not found.")

                    print(f"Image: {img}, title: {company_title},"
                          f" employee_count: {employee_count}, "
                          f"industry: {industry}, "
                          f"location: {location}, url: {company_url}, "
                          f"tech_used: {tech_used}, top_techs; {', '.join(tech_p)}, "
                          f"contacts: {', '.join([': '.join(contact_name) for contact_name in contact_names])}")

                    try:
                        cursor.execute("""INSERT INTO DataJarScrapeFin(
                       CompanyTitle,
                       CompanyEmployeeNum,
                       CompanyIndustry,
                       CompanyLocation,
                       CompanyLogoUrl,
                       CompanySite,
                       CompanyTechUsed,
                       CompanyTopTechs,
                       CompanyContacts,
                       CompanySocial,
                       CompanyDataJarUrl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (company_title,
                                                                                         employee_count,
                                                                                         industry,
                                                                                         location,
                                                                                         img,
                                                                                         company_url,
                                                                                         tech_used,
                                                                                         ','.join(tech_p),
                                                                                         ', '.join(
                                                                                             [': '.join(contact_name)
                                                                                              for
                                                                                              contact_name in
                                                                                              contact_names]),
                                                                                         social_str,
                                                                                         "https://datajar.io" + url
                                                                                         ))

                        cnxn.commit()
                    except:
                        print("Insert failed.")
                    else:
                        print("Insert successful")


if __name__ == "__main__":
    run_datajar_scrape()
