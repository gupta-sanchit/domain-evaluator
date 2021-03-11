import json
import gspread
import pandas as pd
import concurrent.futures
from datetime import datetime
from gspread_formatting import *
from gspread_dataframe import set_with_dataframe
from DomainParams.script import DomainParams
from DomainFetcher.script import DomainFetcher
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting.dataframe import format_with_dataframe, BasicFormatter
from gspread_formatting import Color
from gspread_formatting import *

import gspread_dataframe as gd


class CreateSheet:

    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadSheet = self.client.open("domain-info")
        self.sheetTitle = datetime.now().strftime('%d_%m_%Y_%H_%M')
        self.SheetHeader = ['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic Keywords', 'Organic-Traffic']

        # listWorksheets = self.spreadSheet.worksheets()
        #
        # self.sheet = self.spreadSheet.add_worksheet(title='temp', rows="10", cols="10")
        # self.sheet.insert_row(self.SheetHeader, 1)
        #
        # if len(listWorksheets) >= 3:
        #     self.spreadSheet.del_worksheet(listWorksheets[0])

        self.domainJSON = {}
        self.res = {}
        self.resStore = {}

        # self.CreateSheetThreading()
        self.CreateDataFrame()

        print("Updated Successfully !!")

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
        print(len(self.domainJSON.keys()))
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
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

                self.resStore[paramsJSON['domain']] = row
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
        # sheetsDF = pd.DataFrame(self.sheet.get_all_records())

        df = pd.DataFrame(
            columns=['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic-Keywords', 'Organic-Traffic'])
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            idx = 0
            for key in self.domainJSON:
                if idx == 10: break
                idx += 1
                domain = self.domainJSON[key]
                threads.append(executor.submit(DomainParams().getParams, domain=domain))

            for thread in concurrent.futures.as_completed(threads):
                paramsJSON = thread.result()
                self.res[paramsJSON['domain']] = paramsJSON

            # for key in self.domainJSON:
            #     domain = self.domainJSON[key]
            #     paramsJSON = DomainParams().getParams(domain='ahrefs.com')
            #
            #     self.res[domain] = paramsJSON
        pprint(self.res)
        # df = pd.DataFrame(self.res).T.reset_index().rename(columns={'index': 'Domain-Rating'})
        df = pd.DataFrame(self.res).T.reset_index(drop=True)
        print(df)

        # sh = self.spreadSheet.add_worksheet(title='temp3', rows="10", cols="10")
        # set_with_dataframe(sh, df)
        # 
        # rule = ConditionalFormatRule(
        #     ranges=[GridRange.from_a1_range('1:3', sh)],
        #     booleanRule=BooleanRule(
        #         condition=BooleanCondition('NUMBER_GREATER', ['0']),
        #         format=CellFormat(backgroundColor=Color(1, 0, 0))
        #     )
        # )
        # rules = get_conditional_format_rules(sh)
        # rules.append(rule)
        # rules.save()
        # format_with_dataframe(sh, df, include_index=True, include_column_header=True)
        #
        # formatter = BasicFormatter(
        #     header_background_color=Color(0, 0, 0),
        #     header_text_color=Color(1, 1, 1),
        #     decimal_format='#,##0.00'
        # )
        #
        #         fmt = CellFormat(backgroundColor=Color(1,0,0))
        # )
        #         format_with_dataframe(sh, df, fmt, include_index=False, include_column_header=True)
        # sh.update([df.columns.values.tolist()] + df.values.tolist())

        fmt = cellFormat(
            backgroundColor=color(1.6, 1, 0),  # set it to yellow
            textFormat=textFormat(foregroundColor=color(1, 0, 0)),
        )
        # red: (1,0,0), white: (1,1,1)
        row = 3
        # format_cell_range(sh, 'A2:E', fmt)
        # sh.update([df.columns.values.tolist()] + df.values.tolist())

        old = self.spreadSheet.worksheets()[2]

        # existing = gd.get_as_dataframe(old)
        existing = pd.DataFrame(old.get_all_records())

        title = old.title
        self.spreadSheet.del_worksheet(old)
        newDF = df.append(existing)
        print(newDF)
        print(len(newDF))

        newSheet = self.spreadSheet.add_worksheet(title=title, rows="10", cols="5")
        newSheet.update([newDF.columns.values.tolist()] + newDF.values.tolist())
        format_cell_range(newSheet, '2:11', fmt)

        # ==> To preserve formatting in old sheet !!
        # updated = existing.append(df)
        # gd.set_with_dataframe(old, updated)
        #
        # format_cell_range(old, '2913:2922', fmt)
        # updated = existing.append(df)
        # gd.set_with_dataframe(old, updated)


if __name__ == '__main__':
    c = CreateSheet()
