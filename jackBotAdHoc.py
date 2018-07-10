import pandas as pd
import json
import requests
import os

path = os.getcwd()+"\\All_data.xlsx"
URL_NIFTY_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
URL_NIFTY_NEXT_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/juniorNiftyStockWatch.json"
URL_MIDCAP_50_NIFTY_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyMidcap50StockWatch.json"

entities = {'niftyStock':URL_NIFTY_STOCK,'NextNiftyStocks':URL_NIFTY_NEXT_STOCK,'midcapNiftyStock':URL_MIDCAP_50_NIFTY_STOCK}

COLUMN_NAMES = ['symbol','open','high','low','ltP','ptsC','trdVol','open_High','openHigh Status','open_Low','openLow Status']

def getDataForStocks():
    for entity in entities:
        data = requests.get(entities.get(entity))
        if data.status_code is 200:
            obj = open(entity + ".json", 'wb')
            obj.write(data.content)
            obj.close()
        else:
            print("failed to get data for " + entity)

def updateData():
    getDataForStocks()