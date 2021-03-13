import time
import gspread
import traceback
import pandas as pd
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

from GoogleSheet.script import CreateSheet


class Run:
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', self.scope)
        self.client = None
        self.spreadSheet = None
        self.connect()
        self.Execute()

    def connect(self):
        self.client = gspread.authorize(self.creds)
        self.spreadSheet = self.client.open("domain-info")
        # self.spreadSheet = self.client.open("Copy of domain-info1111")

    def Execute(self):

        TIME = datetime.now().strftime('%d-%m-%Y %H:%M').split(" ")
        Date = TIME[0]
        try:
            while True:
                currTIME = datetime.now().strftime('%d-%m-%Y %H:%M').split(" ")
                currDate = currTIME[0]
                emptyFlag = False
                sheetPrev = None

                self.connect()  # initializing connection with spreadsheet
                c = CreateSheet(spreadSheet=self.spreadSheet)
                listWorksheets = self.spreadSheet.worksheets()
                sh = listWorksheets[len(listWorksheets) - 1]  # to get the recent sheet i.e, for current day

                if len(sh.get_all_records()) == 0:
                    sheetPrev = listWorksheets[len(listWorksheets) - 2]
                    emptyFlag = True
                if currDate != Date:
                    shNew = self.spreadSheet.add_worksheet(title=datetime.now().strftime('%d_%m_%Y'), rows="10",
                                                           cols="5")

                    c.everyHour(shNew, sheetPrevDay=sh)
                    if len(self.spreadSheet.worksheets()) > 3:
                        self.spreadSheet.del_worksheet(self.spreadSheet.worksheets()[0])
                    Date = currDate

                else:
                    if emptyFlag:
                        print("Current Empty")
                        c.everyHour(sheet=sh, sheetPrevDay=sheetPrev, emptyFlag=True)
                    else:
                        c.everyHour(sheet=sh)

                print('Sleeping for 1 hour !!')
                print(f"Next Update Time ==> {(datetime.now() + timedelta(hours=1)).strftime('%d-%m-%Y %H:%M')}\n\n")
                time.sleep(3600)
        except BaseException as e:
            print(f"Error : {e}")
            traceback.print_tb(e.__traceback__)
            print("Timeout, Please re-run the script after 60s !!")


if __name__ == '__main__':
    r = Run()
