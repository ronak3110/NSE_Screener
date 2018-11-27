import requests
import os
from shutil import copyfile

path = os.getcwd()+"\\All_data.xlsx"

all_indices = {'Nifty Next 50':'juniorNifty','Nifty 50':'nifty','Nifty Midcap 50':'niftyMidcap50','Nifty Bank':'bankNifty','Nifty Energy':'cnxEnergy','Nifty Financial Services':'cnxFinance',
               'Nifty FMCG':'cnxFMCG','Nifty IT':'cnxit','Nifty Media':'cnxMedia','Nifty Metal':'cnxMetal','Nifty Pharma':'cnxPharma','Nifty PSU Bank':'cnxPSU','Nifty Realty':'cnxRealty','Nifty Private Bank':'niftyPvtBank'}
URL = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/"
URL_END = "StockWatch.json"

def getDataForStocks():
    storeOldData()
    for entity in all_indices:
        print("scheduler invoked for entity " + entity +"...")
        data = requests.get(URL+str(all_indices.get(entity))+URL_END)
        if data.status_code is 200:
            print("retrieved data for " + entity)
            obj = open(all_indices.get(entity) + ".json", 'wb')
            obj.write(data.content)
            obj.close()
        else:
            return False
    return True

def storeOldData():
    for entity in all_indices:
        try:
            fh = open(all_indices.get(entity) + ".json",'r')
            copyfile(all_indices.get(entity) + ".json", all_indices.get(entity) + 'old.json')
        except:
            pass

def updateData():
    return getDataForStocks()