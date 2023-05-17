#youtube video https://www.youtube.com/watch?v=csj1RoLTMIA

import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.ebay.ca/sch/i.html?_from=R40&_nkw=rx+6700+xt&_sacat=0&LH_PrefLoc=3&LH_Sold=1&LH_Complete=1&rt=nc&LH_BIN=1'

def get_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def parse(soup):
    results = soup.find_all('div', {'class': "s-item__info clearfix"}) #"s-item__detail"
    for item in results:
        products = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'soldprice': float(item.find('span', {'class': 's-item__price'}).text.replace('C', '').replace('$', '').strip()),
            'solddate': item.find('span', {'class': 's-item__title--tagblock'}).find('span', {"class": 'POSITIVE'}).text,
            'bids': item.find('span', {'class': "s-item__bids"}).text,
            'link': item.find('a', {"class": 's-item-link'})['href'],
        }
        print(products)


    #print(len(results))
    return

soup = get_data(url)
parse(soup)

#   "<div class="s-item__detail s-item__detail--primary"><span class="s-item__price"><span class="POSITIVE ITALIC">C $419.83</span></span></div>"
