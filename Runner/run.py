import time
import gspread
from datetime import datetime
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

    def Execute(self):

        TIME = datetime.now().strftime('%d-%m-%Y %H:%M').split(" ")
        Date = TIME[0]
        try:
            while True:
                flag = False
                currTIME = datetime.now().strftime('%d-%m-%Y %H:%M').split(" ")
                currDate = currTIME[0]

                self.connect()
                c = CreateSheet(spreadSheet=self.spreadSheet)
                listWorksheets = self.spreadSheet.worksheets()
                sh = listWorksheets[len(listWorksheets) - 1]  # to get the recent sheet i.e, for current day

                if currDate != Date:
                    shNew = self.spreadSheet.add_worksheet(title=datetime.now().strftime('%d_%m_%Y_%H_%M'), rows="10",
                                                           cols="5")

                    c.everyHour(shNew, sheetPrevDay=sh)
                    if len(self.spreadSheet.worksheets()) > 3:
                        self.spreadSheet.del_worksheet(self.spreadSheet.worksheets()[0])
                    Date = currDate

                else:
                    c.everyHour(sheet=sh)

                print(f"Sleeping for 1 hour\nCurrent Time {datetime.now().strftime('%d-%m-%Y %H:%M')}")
                time.sleep(120)
        except BaseException as e:
            print(e.__traceback__)
            print("Timeout, Please re-run the script after 60s !!")


if __name__ == '__main__':
    r = Run()
