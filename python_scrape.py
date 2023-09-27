import mechanicalsoup as ms
import pandas as pd
url = "https://en.wikipedia.org/wiki/Comparison_of_Linux_distributions"
browser = ms.StatefulBrowser()
browser.open(url)
browser.page.find_all("th", attrs={"class": "table-rh"})
distribution = [value.text for value in th]
print(distribution)