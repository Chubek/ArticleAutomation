import pyodbc

driver = "{ODBC Driver 17 for SQL Server}"
server = "tcp:marketing-server-chubak.database.windows.net"
database = "marketing_scraped_data"
username = "chubak"
password = "LAsvegas11"

connection_string = 'DRIVER={driver};PORT=1433;SERVER={server};DATABASE={database};UID={username};PWD={password}' \
    .format(driver=driver, server=server, database=database, username=username, password=password)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

cursor.execute("SELECT * FROM LushaCompanies")

rows = cursor.fetch_rows()

print(rows)