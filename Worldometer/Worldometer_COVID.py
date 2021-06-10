'''
"Worldometer COVID-19 Active Cases"
Done by: R Karthick Paramesh
Date   : 14-01-2021
'''

# Import Modules
import pandas as pd
import requests
import json
import os
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime

# Output directory
if not os.path.exists('Output'):
     os.mkdir('output')
output_path = "output/Worldometer_active_cases.csv"

# URL map dataframe
# Map directory
map_path = "resources/Worldometer_URL_map.csv"

# Header for the browser
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}

# Map dataframe
map_df = pd.read_csv(map_path)
name = map_df['Country_name']
url_tag = map_df['URL_tag']
map_dict = dict(zip(url_tag,name))

# String to datetime
def string_to_datetime(dt):
     return(datetime.strptime(dt, "%b %d, %Y").date())

# Index finder
def index_find(text, text_to_find, word_type):
     if word_type == 'start':
          return (text.find(text_to_find)+len(text_to_find))
     elif word_type == 'end':
          return (text.find(text_to_find)-1)
     else:
          raise KeyError

# Returns list of countries/locations for which data is available in the Worldometer
def get_countries():
     return (name.to_list())

# Returns list of country's/location's URL tags
def get_country_url_tags():
     return (url_tag.to_list())

# Active Cases download country wise
def get_country_data(tag):
     URL = 'https://www.worldometers.info/coronavirus/country/'+ tag +'/'
     page = requests.get(URL, headers=header)
     tree = html.fromstring(page.content)

     # Search for active cases category
     script = tree.xpath('//script[contains(., "graph-active-cases-total")]')[0]

     # Searching within the script for dates
     # Dates values are in xAxis, 'categories' set
     # Active cases values are in 'data' set
     script_text = "".join([i for i in script.text.strip() if not i.isspace()])
     date_start = index_find(script_text, 'xAxis:', 'start')
     date_end = index_find(script_text, 'yAxis:', 'end')

     # Date values
     date_dict = json.loads(script_text[date_start:date_end].replace('categories','"Dates"'))
     dates = date_dict["Dates"]

     # Searching within the script for values
     value_start = index_find(script_text, 'data:', 'start')
     value_end = index_find(script_text, 'responsive:', 'end')

     # Active cases values
     values = json.loads(script_text[value_start:value_end].replace(']}]',']'))

     # Dataframe for Active cases
     df = pd.DataFrame({map_dict[tag]:values}, index = list(map(string_to_datetime, dates)))
     return(df)

# Active Cases download for all countries
def get_all_data(countries = map_dict):
    # Data Concatenation
    data_list = []
    for i in countries:
         try:
              data_list.append(country_data(i))
         except:
              pass

    # Final Dataframe
    all_dataframe = pd.concat(data_list,axis=1)
    return(all_dataframe)
