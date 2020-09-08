import requests
import pandas as pd
from lxml.html.soupparser import fromstring
import pyodbc

url_baser = lambda pg: f"" \
                       f"https://www.thomasnet.com/nsearch.html?cov=NA&heading=17873050&searchsource=" \
                       f"suppliers&searchterm=electronic+man&what=Electronic+Contract+Manufacturing&pg={pg}"

domain_adder = lambda lnk: f"https://www.thomasnet.com/{lnk}"

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
    cursor.execute("""CREATE TABLE ThomasNetScrape(
                       CompanyPageTitle nvarchar(MAX),
                       CompanyLogoUrl nvarchar(MAX),
                       CompanySiteUrl nvarchar(MAX),
                       CompanyName nvarchar(MAX),
                       CompanyCovidRes nvarchar(MAX),
                       CompanyAddress nvarchar(MAX),
                       CompanyDescByTomNet nvarchar(MAX),
                       CompanyDescBySelf nvarchar(MAX),
                       CompanyAnnualSales nvarchar(MAX),
                       CompanyIndustry nvarchar(MAX),
                       CompanyEmployeeNum nvarchar(MAX),
                       CompanyAddActivity nvarchar(MAX),
                       CompanyYearFounded nvarchar(MAX),
                       CompanyKeyPersonnel nvarchar(MAX),
                       CompanyLinkedIn nvarchar(MAX),
                       CompanyTwitter nvarchar(MAX),
                       CompanyYoutube nvarchar(MAX),
                       CompanyFacebook nvarchar(MAX))""")
    cnxn.commit()
except:
    print("Table already exists.")
else:
    print("Table created.")

for i in range(1, 46):

    try:
        dir_index = requests.get(url_baser(i))
    except:
        continue

    root_dir = fromstring(dir_index.content)

    hrefs = root_dir.xpath("//a[text() = 'View Supplier']/@href")

    print(f"Got {len(hrefs)} links")

    for lnk in hrefs:

        try:
            req_lnk = requests.get(domain_adder(lnk))
        except:
            continue

        root_page = fromstring(req_lnk.content)

        try:
            title = root_page.xpath("//title/text()")[0]
        except:
            title = ""

        try:
            logo = root_page.xpath("//img[@class = 'framed']/@src")[0]
        except:
            logo = ""

        try:
            site = root_page.xpath("//h1/a[1]/@href")
        except:
            site = ""

        try:
            name = root_page.xpath("//h1/a[1]/text()")
        except:
            name = ""

        covid_res = bool(root_page.xpath("//span[text() = 'COVID-19 Response']"))

        try:
            addr = root_page.xpath("//p[@class = 'addrline']/text()")
        except:
            addr = ""

        try:
            desc_by_thomasnext = root_page.xpath("//div[@id = 'copro_about']/p[1]/text()")
        except:
            desc_by_thomasnext = ""

        try:
            desc_by_company = root_page.xpath("//div[@id = 'copro_about']/p[2]/text()")
        except:
            desc_by_company = ""

        try:
            annual_sales = root_page.xpath("//div[@class = 'bizdetail'][1]/ul/li/text()")
        except:
            annual_sales = ""

        try:
            industry = root_page.xpath("//div[@class = 'bizdetail'][2]/ul/li/text()")[0]
        except:
            industry = ""

        try:
            employee_num = root_page.xpath("//div[@class = 'bizdetail'][2]/ul/li/text()")[1]
        except:
            employee_num = ""

        try:
            add_act = root_page.xpath("//div[@class = 'bizdetail'][3]/ul/li/text()")[0]
        except:
            add_act = ""

        try:
            year_founded = root_page.xpath("//div[@class = 'bizdetail'][3]/ul/li/text()")[1]
        except:
            year_founded = ""

        try:
            key_personnel = root_page.xpath("//div[@class = 'bizdetail'][4]/ul/li/text()")
        except:
            key_personnel = ""

        try:
            linkedin = root_page.xpath("//a[@data-hierarchy_3='LINKEDIN']/@href")[0]
        except:
            linkedin = ""

        try:
            facebook = root_page.xpath("//a[@data-hierarchy_3='FACEBOOK']/@href")[0]
        except:
            facebook = ""

        try:
            youtube = root_page.xpath("//a[@data-hierarchy_3='YOUTUBE']/@href")[0]
        except:
            youtube = ""

        try:
            twitter = root_page.xpath("//a[@data-hierarchy_3='LINKEDIN']/@href")[0]
        except:
            twitter = ""

        try:
            cursor.execute("""INSERT INTO ThomasNetScrape(
                        CompanyPageTitle,
                       CompanyLogoUrl,
                       CompanySiteUrl,
                       CompanyName,
                       CompanyCovidRes,
                       CompanyAddress,
                       CompanyDescByTomNet,
                       CompanyDescBySelf,
                       CompanyAnnualSales,
                       CompanyIndustry,
                       CompanyEmployeeNum,
                       CompanyAddActivity,
                       CompanyYearFounded,
                        CompanyKeyPersonnel,
                       CompanyLinkedIn,
                       CompanyTwitter,
                       CompanyYoutube,
                       CompanyFacebook) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (title,
                                                                                                            logo,
                                                                                                            ",".join(
                                                                                                                site),
                                                                                                            ",".join(
                                                                                                                name),
                                                                                                            covid_res,
                                                                                                            ",".join(
                                                                                                                addr),
                                                                                                            ",".join(
                                                                                                                desc_by_thomasnext),
                                                                                                            ",".join(
                                                                                                                desc_by_company),
                                                                                                            ",".join(
                                                                                                                annual_sales),
                                                                                                            industry,
                                                                                                            employee_num,
                                                                                                            add_act,
                                                                                                            year_founded,
                                                                                                            ",".join(
                                                                                                                key_personnel),
                                                                                                            linkedin,
                                                                                                            twitter,
                                                                                                            youtube,
                                                                                                            facebook
                                                                                                            ))

            cnxn.commit()
        except:
            print("Insert failed.")
        else:
            print("Insert successful")


