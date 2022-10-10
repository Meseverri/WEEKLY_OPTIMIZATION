import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from paramsParserToSetOrIni import parseToSetOrIni

def normOfDiference(list1,list2):
    arr1=np.array(list1)
    arr2=np.array(list2)
    dif=np.subtract(arr1,arr2)
    return round(np.linalg.norm(dif),3)

def refTupleGenerator(refY,refW,Estrategy=1):
    WperYdict={2015:53,
          2016:52,
          2017:52,
          2018:52,
          2019:52,
          2020:53}
    data=[]
    if Estrategy==1:
        refYUpper=refY-1
        refWUpper=refW+2
        
        refYLower=refY-1
        refWLower=refW-2
        
        if refWLower<=0:
            refYLower-=1
            refWLower=WperYdict[refYLower]-refWLower
        elif refWUpper>WperYdict[refYLower]:
            refYUpper+=1
            refWUpper=refWUpper-WperYdict[refYLower]
            
        data=[(refYLower,refWLower),(refYUpper,refWUpper),(refY,refW)]
        
    if Estrategy==2:
        refYUpper=refY-1
        refWUpper=refW+2
        
        refYLower=refY-1
        refWLower=refW-2
        pass
    #print(data)
    return data

def ParamEstimator(ref,relationMatrix,allMedianResults,Estrategy=1,dropFistYear=False):
    years=[2016,2017,2018,2019,2020]
    if dropFistYear:years=years[1:]
    newRow=[]
    if Estrategy==1:
        for i in years:
            Ref=refTupleGenerator(i,ref,Estrategy)
            newRow.append(relationMatrix.loc[Ref[0]:Ref[1],Ref[2]].idxmin()[1])
         
    if Estrategy==2:   
        newRow=[relationMatrix[2016,ref][2015].loc[ref-4:ref].idxmin(),
        relationMatrix[2017,ref][2016].loc[ref-4:ref].idxmin(),
        relationMatrix[2018,ref][2017].loc[ref-4:ref].idxmin(),
        relationMatrix[2019,ref][2018].loc[ref-4:ref].idxmin(),
        relationMatrix[2020,ref][2019].loc[ref-4:ref].idxmin()]
        
    #print(newRow)
    #pd.Series(newRow,years).plot(title='Week '+str(ref))
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
    "{atrPeriodInput}":refWeek.loc[:,"atrPeriod"].median(),
    "{deltaInput}":-1,
    "{optionInput}":refWeek.loc[:,"option"].mode().iloc[0],
    "{fastEmaPeriodInput}":refWeek.loc[:,"fastEmaPeriod"].median(),
    "{slowEMAPeriodInput}":refWeek.loc[:,"slowEMAPeriod"].median(),
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
    list1=allBestData_df.iloc[-8:,ref].to_list()
    rowName=allBestData_df.iloc[-8:,ref].name
    for i in range(len(allBestData_df.columns)):
        list2=allBestData_df.iloc[-8:,i].to_list()
        fila.append(normOfDiference(list1,list2))
    data[rowName]=fila

relationMatrix=pd.DataFrame(data,index=allBestData_df.columns)
mIndex=[]
for i in relationMatrix.columns.to_list():
    mIndex.append((int(i[:4]),int(i[5:])))

# 
index = pd.MultiIndex.from_tuples(mIndex, names=["Year", "Week"])


RelationMatrix=pd.DataFrame(relationMatrix.values,index,columns=index)
AllBestData=pd.DataFrame(allBestData_df.values,allBestData_df.index,columns=index)

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
        E1: ubservamos el entorn al rededor de la semana +-2 respecto a la sem de referencia
        E2: tomamos 4 hacia atra
        E3: comparando todas las del año
        E3: comparando 53 semanas hacia atras"""

_weeksGeneratedParams = {}
for i in range(42,50):
    _completeParams = dictionaryInputs | ParamEstimator(i,RelationMatrix,AllBestData,Estrategy=1,dropFistYear=True) 
    if i > 0 and i <10: i = f"0{i}"
    f = open(f"2021_BT_sets/W{i}.set","w", encoding='utf-16')
    f.write(parseToSetOrIni(_completeParams, "GeneralInputConf.set"))
    f.close()







