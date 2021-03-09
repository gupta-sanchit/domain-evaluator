import re
import json
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pprint import pprint


class DomainFetcher:
    def __init__(self):
        self.res = {}
        self.URL = 'https://www.webhosting.dk/cgi-bin/domainscannerview.pl'
        self.payload = 'language=DKK&sortby=1&showdayslimit=28'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.webhosting.dk/cgi-bin/domainscannerview.pl?language=DKK',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.webhosting.dk',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers'
        }
        self.response = requests.request("POST", self.URL, headers=self.headers, data=self.payload)
        self.soup = BeautifulSoup(self.response.text, "lxml")

    def getDomains(self):
        data = []
        table = self.soup.find('table', class_='roundedcornerswh')
        # table_body = table.find('tbody')
        # pprint(table_body)

        rows = table.findAll('tr')
        for row in rows:
            pprint(rows)

            # cols = row.find_all('td')
            # cols = [ele.text.strip() for ele in cols]
            # data.append([ele for ele in cols if ele])  # Get rid of empty values

    def PandasV(self):
        print("Start !!")
        df_list = pd.read_html(self.response.text, attrs={
            "class": "roundedcornerswh"})

        df = df_list[0]

        idx = 0

        for i in range(1, len(df)):  # >>==>>Loop starts from 1 to  exclude table header
            domain = df[1][i]
            if not pd.isnull(domain):
                idx += 1
                self.res[idx] = str(domain)
        print("Count:", idx)
        pprint(self.res)


d = DomainFetcher()
# d.getDomains()
d.PandasV()
