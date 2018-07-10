import schedule
import requests
import pandas as pd
import json
import os
import time
from flask import Flask, request
from flask_restful import Resource, Api
import webbrowser
import signal

app = Flask(__name__)
api = Api(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

class NiftyStocks(Resource):
    def get(self):
        with open('niftyStock.json') as f:
            data = json.load(f)
        return data

class NextNiftyStocks(Resource):
    def get(self):
        with open('NextNiftyStocks.json') as f:
            data = json.load(f)
        return data

class UpadateData(Resource):
    def get(self):
        import jackBotAdHoc
        jackBotAdHoc.updateData()

class MidCapNiftyStocks(Resource):
    def get(self):
        with open('midcapNiftyStock.json') as f:
            data = json.load(f)
        return data

class Terminate(Resource):
    def get(self):
        os.kill(os.getpid(), signal.SIGTERM)

api.add_resource(NiftyStocks, '/niftyStocks')  # Route_1
api.add_resource(NextNiftyStocks, '/NextNiftyStocks')  # Route_2
api.add_resource(MidCapNiftyStocks, '/midcapNiftyStocks')  # Route_3
api.add_resource(Terminate, '/terminate')  # Route_4 KILL
api.add_resource(UpadateData, '/refreshData')  # Route_5 UPDATE


path = os.getcwd()+"\\All_data.xlsx"

URL_NIFTY_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
URL_NIFTY_NEXT_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/juniorNiftyStockWatch.json"
URL_MIDCAP_50_NIFTY_STOCK = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyMidcap50StockWatch.json"

entities = {'niftyStock':URL_NIFTY_STOCK,'NextNiftyStocks':URL_NIFTY_NEXT_STOCK,'midcapNiftyStock':URL_MIDCAP_50_NIFTY_STOCK}

COLUMN_NAMES = ['symbol','open','high','low','ltP','ptsC','trdVol','open_High','openHigh Status','open_Low','openLow Status']

def getDataForStocks():
    for entity in entities:
        print("scheduler invoked for entity " + entity +"...")
        data = requests.get(entities.get(entity))
        if data.status_code is 200:
            print("retrieved data for " + entity)
            obj = open(entity + ".json", 'wb')
            obj.write(data.content)
            obj.close()
        else:
            print("failed to get data for " + entity)

    createCSV()

def createCSV():
    writer = pd.ExcelWriter(path, engine='openpyxl')
    for entity in entities:
        with open(entity + '.json') as f:
            data = json.load(f)
            csvData = []
            for stock in data["data"]:
                csvData.append(list(map(lambda x: stock[x], COLUMN_NAMES[0:7])))
            for row in csvData:
                openHigh = float(row[1].replace(',', ''))-float(row[2].replace(',', ''))
                openLow = float(row[1].replace(',', ''))-float(row[3].replace(',', ''))
                row.append(openHigh)
                if openHigh == 0:
                    row.append("SELL")
                else:
                    row.append("")
                row.append(openLow)
                if openLow == 0:
                    row.append("BUY")
                else:
                    row.append("")
            df = pd.DataFrame(csvData,columns=COLUMN_NAMES)
            # print(df)
            print("creating csv for " + entity)
            df.to_excel(writer, sheet_name=entity)
    writer.save()
    writer.close()
    print("Starting server.....")
    webbrowser.open('file:///'+os.getcwd()+'/landingPage.html')
    app.run(port='5002')

# schedule.every(1).minutes.do(getDataForStocks)
# schedule.every().hour.do(getDataForStocks)
schedule.every().day.at("09:31").do(getDataForStocks)

while 1:
    schedule.run_pending()
    time.sleep(1)
# getDataForStocks()