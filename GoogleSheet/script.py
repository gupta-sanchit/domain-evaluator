import json
import pandas as pd
from turtle import color
import concurrent.futures
from gspread_formatting import *
from DomainParams.script import DomainParams
from DomainFetcher.script import DomainFetcher


class CreateSheet:

    def __init__(self, spreadSheet):
        self.spreadSheet = spreadSheet

        self.domainJSON = {}
        self.res = {}
        self.resStore = {}
        self.existingDomains = {}

    def everyHour(self, sheet, sheetPrevDay=None, emptyFlag=False):
        with open('../domains.json', 'r') as fp:
            self.existingDomains = json.load(fp)

        title = sheet.title
        if sheetPrevDay:
            print("DAY CHANGE")
            existingSheetDF = pd.DataFrame(sheetPrevDay.get_all_records())
            bgColor = color(1, 1, 1)  # white
            format_cell_range(sheetPrevDay, f'2: {2 + len(existingSheetDF) - 1}', cellFormat(backgroundColor=bgColor))
        else:
            existingSheetDF = pd.DataFrame(sheet.get_all_records())
            bgColor = color(1.6, 1, 0)  # green

        # TO CREATE DB
        # for i in existingSheetDF[existingSheetDF.columns[0]].values:
        #     existingDomains['domain'].append(i)

        #   Filtering New Domains
        self.domainJSON = DomainFetcher().getDomains()  # scraped domains json
        newDomainsJSON = {}

        idx = 1
        for key in self.domainJSON.keys():
            domain = self.domainJSON[key]
            if domain not in self.existingDomains['domain']:
                newDomainsJSON[idx] = domain
                self.existingDomains['domain'].append(domain)
                idx += 1

        # print(len(existingDomains['domain']))
        with open('../domains.json', 'w') as fp:
            json.dump(self.existingDomains, fp, indent=4)

        print(f'NEW DOMAINS FOUND ==> {len(newDomainsJSON.keys())}')

        if len(newDomainsJSON.keys()) == 0:
            if sheetPrevDay:
                df_empty = pd.DataFrame(columns=['Domain-Name', 'Ref-Domain', 'Domain-Rating', 'Organic-Keywords',
                                                 'Organic-Traffic'])
                sheet.update([df_empty.columns.values.tolist()] + df_empty.values.tolist())
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
        if sheetPrevDay or emptyFlag:
            newDF = df
        else:
            newDF = df.append(existingSheetDF)

        newSheet = self.spreadSheet.add_worksheet(title='temp', rows="10", cols="5")
        self.spreadSheet.del_worksheet(sheet)
        newSheet.update_title(title)

        newSheet.update([newDF.columns.values.tolist()] + newDF.values.tolist())

        fmt = cellFormat(
            backgroundColor=bgColor
        )

        cellRANGE = f'2:{2 + len(df) - 1}'
        format_cell_range(newSheet, cellRANGE, fmt)
        print("Sheet Updated !!")
