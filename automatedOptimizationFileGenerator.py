from datetime import datetime
from paramsParserToSetOrIni import parseToSetOrIni
from isoweek import Week

def isBisiesto(year):
    return not year % 4 and (year % 100 or not year % 400)

def has53Weeks(year):
    if((isBisiesto(year) and datetime(year,1,1).weekday() == 2) or (datetime(year,1,1).weekday() == 3)):
        return True
    else: return False

def generateFileOpt(fromDate, toDate, week):
    dictionaryInputs={
        "{Expert}":"VWap EA.ex5",
        "{ExpertParameters}":"VWapOpt.set",
        "{Symbol}":"EURUSD",
        "{Period}":"M5",
        "{FromDate}":fromDate.strftime("%Y.%m.%d"),
        "{ToDate}":toDate.strftime("%Y.%m.%d"),
        "{Report}":f"optVWAP{fromDate.year}W{week}",
    }

    parsedString = parseToSetOrIni(dictionaryInputs, "myCommonStrategyOptimazerModel.ini")
    
    f = open(f"myCommonStrategyOptimazer{fromDate.year}W{week}.ini","w", encoding='utf-16')

    f.write(parsedString)


generateFileOpt(datetime(2020,12,28),datetime(2021,1,3),53)
#print(Week(2021,1).monday())

    