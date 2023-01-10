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
        "{Expert}":"VWap EA original.ex5",
        "{ExpertParameters}":"VWapOpt.set",
        "{Symbol}":"EURUSD",
        "{Period}":"M5",
        "{FromDate}":fromDate.strftime("%Y.%m.%d"),
        "{ToDate}":toDate.strftime("%Y.%m.%d"),
        "{Report}":f"{year}W{week}",
    }

    parsedString = parseToSetOrIni(dictionaryInputs, "myCommonStrategyOptimazerModel.ini")
    
    f = open(f"AllOpt/{year}/myCommonStrategyOptimazer{year}W{week}.ini","w", encoding='utf-16')

    f.write(parsedString)

    f.close()


#
#print(Week(2015,53).monday())

generateFileOpt(Week(2014,51).monday(),Week(2014,51).sunday(),51,2014)
generateFileOpt(Week(2014,52).monday(),Week(2014,52).sunday(),52,2014)
for year in range(2015,2023):
    weeks = 53 if has53Weeks(year) else 52
    for week in range(1,weeks+1):
        #print(f"Year {year} Week {week}")
        if week > 0 and week < 10: week = f"0{week}"
        generateFileOpt(Week(year,int(week)).monday(),Week(year,int(week)).sunday(),week,year)

# year = 2023
# for week in range(1,50):
#         #print(f"Year {year} Week {week}")
#         if week > 0 and week < 10: week = f"0{week}"
#         generateFileOpt(Week(year,int(week)).monday(),Week(year,int(week)).sunday(),week,year)    