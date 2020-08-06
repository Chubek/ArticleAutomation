import logging
import pyodbc
from bs4 import BeautifulSoup
import requests
import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient
import azure.durable_functions as df
import os
import typing
import json
import time

def run_scrape():
    logging.info("Function started")

    driver = "{ODBC Driver 17 for SQL Server}"
    server = "tcp:chubak-sql.database.windows.net,1433"
    database = "marketing_scrape"
    username = "chubak"
    password = "LAsvegas11"

    connection_string = 'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}' \
        .format(driver=driver, server=server, database=database, username=username, password=password)

    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()

    logging.info("Connection made")

    try:
        cursor.execute("""CREATE TABLE LushaCompaniesScrapingsRaan(
                   CompanyName text,
                   CompanyInfo text,
                   CompanyUrl text,
                   CompanyLogoUrl text,
                   CompanySite text,
                   CompanyFounded text,
                   CompanyEmployees text,
                   CompanyLeadNames text,
                   CompanyTwitter text,
                   CompanyLinkedIn text,
                   CompanyFacebook text,
                   CompanyPermutationTypes text,
                   CompanyPermutationExamples text,
                   CompanyPermutationPercentages text)""")

        cnxn.commit()
    except:
        logging.info("Table already exists.")
    else:
        logging.info("Table created.")

    current_path = "/home/site/wwwroot"
    url_file = open(os.path.join(current_path, 'url_file.txt'), 'r')

    logging.info(f"File {url_file.name} loaded.")

    urls = [url.strip() for url in url_file.readlines()]

    lam = lambda x: "'" + x + "'"

    for i, url in enumerate(urls):

        logging.info(f"Checking url {url} {i} of {len(urls)}")

        try:
            req = requests.get(url)
        except:
            logging.info("Url GET failed.")
            continue
        else:
            logging.info(f"Url {url} get success")

        soup = None

        try:
            soup = BeautifulSoup(req.content, 'html.parser')
        except:
            logging.warning("Problem parsing.")
        else:
            logging.info("Parsing complete.")

        company_name = ""

        try:
            company_name = soup.h1.get_text()
        except:
            logging.info("Company name scrape failed. No company name.")
        else:
            logging.info("Name get success")

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
            logging.info("No leads.")
        else:
            logging.info("Leads get success")

            site = ""

        try:
            site = soup.find('div', {'class': 'link'}).h2.a['href']
        except:
            logging.info("No site")
        else:
            logging.info("Site get success")

        founded = ""
        employees = ""

        try:
            details = soup.find('dl', {'class': 'company-details'}).find_all('dd')

            founded = details[0].get_text()
            employees = details[1].get_text()

        except:
            logging.info("No founded or employees")

        else:
            logging.info("employee/founded get success")

        facebook_link = ""
        linkedin_link = ""
        twitter_link = ""

        try:
            facebook_link = soup.find('a', {'class': 'facebook'})['href']
        except:
            logging.info("No Facebook")
        else:
            logging.info("Facebook get success")

        try:
            linkedin_link = soup.find('a', {'class': 'linkedin'})['href']
        except:
            logging.info("No LinkedIn")
        else:
            logging.info("Linkedin get success")

        try:
            twitter_link = soup.find('a', {'class': 'twitter'})['href']
        except:
            logging.info("No Twitter")
        else:
            logging.info("Twitter get success")

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
            logging.info("No perm data")
        else:
            logging.info("Perm get success")

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
            logging.info("Problem with joining")
        else:
            logging.info("joining success")

        company_logo = ""

        try:
            company_logo = soup.find('strong', {'class': 'company-logo'}).img['src']
        except:
            logging.info("No company logo")
        else:
            logging.info("Logo get success")

        company_info = ""

        try:
            company_info = soup.find('div', {'class': 'company-info'}).p.get_text()
        except:
            logging.info("No company info")
        else:
            logging.info("Info get success")

        try:
            cursor.execute("""INSERT INTO LushaCompaniesScrapingsRaan(
                    CompanyName,
                     CompanyInfo,
                     CompanyUrl,
                     CompanyLogoUrl,
                     CompanySite,
                     CompanyFounded, 
                     CompanyEmployees, 
                     CompanyLeadNames,
                     CompanyTwitter, 
                     CompanyLinkedIn, 
                     CompanyFacebook, 
                     CompanyPermutationTypes, 
                     CompanyPermutationExamples, 
                     CompanyPermutationPercentages) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?) """, (company_name,
                                     company_info,
                                     url,
                                     company_logo,
                                     site,
                                     founded,
                                     employees,
                                     lead_names,
                                     twitter_link,
                                     linkedin_link,
                                     facebook_link,
                                     perm_data_type_str,
                                     perm_data_ex_str,
                                     perm_data_percent_str))

            cnxn.commit()
        except:
            logging.info("Insert failed.")
        else:
            logging.info("Insert successful")

    return "Done"


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = "RunScrapeHTTP"
    await run_scrape()
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
