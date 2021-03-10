import gspread
import json
import pandas as pd
from tqdm import tqdm
from pprint import pprint
from DomainParams.script import DomainParams
from DomainFetcher.script import DomainFetcher

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

        self.CreateSheetRealtime()

    def next_available_row(self):
        """
        returns: index of first empty row in sheet
        """
        str_list = list(filter(None, self.sheet.col_values(1)))
        return len(str_list) + 1

    def CreateSheetRealtime(self):
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        rowIDX = self.next_available_row()  # ==>> get index of first empty row
        for key in tqdm(self.domainJSON):
            domain = self.domainJSON[key]
            paramsJSON = DomainParams(domain=domain).getParams()
            row = [domain, paramsJSON['ref-domains'], paramsJSON['domain-rating'], paramsJSON['organic-keywords'],
                   paramsJSON['organic-traffic']]

            self.sheet.insert_row(row, rowIDX)
            # print(rowIDX)
            # rowIDX += 1

    def CreateDataFrame(self):
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        idx = 0
        for key in tqdm(self.domainJSON):
            if idx == 100:
                with open('data/SheetDF.json', 'w') as fp:
                    json.dump(self.res, fp, indent=4)
                print(f"File Saved at: {idx}")
                break

            domain = self.domainJSON[key]
            paramsJSON = DomainParams(domain='ahrefs.com').getParams()
            # pprint(paramsJSON)
            self.res[domain] = paramsJSON
            idx += 1
        self.df = pd.DataFrame(self.res).T.reset_index().rename(columns={'index': 'Domain-Rating'})

    def CreateSheet(self):
        # TODO ==> check for empty df
        self.CreateDataFrame()
        self.sheet.update([self.df.columns.values.tolist()] + self.df.values.tolist())


if __name__ == '__main__':
    c = CreateSheet()
