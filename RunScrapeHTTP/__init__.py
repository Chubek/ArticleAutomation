import logging
import pyodbc
from bs4 import BeautifulSoup
import requests
import azure.functions as func
import os
import gspread
from google.oauth2.service_account import Credentials

def run_scrape():
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "tcp:chubak-sql.database.windows.net,1433"
    database = "marketing_scrape"
    username = "chubak"
    password = "LAsvegas11"

    connection_string = 'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}' \
        .format(driver=driver, server=server, database=database, username=username, password=password)

    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()

    cursor.execute("CREATE TABLE LushaCompanies("
                   "CompanyName varchar(400),"
                   "CompanyInfo text,"
                   "CompanyUrl varchar(255),"
                   "CompanyLogoUrl varchar(300),"
                   "CompanySite varchar(255),"
                   "CompanyFounded varchar(255),"
                   "CompanyEmployees varchar(255),"
                   "CompanyLeadNames text,"
                   "CompanyTwitter varchar(255),"
                   "CompanyLinkedIn varchar(255),"
                   "CompanyFacebok varchar(255),"
                   "CompanyPermutationTypes text,"
                   "CompanyPermutationExamples text,"
                   "CompanyPermutationPercentages text)")

    current_path = "/home/site/wwwroot"
    url_file = open(os.path.join(current_path, 'url_file.txt'), 'r')

    urls = [url.strip() for url in url_file.readlines()]

    lam = lambda x: "'" + x + "'"

    for i, url in enumerate(urls):
        print(f"Checking url {url}; {i} of {len(urls)}")
        for j in range(20):
            try:
                req = None
                try:
                    req = requests.get(url)
                except:
                    print("Url GET failed.")
                else:
                    print("Url get success")

                soup = BeautifulSoup(req.content, 'html.parser')

                company_name = ""

                try:
                    company_name = soup.h1.get_text()
                except:
                    print("Company name scrape failed. No company name.")
                else:
                    print("Name get success")

                leads = []
                lead_names = ""

                try:
                    lead_soup = soup.find_all("ul", {"class": "searches-list t"})

                    for lead in lead_soup:
                        lis = lead.find_all('li')
                        for li in lis:
                            try:
                                leads.append(f"{li.a.span.get_text()} | {li.a['href']}")
                            except:
                                continue
                    lead_names = ",".join(leads)
                except:
                    print("No leads.")
                else:
                    print("Leads get success")

                site = ""

                try:
                    site = soup.find('div', {'class': 'link'}).h2.a['href']
                except:
                    print("No site")
                else:
                    print("Site get success")

                founded = ""
                employees = ""

                try:
                    details = soup.find('dl', {'class': 'company-details'}).find_all('dd')

                    founded = details[0].get_text()
                    employees = details[1].get_text()

                except:
                    print("No founded or employees")

                else:
                    print("employee/founded get success")

                facebook_link = ""
                linkedin_link = ""
                twitter_link = ""

                try:
                    facebook_link = soup.find('a', {'class': 'facebook'})['href']
                except:
                    print("No Facebook")
                else:
                    print("Facebook get success")

                try:
                    linkedin_link = soup.find('a', {'class': 'linkedin'})['href']
                except:
                    print("No LinkedIn")
                else:
                    print("Linkedin get success")

                try:
                    twitter_link = soup.find('a', {'class': 'twitter'})['href']
                except:
                    print("No Twitter")
                else:
                    print("Twitter get success")

                perm_data = []

                perm_data_type_str = ""
                perm_data_ex_str = ""
                perm_data_percent_str = ""

                try:
                    table = soup.find('table')
                    table_body = table.find('tbody')

                    rows = table_body.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        cols = [ele.text.strip() for ele in cols]
                        perm_data.append([ele for ele in cols if ele])
                except:
                    print("No perm data")
                else:
                    print("Perm get success")

                perm_data_type = []
                perm_data_ex = []
                perm_data_percent = []

                for perm_datum in perm_data:
                    perm_data_type.append(perm_datum[0])
                    perm_data_ex.append(perm_datum[1])
                    perm_data_percent.append(perm_datum[2])

                try:
                    perm_data_type_str = ",".join(perm_data_type)
                    perm_data_ex_str = ",".join(perm_data_ex)
                    perm_data_percent_str = ",".join(perm_data_percent)
                except:
                    print("Problem with joining")
                else:
                    print("joining success")

                company_logo = ""

                try:
                    company_logo = soup.find('strong', {'class': 'company-logo'}).img['src']
                except:
                    print("No company logo")
                else:
                    print("Logo get success")

                company_info = ""

                try:
                    company_info = soup.find('div', {'class': 'company-info'}).p.get_text()
                except:
                    print("No company info")
                else:
                    print("Info get success")

                try:

                    sql = f"INSERT INTO LushaCompanies ([CompanyName]," \
                          "[CompanyInfo]," \
                          "[CompanyUrl])," \
                          "[CompanySite]," \
                          "[CompanyFounded]," \
                          "[CompanyEmployees]," \
                          "[CompanyLeadNames]," \
                          "[CompanyTwitter]," \
                          "[CompanyLinkedIn]," \
                          "[CompanyFacebok]," \
                          "[CompanyPermutationTypes]," \
                          "[CompanyPermutationExamples]," \
                          "[CompanyPermutationPercentages] VALUES (lam(company_name)}," \
                          " {lam(company_info)}, " \
                          "{lam(url)}, " \
                          "{lam(site)}," \
                          " {lam(founded)}," \
                          " {lam(employees)}," \
                          " {lam(lead_names)}," \
                          " {lam(twitter_link)}, " \
                          "{lam(linkedin_link)}," \
                          " {lam(facebook_link)}," \
                          " {lam(perm_data_type_str)}," \
                          " {lam(perm_data_ex_str)}, " \
                          "{lam(perm_data_percent_str)});"

                    cursor.execute(sql)

                except:
                    print("Insert failed.")
                else:
                    print("Insert successful.")


            except:
                print("The whole thing failed. Retrying...")
                continue
            else:
                break
            finally:
                print("Everything success")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    run_scrape()
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
