import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import string
import re
import pyodbc

driver = "{ODBC Driver 17 for SQL Server}"
server = "tcp:chubak-sql.database.windows.net,1433"
database = "marketing_scrape"
username = "chubak"
password = "LAsvegas11"

connection_string = 'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}' \
    .format(driver=driver, server=server, database=database, username=username, password=password)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

try:
    cursor.execute("""CREATE TABLE AeroLeadsCompanies(
                   CompanyTitle nvarchar(MAX),
                   CompanyFounders nvarchar(MAX),
                   CompanyHeadquarters nvarchar(MAX),
                   CompanyIndustry nvarchar(MAX),
                   CompanyLocation nvarchar(MAX),                  
                   CompanySite nvarchar(MAX),
                   CompanyBlog nvarchar(MAX),
                   CompanySpecialties nvarchar(MAX),
                   CompanyFacebook nvarchar(MAX),
                   CompanyTwitter nvarchar(MAX),
                   CompanyLinkedIn nvarchar(MAX),
                   CompanyYoutube nvarchar(MAX),
                   CompanyEmailInfo text,
                   CompanyManagementInfo text,
                   CompanyEmployeeInfo text,
                   CompanyRoles text,
                   CompanyAeroLeadsUrl nvarchar(MAX))""")
    cnxn.commit()
except:
    print("Table already exists.")
else:
    print("Table created.")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('headless')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--window-size=1420,1080')
driver = webdriver.Chrome(options=options)

replacer = lambda rplc: rplc.replace('\xa0', '').replace('\n', '').strip()

splitter = lambda splt: splt.split(":")[-1]

last_index = open("last_index.txt", "r+")

req_index = last_index.readlines()[-1].strip()
letter_index = req_index.split(";")[0]
num_index = req_index.split(";")[1]

alphabet = {}
lowercase_letters = string.ascii_lowercase

for char in lowercase_letters[lowercase_letters.index(letter_index):]:
    alphabet[char] = char

pattern = re.compile(r"[\/a-z\d](?:[a-z\d_-]*[a-z\d\/])?")

for alpha in alphabet:
    for i in range(int(num_index), 400):
        req = requests.get(f"https://aeroleads.com/company/index-{alpha}-{i}.html")

        last_index.write(f"\n{alpha};{i}")

        print(f"Working on {alpha}-{i}")

        if req.status_code == 200:

            soup_dir = BeautifulSoup(req.content, 'html.parser')

            lis_listgroup_url = [li.h3.a['href'] for li in soup_dir.find_all('li', {'class': 'list-group-item'})]

            for url in lis_listgroup_url:
                print(f"driver getting url {url}")

                if not bool(pattern.search(url)):
                    print("Not a valid slug. Continuing...")
                    continue

                for j in range(50):
                    try:
                        driver.get("https://aeroleads.com" + url)

                        name = driver.find_element_by_class_name('company-name-header').find_element_by_tag_name(
                            'a').text
                        name = " ".join(name.split(" ")[:-2])

                        email_types = driver.find_elements_by_xpath(
                            '//table[contains(@class, "table-email-format")]/tbody/tr/td[1]')

                        email_examples = driver.find_elements_by_xpath(
                            '//table[contains(@class, "table-email-format")]/tbody/tr/td[2]')

                        email_percent = driver.find_elements_by_xpath(
                            '//table[contains(@class, "table-email-format")]/tbody/tr/td[3]')

                        print(email_percent)

                        company_emails = []

                        for type_, example, percent in zip(email_types, email_examples, email_percent):
                            company_emails.append(
                                (replacer(type_.text), replacer(example.text), replacer(percent.text)))

                        print(company_emails)

                        striped_roles = driver.find_elements_by_xpath(
                            '//div[contains(@id, "employeeList")]/table[contains(@class,'
                            ' "table-striped" )]/tbody/tr/td[1]/div/div/span')

                        striped_address = driver.find_elements_by_xpath('//div[contains(@id, "employeeList")]/'
                                                                        'table[contains(@class, "table-striped")]/tbody/tr/td[2]')

                        striped_found = driver.find_elements_by_xpath('//div[contains(@id, "employeeList")]/'
                                                                      'table[contains(@class, "table-striped")]/tbody/tr/td[3]')

                        company_employees = []

                        for role, address, found in zip(striped_roles, striped_address, striped_found):
                            company_employees.append(
                                (replacer(role.text), replacer(address.text), replacer(found.text)))

                        tab_info = driver.find_element_by_xpath('//a[contains(@href, "#conpanyInfomation")]').click()

                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        facebook_link = replacer(soup.find('a', {'class': 'fa-facebook'})['href'])
                        twitter_link = replacer(soup.find('a', {'class': 'fa-twitter'})['href'])
                        linkedin_link = replacer(soup.find('a', {'class': 'fa-linkedin'})['href'])
                        youtube_link = replacer(soup.find('a', {'class': 'fa-youtube'})['href'])

                        list_overview = soup.find('ul', {'class': 'list-overview'})

                        information = [replacer(li.get_text().strip()) for li in list_overview.find_all('li')]

                        tab_management = driver.find_element_by_xpath('//a[contains(@href, "management")]').click()

                        roles = {}

                        div = soup.find_all('div', {'class': 'col-sm-2'})

                        roles["CEO"] = replacer(div[1].span.get_text().strip())
                        roles["CTO"] = replacer(div[2].span.get_text().strip())
                        roles["CFO"] = replacer(div[3].span.get_text().strip())
                        roles["COO"] = replacer(div[4].span.get_text().strip())
                        roles["CMO"] = replacer(div[5].span.get_text().strip())

                        management_roles = driver.find_elements_by_xpath('//table[contains(@class,'
                                                                         ' "table-management" )]/tbody/tr/td[1]')

                        management_address = driver.find_elements_by_xpath(
                            '//table[contains(@class, "table-management")]/tbody/tr/td[2]')

                        management_found = driver.find_elements_by_xpath(
                            '//table[contains(@class, "table-management")]/tbody/tr/td[3]')

                        company_management = []

                        for role, address, found in zip(management_roles, management_address, management_found):
                            company_management.append(
                                (replacer(role.text), replacer(address.text), replacer(found.text)))

                        email_str = '\n'.join([' -> '.join(list(em)) for em in company_emails])
                        employee_str = '\n'.join([' -> '.join(list(emp)) for emp in company_employees])
                        management_str = '\n'.join([' -> '.join(list(man)) for man in company_management])
                        roles_str = '\n'.join([f"{role}: {roles[role]}" for role in roles])

                        location = splitter(information[0])
                        founders = splitter(information[1])
                        founded = splitter(information[2])
                        industry = splitter(information[3])
                        headquarters = splitter(information[4])
                        website = splitter(information[5])
                        blog = splitter(information[6])
                        specialties = splitter(information[7])

                        try:
                            cursor.execute("""INSERT INTO AeroLeadsCompanies(
                                           CompanyTitle,
                                           CompanyFounders,
                                           CompanyHeadquarters,
                                           CompanyIndustry,
                                           CompanyLocation,                  
                                            CompanySite,
                                           CompanyBlog,
                                           CompanySpecialties,
                                           CompanyFacebook,
                                           CompanyTwitter,
                                           CompanyLinkedIn,
                                            CompanyYoutube,
                                           CompanyEmailInfo,
                                           CompanyManagementInfo,
                                           CompanyEmployeeInfo,
                                           CompanyRoles,
                                           CompanyAeroLeadsUrl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                                           (name,
                                            founders,
                                            headquarters,
                                            industry,
                                            location,
                                            website,
                                            blog,
                                            specialties,
                                            facebook_link,
                                            twitter_link,
                                            linkedin_link,
                                            youtube_link,
                                            email_str,
                                            management_str,
                                            employee_str,
                                            roles_str,
                                            "https://aeroleads.com" + url
                                            ))

                            cnxn.commit()
                        except:
                            print("Insert failed.")
                        else:
                            print("Insert successful")

                    except:
                        continue
                    else:
                        break

driver.close()
driver.quit()
