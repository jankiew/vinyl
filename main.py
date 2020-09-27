import requests
import bs4 as bs
from urllib import parse
import json
import pandas as pd
import pygsheets

def scrape_urls():
    gdoc_link = 'GOOGLE_DOC_LINK'
    sheet_name = 'asfalt shop'

    urls=list()
    product_list = list()

    for i in range(1,2,1):
        url = 'https://asfaltshop.pl/nowosci/?sortType=3&page=' + str(i)
        listPage = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
        soup = bs.BeautifulSoup(listPage.text, 'html.parser')
        product_div = soup.find_all("div", {"class": "kafelki"})
        products = product_div[0].find_all("div", {"class": "kafelek"})

        [product_list.append([
            product.find("div", {"class": "title1"}).text,
            product.find("div", {"class": "title2"}).text,
            product.find("div", {"class": "pricing"}).text,
            f"https://asfaltshop.pl{product.find('div').find_parent('a')['href']}",
            [src['data-original'] for src in product.find_all('img')][0]
        ]) for product in products]

    output_df = pd.DataFrame(product_list)
    c = pygsheets.authorize(service_file='service_account_credentials.json')
    #c = pygsheets.authorize()
    sht = c.open_by_url(gdoc_link)
    wks = sht.worksheet(property='title', value=sheet_name)
    db_list = wks.get_all_values(include_tailing_empty_rows = False)

    db_df = pd.DataFrame(db_list)
    db_df.columns = db_df.iloc[0]
    db_df = db_df.drop(db_df.index[0])
    new_records = list()

    for index, row in output_df.iterrows():
        if row[3] in db_df['Link'].values.tolist():
            continue
        else:
            new_records.append([row[0],row[1],row[2],row[3],row[4]])
    wks.append_table(new_records, start=f'A{len(db_list)+1}', end=None, dimension='ROWS', overwrite=False)

    return
    
scrape_urls()


