import json
import requests
import pandas as pd
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
        print("Response Received !!")

    def getDomains(self):

        df_list = pd.read_html(self.response.text, attrs={
            "class": "roundedcornerswh"})

        df = df_list[0]

        idx = 0

        for i in range(1, len(df)):  # >>==>>Loop starts from 1 to  exclude table header
            domain = df[1][i]
            if not pd.isnull(domain):
                idx += 1
                self.res[idx] = str(domain)
        self.res['count'] = idx
        return self.res


d = DomainFetcher()
res = d.getDomains()

with open('domains.json', 'w') as fp:
    json.dump(res, fp, indent=4)

