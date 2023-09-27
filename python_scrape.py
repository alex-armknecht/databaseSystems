import pandas as pd
import mechanicalsoup as ms
import sqlite3

url = "https://en.wikipedia.org/wiki/List_of_A24_films"
browser = ms.StatefulBrowser()
browser.open(url)

th = browser.page.find_all("th")
A24_titles = [value.text.strip() for value in th]
glimpse_index = A24_titles.index("A Glimpse Inside the Mind of Charles Swan III")
uncut_gems_index = A24_titles.index("Uncut Gems")
A24_titles = A24_titles[glimpse_index:uncut_gems_index+1]
print(A24_titles)

td = browser.page.find_all("td")
columns = [value.text.strip() for value in td]
first_index = columns.index("February 8, 2013")
last_index = columns.index("December 13, 2019") + 5
columns = columns[first_index:last_index]
# print(columns)

column_names = ["Release_date", "Directors", "Synopsis", "Notes", "Refrences"]


dictionary = {"A24_titles": A24_titles}
for idx, key in enumerate(column_names):
    dictionary[key] = columns[idx:][::5]


df = pd.DataFrame(data = dictionary)


print(df.head())
print(df.tail())

connection = sqlite3.connect("a24.db")
cursor = connection.cursor()
cursor.execute("Create table movies (Titles, " + ",".join(column_names) +")")

for i in range(len(df)) :
    cursor.execute("insert into movies values (?,?,?,?,?,?)", df.iloc[i])

connection.commit()
connection.close()