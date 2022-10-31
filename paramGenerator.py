import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime


from paramsParserToSetOrIni import parseToSetOrIni

def isBisiesto(year):
    return not year % 4 and (year % 100 or not year % 400)

def has53Weeks(year):
    if((isBisiesto(year) and datetime(year,1,1).weekday() == 2) or (datetime(year,1,1).weekday() == 3)):
        return True
    else: return False

def normOfDiference(list1,list2):
    arr1=np.array(list1)
    arr2=np.array(list2)
    dif=np.subtract(arr1,arr2)
    return round(np.linalg.norm(dif),3)

def refTupleGenerator(refY,refW,Estrategy=1):
    data=[]
    if Estrategy==1:
        refYUpper=refY-1
        refWUpper=refW+2
        
        refYLower=refY-1
        refWLower=refW-4
        
        if refWLower<=0:
            refYLower-=1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWLower=weeksY+refWLower
        elif refWUpper>(53 if has53Weeks(refYLower) else 52):
            refYUpper+=1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWUpper=refWUpper-weeksY
            
        data=[(refYLower,refWLower),(refYUpper,refWUpper),(refY,refW)]
        #print(data)
        
    if Estrategy==2: 
        refYLower=refY-1
        refWLower=refW-4

        refYUpper=refY-1
        refWUpper=refW 
        if (refW == 53 and has53Weeks(refYUpper)) or refW !=53:
            pass
        else:
            refWUpper=1
            refYUpper+=1
        
        if refWLower<=0:
            refYLower-=1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWLower=weeksY+refWLower
        

        data=[(refYLower,refWLower),(refYUpper,refWUpper),(refY,refW)]
        
        #print(data)

    if Estrategy==3: 
        refYLower=refY
        refWLower=refW-4

        refYUpper=refY
        refWUpper=refW - 1
        
        if refWLower<=0:
            refYLower-= 1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWLower=weeksY+refWLower

        if refWUpper<=0:
            refYUpper-=1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWUpper=weeksY+refWUpper
        data=[(refYLower,refWLower),(refYUpper,refWUpper),(refY,refW)]
    
    if Estrategy==4: 
        refYLower=refY
        refWLower=refW-8

        refYUpper=refY
        refWUpper=refW - 1
        
        if refWLower<=0:
            refYLower-= 1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWLower=weeksY+refWLower

        if refWUpper<=0:
            refYUpper-=1
            weeksY = 53 if has53Weeks(refYLower) else 52
            refWUpper=weeksY+refWUpper
        data=[(refYLower,refWLower),(refYUpper,refWUpper),(refY,refW)]

    return data

def ParamEstimator(ref,relationMatrix,allMedianResults,Estrategy=1,dropFistYear=False):
    years=[2016,2017,2018,2019,2020]
    if dropFistYear:years=years[1:]
    newRow=[]

    flag52 = False
    for i in years:
        if ref == 53 and not has53Weeks(i):
            ref = 52
            flag52 = True
        Ref=refTupleGenerator(i,ref,Estrategy)
        print(Ref)
        newRow.append(relationMatrix.loc[Ref[0]:Ref[1],Ref[2]].idxmin()[1])
        if flag52: ref = 53
        
    refWeek = pd.DataFrame()
    if not(dropFistYear):
        refWeek=pd.concat([allMedianResults[years[0],newRow[0]],
        allMedianResults[years[1],newRow[1]],
        allMedianResults[years[2],newRow[2]],
        allMedianResults[years[3],newRow[3]],
        allMedianResults[years[4],newRow[4]]],axis=1).iloc[8:,:].T
    else:
        refWeek=pd.concat([allMedianResults[years[0],newRow[0]],
        allMedianResults[years[1],newRow[1]],
        allMedianResults[years[2],newRow[2]],
        allMedianResults[years[3],newRow[3]]],axis=1).iloc[8:,:].T

    new_configuration = {
    "{SlFactorInput}":refWeek.loc[:,"SlFactor"].mean(),
    "{TpFactorInput}":refWeek.loc[:,"TpFactor"].mean(),
    "{atrPeriodInput}":round(refWeek.loc[:,"atrPeriod"].median()),
    "{deltaInput}":-1,
    "{optionInput}":refWeek.loc[:,"option"].mode().iloc[0],
    "{fastEmaPeriodInput}":round(refWeek.loc[:,"fastEmaPeriod"].median()),
    "{slowEMAPeriodInput}":round(refWeek.loc[:,"slowEMAPeriod"].median()),
    }

    if new_configuration["{optionInput}"] == 2:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==2].delta.mean()

    elif new_configuration["{optionInput}"] == 1:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==1].delta.mean()
    else:
        new_configuration["{deltaInput}"] = 0

    return new_configuration

def ParamEstimator2(ref,relationMatrix,allMedianResults,Estrategy=2,dropFistYear=False):
    Ref=refTupleGenerator(2021,ref,Estrategy)
    refWeek = allMedianResults.loc[:,Ref[0]:Ref[1]].T

    #print(refWeek.to_string())

    new_configuration = {
    "{SlFactorInput}":refWeek.loc[:,"SlFactor"].mean(),
    "{TpFactorInput}":refWeek.loc[:,"TpFactor"].mean(),
    "{atrPeriodInput}":round(refWeek.loc[:,"atrPeriod"].median()),
    "{deltaInput}":-1,
    "{optionInput}":refWeek.loc[:,"option"].mode().iloc[0],
    "{fastEmaPeriodInput}":round(refWeek.loc[:,"fastEmaPeriod"].median()),
    "{slowEMAPeriodInput}":round(refWeek.loc[:,"slowEMAPeriod"].median()),
    }

    if new_configuration["{optionInput}"] == 2:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==2].delta.mean()

    elif new_configuration["{optionInput}"] == 1:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==1].delta.mean()
    else:
        new_configuration["{deltaInput}"] = 0

    return new_configuration

def ParamEstimator53(ref,relationMatrix,allMedianResults,Estrategy=1,dropFistYear=False):
    years=[2017,2018,2019,2020,2021]
    if dropFistYear:years=years[1:]
    newRow=[]


    for i in years:
        if ref == 53 and not has53Weeks(i):
            ref = 52
        Ref=refTupleGenerator(i,ref,Estrategy)
        print(Ref)
        newRow.append(relationMatrix.loc[Ref[0]:Ref[1],Ref[2]].idxmin()[1])
        ref = 53
        
    refWeek = pd.DataFrame()
    if not(dropFistYear):
        refWeek=pd.concat([allMedianResults[years[0],newRow[0]],
        allMedianResults[years[1],newRow[1]],
        allMedianResults[years[2],newRow[2]],
        allMedianResults[years[3],newRow[3]],
        allMedianResults[years[4],newRow[4]]],axis=1).iloc[8:,:].T
    else:
        refWeek=pd.concat([allMedianResults[years[0],newRow[0]],
        allMedianResults[years[1],newRow[1]],
        allMedianResults[years[2],newRow[2]],
        allMedianResults[years[3],newRow[3]]],axis=1).iloc[8:,:].T

    new_configuration = {
    "{SlFactorInput}":refWeek.loc[:,"SlFactor"].mean(),
    "{TpFactorInput}":refWeek.loc[:,"TpFactor"].mean(),
    "{atrPeriodInput}":round(refWeek.loc[:,"atrPeriod"].median()),
    "{deltaInput}":-1,
    "{optionInput}":refWeek.loc[:,"option"].mode().iloc[0],
    "{fastEmaPeriodInput}":round(refWeek.loc[:,"fastEmaPeriod"].median()),
    "{slowEMAPeriodInput}":round(refWeek.loc[:,"slowEMAPeriod"].median()),
    }

    if new_configuration["{optionInput}"] == 2:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==2].delta.mean()

    elif new_configuration["{optionInput}"] == 1:
        new_configuration["{deltaInput}"] = refWeek[refWeek.option==1].delta.mean()
    else:
        new_configuration["{deltaInput}"] = 0

    return new_configuration

allBestData_df=pd.read_excel("BestMedianResults.xlsx",index_col=0)

data={}
for ref in range(len(allBestData_df.columns)):   
    fila=[]
    list1=allBestData_df.iloc[-7:,ref].to_list()
    rowName=allBestData_df.iloc[-7:,ref].name
    for i in range(len(allBestData_df.columns)):
        list2=allBestData_df.iloc[-7:,i].to_list()
        fila.append(normOfDiference(list1,list2))
    data[rowName]=fila

relationMatrix=pd.DataFrame(data,index=allBestData_df.columns)
relationMatrix.to_excel("RelationM.xlsx")
mIndex=[]
for i in relationMatrix.columns.to_list():
    mIndex.append((int(i[:4]),int(i[5:])))

# 
index = pd.MultiIndex.from_tuples(mIndex, names=["Year", "Week"])


RelationMatrix=pd.DataFrame(relationMatrix.values,index,columns=index)
AllBestData=pd.DataFrame(allBestData_df.values,allBestData_df.index,columns=index)
#print(RelationMatrix.to_string())
#print(AllBestData.to_string())

dictionaryInputs={"{ClosePercentInput}":50,
"{SlFactorInput}":None,
"{TpFactorInput}":None,
"{riskPercentageInput}":1,
"{riskRewardTargetInput}":2,
"{minHoldingPeriodInput}":0,
"{atrPeriodInput}":None,
"{deltaInput}":None,
"{optionInput}":None,
"{fastEmaPeriodInput}":None,
"{slowEMAPeriodInput}":None,
"{vwapZoneMultiplyerInput}":2,
"{switchCandelConditionInput}":0,
"{maxDrowdownInput}":100,
"{maxDrowdownAnualInput}":100,
"{maxDrowdownMonthlyInput}":100,
"{maxDrowdownDailyInput}":15,
"{TargetAnualyInput}":80,
"{TargetMonthlyInput}":80,
"{TargetDailyInput}":20}

"""Usaremos multiples estrategias de eleccion y estimacion de parametros
        E1: ubservamos el entorn al rededor de la semana +-2 respecto a la sem de referencia en cada year hacia atras obteniendo la minima diferencia entre los atributos con respecto a la semana de referencia y al final hacemos una media entre los atributos de cada year hacia atras
        E2: igual que la 1 pero solo 4 hacia atras cada year
        E2.1: igual que la 1 pero solo 4 hacia atras cada year pero en este caso en vez de hacerlo con la semana de referencia se hace con la ultima semana del year
        E3: tomamos 4 hacia atra solo coin respecto a la semana actual y no se calcula ninguna relacion con la semana actual ya que seria trampa, simplementa sacamos la media de todas las semanas escogidas
        E4: lo mismo que la anterior pero variando la cantidad de semanas hacia atras
        """

_weeksGeneratedParams = {}
for i in range(1,53):
    _completeParams = dictionaryInputs | ParamEstimator53(i,RelationMatrix,AllBestData,Estrategy=2,dropFistYear=True) 
    if i > 0 and i <10: i = f"0{i}"
    f = open(f"2022_BT_sets/W{i}.set","w", encoding='utf-16')
    f.write(parseToSetOrIni(_completeParams, "GeneralInputConf.set"))
    f.close()







