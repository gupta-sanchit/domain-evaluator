import gspread
import pandas as pd
from tqdm import tqdm
from pprint import pprint
from domainParams.script import DomainParams
from domainFetcher.script import DomainFetcher

from oauth2client.service_account import ServiceAccountCredentials


class CreateSheet:

    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open("domain-info").sheet1

        self.sheetsDF = pd.DataFrame(self.sheet.get_all_records())

        self.df = pd.DataFrame(
            columns=['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic-Keywords', 'Organic-Traffic'])

        self.domainJSON = {}
        self.res = {}

        self.CreateSheet()

    def CreateDataFrame(self):
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        count = 0
        for key in tqdm(self.domainJSON):
            if count == 100:
                break
            domain = self.domainJSON[key]

            paramsJSON = DomainParams(domain='ahrefs.com').getParams()
            pprint(paramsJSON)
            self.res[domain] = paramsJSON
            count += 1

        self.df = pd.DataFrame(self.res).T.reset_index().rename(columns={'index': 'Domain-Rating'})

    def CreateSheet(self):
        # TODO ==> check for empty df
        self.CreateDataFrame()
        self.sheet.update([self.df.columns.values.tolist()] + self.df.values.tolist())


if __name__ == '__main__':
    c = CreateSheet()
