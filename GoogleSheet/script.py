import pandas as pd
import concurrent.futures
from turtle import color
from gspread_formatting import *
from DomainParams.script import DomainParams
from DomainFetcher.script import DomainFetcher


class CreateSheet:

    def __init__(self, spreadSheet):
        self.spreadSheet = spreadSheet

        self.domainJSON = {}
        self.res = {}
        self.resStore = {}

    def everyHour(self, sheet, sheetPrevDay=None):
        title = sheet.title
        if sheetPrevDay:
            print("DAY CHANGE")
            existingSheetDF = pd.DataFrame(sheetPrevDay.get_all_records())
            bgColor = color(1, 1, 1)
        else:
            existingSheetDF = pd.DataFrame(sheet.get_all_records())
            bgColor = color(1.6, 1, 0)  # green

        #   Filtering New Domains
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json
        newDomainsJSON = {}
        idx = 1
        for key in self.domainJSON.keys():
            domain = self.domainJSON[key]
            if domain not in existingSheetDF['Domain-Name'].values:
                newDomainsJSON[idx] = domain
                idx += 1
        print(f'OLD DOMAINS: {len(self.domainJSON.keys())}')
        print(f'NEW DOMAINS: {len(newDomainsJSON.keys())}')

        if len(newDomainsJSON.keys()) == 0:
            print("No new domains found !!")
            if sheetPrevDay:
                sheet.update([existingSheetDF.columns.values.tolist()] + existingSheetDF.values.tolist())
                return
            else:
                return

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for key in newDomainsJSON:
                domain = newDomainsJSON[key]
                threads.append(executor.submit(DomainParams().getParams, domain=domain))

            for thread in concurrent.futures.as_completed(threads):
                paramsJSON = thread.result()
                self.res[paramsJSON['domain']] = paramsJSON

        df = pd.DataFrame(self.res).T.reset_index(drop=True)

        df.columns = existingSheetDF.columns
        newDF = df.append(existingSheetDF)

        self.spreadSheet.del_worksheet(sheet)
        print(title)
        newSheet = self.spreadSheet.add_worksheet(title=title, rows="10", cols="5")

        newSheet.update([newDF.columns.values.tolist()] + newDF.values.tolist())

        fmt = cellFormat(
            backgroundColor=bgColor
        )

        cellRANGE = f'2:{2 + len(df) - 1}'
        print(f"cell range:{cellRANGE}")
        format_cell_range(newSheet, cellRANGE, fmt)
