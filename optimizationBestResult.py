
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats

def xml_2_xlsx(path):
    
    f = open(path, encoding='utf-8')
    xml_data = f.read()
    f.close()

    root = ET.fromstring(xml_data)

    all = []
    col = []
    for i in range(len(root[2][0])):
        for n in range(len(root[2][0][0])):
            if root[2][0][i][n][0].text==None:
                col.append(root[2][0][i][n][0].text)    
            else: col.append(root[2][0][i][n][0].text.strip())
        all.append(col)
        col = []

    df = pd.DataFrame(all)
    df = df.set_axis(df.iloc[0,:], axis=1)
    df = df.drop(0, axis=0)
    df=df.astype({'Trades': int})
    df=df[df.Trades>0]
    dict={'Pass':int, 'Result': float, 'Profit': float, 'Expected Payoff': float, 'Profit Factor': float,
       'Recovery Factor': float, 'Sharpe Ratio': float, 'Custom': float, 'Equity DD %': float, 'Trades': int,
       'SlFactor': float, 'TpFactor': float, 'atrPeriod': int, 'delta': float, 'option': int, 'fastEmaPeriod': int,
       'slowEMAPeriod': int}
   # print(df.astype(dict))
    df=df.astype(dict)
    return df 





"""Ratio list variable toma 2 pesos relativos, el primero es resultado > 0 respecto al total, la segunda es resultado > 1 respecto al total, """


# iterate over files in the folder directory
# return a list of df with all the data of the xml files
def file_XLM_to_df(directory,cleaned=True):
    DataFrameDict={}
    CleanDataFrameDict={}
    files = os.listdir(directory)
    for filename in sorted(files):
        F = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(F): 
            if F[-4:]==".xml":
            
                DF = xml_2_xlsx(F)
                DataFrameDict[F]=DF
              
                # print(f"***************************************{F}****************************************")
                # print(DF.head(20).to_string())
                DF=DF.groupby("Profit").agg({'Result':np.mean, 
                        'Expected Payoff':np.mean, 
                        'Profit Factor':np.mean,
                        'Recovery Factor':np.mean, 
                        'Sharpe Ratio':np.mean,
                        'Custom': np.mean, 
                        'Equity DD %':np.mean, 
                        'Trades': lambda x: stats.mode(x,keepdims=True)[0][0], 
                        'SlFactor':np.mean,
                        'TpFactor':np.mean, 
                        'atrPeriod':lambda x: stats.mode(x,keepdims=True)[0][0], 
                        'delta':np.mean, 
                        'option':lambda x: stats.mode(x,keepdims=True)[0][0], 
                        'fastEmaPeriod':lambda x: stats.mode(x,keepdims=True)[0][0],
                        'slowEMAPeriod':lambda x: stats.mode(x,keepdims=True)[0][0]})
                DF['delta']= DF['delta'].round(2)
                DF=DF.sort_values(by=["Result"],ascending=False,)

                CleanDataFrameDict[F]=DF
    print(f"******************************** All files from {directory} cleaned *********************************")
    if cleaned:
        return CleanDataFrameDict
    else: return DataFrameDict

def normOfDiference(list1,list2):
    arr1=np.array(list1)
    arr2=np.array(list2)
    dif=np.subtract(arr1,arr2)
    return round(np.linalg.norm(dif),3)


_2015data=file_XLM_to_df("2015")
_2016data=file_XLM_to_df("2016")
_2017data=file_XLM_to_df("2017")
_2018data=file_XLM_to_df("2018")
_2019data=file_XLM_to_df("2019")
_2020data=file_XLM_to_df("2020")



_2015Best={}
_2016Best={}
_2017Best={}
_2018Best={}
_2019Best={}
_2020Best={}


for i in _2015data:
    _2015Best[i[5:-4]]=_2015data[i][_2015data[i].Trades>30].iloc[0,:]

    
for i in _2016data:
    _2016Best[i[5:-4]]=_2016data[i][_2016data[i].Trades>30].iloc[0,:]
    
for i in _2017data:
    _2017Best[i[5:-4]]=_2017data[i][_2017data[i].Trades>30].iloc[0,:]
    
for i in _2018data:
    _2018Best[i[5:-4]]= _2018data[i][_2018data[i].Trades>30].iloc[0,:]
    
for i in _2019data:
    _2019Best[i[5:-4]]=_2019data[i][_2019data[i].Trades>30].iloc[0,:]
    
for i in _2020data:
    _2020Best[i[5:-4]]=_2020data[i][_2020data[i].Trades>30].iloc[0,:]
    

_2015df=pd.DataFrame(_2015Best)

_2016df=pd.DataFrame(_2016Best)

_2017df=pd.DataFrame(_2017Best)

_2018df=pd.DataFrame(_2018Best)

_2019df=pd.DataFrame(_2019Best)

_2020df=pd.DataFrame(_2020Best)

allBestData_df=pd.concat([_2015df,_2016df,_2017df,_2018df,_2019df,_2020df],axis=1)


list1=allBestData_df.iloc[-8:,0].to_list()
# list2=allBestData_df.iloc[-8:,1].to_list()

allBestData_df.to_excel("BestResults.xlsx")





print("BestResults.csv CREATED")
