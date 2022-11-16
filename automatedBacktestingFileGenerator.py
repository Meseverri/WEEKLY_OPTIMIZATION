from datetime import datetime
from paramsParserToSetOrIni import parseToSetOrIni
from isoweek import Week

def isBisiesto(year):
    return not year % 4 and (year % 100 or not year % 400)

def has53Weeks(year):
    if((isBisiesto(year) and datetime(year,1,1).weekday() == 2) or (datetime(year,1,1).weekday() == 3)):
        return True
    else: return False

def generateFileOpt(fromDate, toDate, week, year):
    dictionaryInputs={
        "{Expert}":"VWap EA.ex5",
        "{ExpertParameters}":f"W{week}.set",
        "{Symbol}":"EURUSD",
        "{Period}":"M5",
        "{FromDate}":fromDate.strftime("%Y.%m.%d"),
        "{ToDate}":toDate.strftime("%Y.%m.%d"),
        "{Report}":f"{year}W{week}",
    }

    parsedString = parseToSetOrIni(dictionaryInputs, "myCommonStrategyTesterModel.ini")
    
    f = open(f"{year}_BT_ini/myCommonStrategyBacktesting{year}W{week}.ini","w", encoding='utf-16')

    f.write(parsedString)

    f.close()


year = 2022
weeks = 53 if has53Weeks(year) else 52

for week in range(1,45):
    #print(f"Year {year} Week {week}")
    if week > 0 and week < 10: week = f"0{week}"
    generateFileOpt(Week(year,int(week)).monday(),Week(year,int(week)).sunday(),week,year)

    