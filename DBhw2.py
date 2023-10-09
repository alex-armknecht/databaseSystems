import pandas as pd
import sqlite3

df = pd.read_csv("train_egg_sales.csv")
print(df.head())
print(df.tail())


connection = sqlite3.connect("eggs.db")

cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS 'Egg_Sales'")

df.to_sql("Egg_Sales", connection)

connection.close

print("total egg sales:")
print(df['Egg Sales'].sum())
