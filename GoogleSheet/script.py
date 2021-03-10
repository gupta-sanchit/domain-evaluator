import gspread
import pandas as pd
from datetime import datetime
import concurrent.futures
from DomainParams.script import DomainParams
from DomainFetcher.script import DomainFetcher

from oauth2client.service_account import ServiceAccountCredentials


class CreateSheet:

    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadSheet = self.client.open("domain-info")
        self.sheetTitle = datetime.now().strftime('%d_%m_%Y_%H_%M')
        self.SheetHeader = ['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic Keywords', 'Organic-Traffic']

        listWorksheets = self.spreadSheet.worksheets()

        self.sheet = self.spreadSheet.add_worksheet(title=self.sheetTitle, rows="10", cols="10")
        self.sheet.insert_row(self.SheetHeader, 1)

        if len(listWorksheets) >= 3:
            self.spreadSheet.del_worksheet(listWorksheets[0])
            self.spreadSheet.del_worksheet(listWorksheets[1])
            self.spreadSheet.del_worksheet(listWorksheets[2])

        self.domainJSON = {}
        self.res = {}

        self.CreateSheetThreading()

    def next_available_row(self):
        """
        returns: index of first empty row in sheet
        """
        str_list = list(filter(None, self.sheet.col_values(1)))
        return len(str_list) + 1

    def CreateSheetThreading(self):
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json
        rowBatchSize = 0
        rowBatch = []
        added = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for key in self.domainJSON:
                domain = self.domainJSON[key]
                futures.append(executor.submit(DomainParams().getParams, domain=domain))

            for future in concurrent.futures.as_completed(futures):
                if rowBatchSize == 500:
                    self.sheet.append_rows(rowBatch)
                    rowBatch = []
                    rowBatchSize = 0
                    added += 500
                    print(f'Rows Added => {added}\n')
                paramsJSON = future.result()
                row = [paramsJSON['domain'], paramsJSON['ref-domains'], paramsJSON['domain-rating'],
                       paramsJSON['organic-keywords'],
                       paramsJSON['organic-traffic']]
                rowBatch.append(row)
                rowBatchSize += 1
            if len(rowBatch) != 0:
                self.sheet.append_rows(rowBatch)

    def CreateSheetRealtime(self):
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        rowIDX = self.next_available_row()  # ==>> get index of first empty row
        for key in self.domainJSON:
            domain = self.domainJSON[key]
            paramsJSON = DomainParams().getParams(domain=domain)
            row = [domain, paramsJSON['ref-domains'], paramsJSON['domain-rating'], paramsJSON['organic-keywords'],
                   paramsJSON['organic-traffic']]

            self.sheet.insert_row(row, rowIDX)

    def CreateDataFrame(self):
        sheetsDF = pd.DataFrame(self.sheet.get_all_records())

        df = pd.DataFrame(
            columns=['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic-Keywords', 'Organic-Traffic'])
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        for key in self.domainJSON:
            domain = self.domainJSON[key]
            paramsJSON = DomainParams().getParams(domain='ahrefs.com')
            # pprint(paramsJSON)
            self.res[domain] = paramsJSON

        df = pd.DataFrame(self.res).T.reset_index().rename(columns={'index': 'Domain-Rating'})


if __name__ == '__main__':
    c = CreateSheet()
