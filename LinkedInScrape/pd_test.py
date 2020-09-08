import pandas as pd

df_cookies = pd.read_csv("cookies-www-linkedin-com.txt", sep="\t", header=None)

cookies_list = []

for i in range(df_cookies.shape[0]):
    cookies_list.append({"name": df_cookies.loc[i, 5], "value": df_cookies.loc[i, 6]})

print(cookies_list)