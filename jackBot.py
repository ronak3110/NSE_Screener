import schedule
import requests
import pandas as pd
import json
import os
import time
import fileinput
from flask import Flask, request
from flask_restful import Resource, Api
import webbrowser
import signal
import jackBotAdHoc
from nsepy import get_history
import datetime
from datetime import date
import talib
from shutil import copyfile
import numpy as np

app = Flask(__name__)
api = Api(app)

schedulerTime = "21:05"

all_indices = {'Nifty Next 50':'juniorNifty','Nifty 50':'nifty','Nifty Midcap 50':'niftyMidcap50','Nifty Bank':'bankNifty','Nifty Energy':'cnxEnergy','Nifty FIN Service':'cnxFinance',
               'Nifty FMCG':'cnxFMCG','Nifty IT':'cnxit','Nifty Media':'cnxMedia','Nifty Metal':'cnxMetal','Nifty Pharma':'cnxPharma','Nifty PSU Bank':'cnxPSU','Nifty Realty':'cnxRealty','Nifty PVT Bank':'niftyPvtBank'}

moving_avg = {}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

class GetStockJson(Resource):
    def get(self):
        args = request.args['key']
        print(args)
        with open(all_indices.get(args)+'.json') as f:
            data = json.load(f)
        return data

class GetOldJson(Resource):
    def get(self):
        args = request.args['key']
        print(args)
        print(all_indices.get(args)+'old.json')
        with open(all_indices.get(args)+'old.json') as f:
            data = json.loads(f.read())
        return data

class UpadateData(Resource):
    def get(self):
        return jackBotAdHoc.updateData()

class Terminate(Resource):
    def get(self):
        os.kill(os.getpid(), signal.SIGTERM)

class UpdateSchedulerTimer(Resource):
    def get(self):
        global schedulerTime
        args = request.args['time']
        for line in fileinput.input("jackBot.py", inplace=True):
            if line.__contains__("schedulerTime = " + '"' + str(schedulerTime) + '"'):
                print(line.replace(str(schedulerTime), str(args)), end='')
            else:
                print(line, end='')
        schedulerTime = args

api.add_resource(Terminate, '/terminate')  # Route_4 KILL
api.add_resource(UpadateData, '/refreshData')  # Route_5 UPDATE
api.add_resource(UpdateSchedulerTimer,'/updateTime') # Route_6 Update Timer
api.add_resource(GetOldJson,'/getOldJson') # Route_6 Update Timer
api.add_resource(GetStockJson,'/getStockJson') # Route_1 Get Json for specific entity


path = os.getcwd()+"\\All_data.xlsx"

URL = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/"
URL_END = "StockWatch.json"

COLUMN_NAMES = ['symbol','open','high','low','ltP','ptsC','trdVol','open_High','openHigh Status','open_Low','openLow Status']

def getDataForStocks():
    storeOldData();
    for entity in all_indices:
        print("scheduler invoked for entity " + entity +"...")
        data = requests.get(URL+str(all_indices.get(entity))+URL_END)
        if data.status_code is 200:
            print("retrieved data for " + entity)
            obj = open(all_indices.get(entity) + ".json", 'wb')
            obj.write(data.content)
            obj.close()
        else:
            print("failed to get data for " + entity)

    createCSV()

def storeOldData():
    for entity in all_indices:
        try:
            fh = open(all_indices.get(entity) + ".json",'r')
            copyfile(all_indices.get(entity) + ".json", all_indices.get(entity) + 'old.json')
        except:
            pass

def updateMovingAverage(args):
    print(args)
    infoData = {}
    with open(all_indices.get(args) + '.json') as f:
        data = json.load(f)
        for item in data['data']:
            endDate = datetime.datetime.now()
            startDate = endDate - datetime.timedelta(days=60)
            historyData = get_history(symbol=item['symbol'], start=date(startDate.year, startDate.month, startDate.day),end=date(endDate.year, endDate.month, endDate.day))
            try:
                out = list(talib.EMA(historyData['Close'],timeperiod=20))
                infoData.update({item['symbol']:out[len(out)-1]})
            except:
                pass
    return infoData
    # for entity in all_indices:
    #     print(entity)
    #     endDate = datetime.datetime.now()
    #     startDate = endDate - datetime.timedelta(days=50)
    #     historyData = get_history(symbol=entity,start=date(startDate.year,startDate.month,startDate.day),end=date(endDate.year,endDate.month,endDate.day),index=True)
    #     for index, row in historyData.iterrows():
    #         info.update({row})

        # with open(all_indices.get(entity) + '.json') as f:
        #     data = json.load(f)
        #     for item in data['data']:
        #         endDate = datetime.datetime.now()
        #         startDate = endDate - datetime.timedelta(days=50)
        #         historyData = get_history(symbol=item['symbol'],start=date(startDate.year,startDate.month,startDate.day),end=date(endDate.year,endDate.month,endDate.day))
        #         moving_avg.update({item['symbol']:sum(historyData['Close'].values.tolist())/50})

    # print(moving_avg)
    # endDate = datetime.datetime.now()
    # startDate = endDate - datetime.timedelta(days=50)
    # print(date(endDate.year,endDate.month,endDate.day))
    # print(startDate)
    # # historyData = get_history(symbol='PGHH',start=date(startDate.year,startDate.month,startDate.day),end=date(endDate.year,endDate.month,endDate.day))
    # sbin = get_history(symbol='SBIN',start=date(2015,1,1),end=date(2015,1,10))
    # print(sbin['Close'].values.tolist())



def createCSV():

    #Skipping the CSV Write Part -- Not needed

    # writer = pd.ExcelWriter(path, engine='openpyxl')
    # for entity in entities:
    #     with open(entity + '.json') as f:
    #         data = json.load(f)
    #         csvData = []
    #         for stock in data["data"]:
    #             csvData.append(list(map(lambda x: stock[x], COLUMN_NAMES[0:7])))
    #         for row in csvData:
    #             openHigh = float(row[1].replace(',', ''))-float(row[2].replace(',', ''))
    #             openLow = float(row[1].replace(',', ''))-float(row[3].replace(',', ''))
    #             row.append(openHigh)
    #             if openHigh == 0:
    #                 row.append("SELL")
    #             else:
    #                 row.append("")
    #             row.append(openLow)
    #             if openLow == 0:
    #                 row.append("BUY")
    #             else:
    #                 row.append("")
    #         df = pd.DataFrame(csvData,columns=COLUMN_NAMES)
    #         # print(df)
    #         print("creating csv for " + entity)
    #         df.to_excel(writer, sheet_name=entity)
    # writer.save()
    # writer.close()
    print("Starting server.....")
    webbrowser.open('file:///'+os.getcwd()+'/landingPage.html')
    app.run(port='5002')

# schedule.every().hour.do(getDataForStocks)
# schedule.every().day.at(schedulerTime).do(getDataForStocks)
# schedule.every(5).minutes.do(jackBotAdHoc.updateData())
# while 1:
#     schedule.run_pending()
#     time.sleep(1)
getDataForStocks()
