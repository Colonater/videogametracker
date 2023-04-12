import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#request module sends a http request to a website and recieve resposes
#BeautifulSoup module is used for web scraping purposes to parse HTML or XML documents
#pandas is a library for data manipulation and analysis.
#re module is used for pattern matching with regular expressions.

searchterm = input("Enter a Search Word for the Ebay Price Scraper to Scrap the web for the price of the last 50 sold: (no spaces use +) ")

#getdate is a function that takes a screach term
# as input and returns the parsed html using the
# request and beautifulsoup modules

def get_data(searchterm):
    url = f'https://www.ebay.ca/sch/i.html?_from=R40&_nkw={searchterm}&_sacat=0&LH_PrefLoc=3&LH_Sold=1&LH_Complete=1&rt=nc&LH_BIN=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

#parse function takes the parsed html as the input and returns a list of products as outputs
#soup.find.all method finds all html tags that match the given criteria

def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': "s-item__info clearfix"}) #"s-item__detail"
    for item in results:
        try:
            solddate = item.find('span', {'class': 's-item__title--tagblock'}).find('span').text
        except:
            solddate = ''
        try:
            bids = item.find('span', {'class': 's-item__bids'}).text
        except:
            bids = ''
        soldprice_str = item.find('span', {'class': 's-item__price'}).text.replace('C', '').replace('$', '').strip()
        soldprice = float(re.findall(r'\d+\.\d+', soldprice_str)[0])
        products = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'soldprice': soldprice,
            'solddate': solddate,
            'bids': bids,
            'link': item.find('a', {"class": 's-item__link'})['href'],
        }
        productslist.append(products)
        #print(products)


    #print(len(results))
    return productslist

#all saved to a csv file

def output(productslist, searchterm):
    productsdf = pd.DataFrame(productslist)
    productsdf.to_csv(searchterm + "output.csv", index=False)
    print('Saved too CSV')
    return

soup = get_data(searchterm )
productslist = parse(soup)
output(productslist)
