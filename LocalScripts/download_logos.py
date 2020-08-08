import pandas as pd
import requests
import numpy as np

csv = pd.read_csv("/home/chubak/Documents/lusha_initial_100.csv")


logo_url_name = csv[["CompanyName", "CompanyLogoUrl"]]


for name, url in logo_url_name.values:
    if not str(type(url)) == "<class 'float'>":
        image = requests.get(url)
        file = open(f"logos/{name}.png", "wb")
        file.write(image.content)

