
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
    for filename in sorted(os.listdir(directory)):
        F = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(F): 
            if F[-4:]==".xml":
            
                DF = xml_2_xlsx(F)
                DataFrameDict[F]=DF
                if len(DF) == 0:
                    print(F)
              
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

def optFilteredData(data):
    BestFiltered={}
    s=""
    for i in data:
        s=i[:4]
        
        _30Trades=data[i][data[i].Trades>30]
        #print(i + " trades>30 --------------------------------------\n" + _30Trades.to_string())
        _Custom=_30Trades[_30Trades.Custom>=1]
        #print(i + " custom>1--------------------------------------\n" + _Custom.to_string())
        _Resultmean1=_Custom[_Custom.Result.mean()+_Custom.Result.std()*2/3<_Custom.Result]
        dataFiltered=_Resultmean1[round(_Resultmean1.Result.median(),2)==round(_Resultmean1.Result,2)].sort_values('Equity DD %')
        #print(i + " Median--------------------------------------\n" + dataFiltered.to_string())
        if len(dataFiltered)!=0:   
             BestFiltered[i[5:-4]]=dataFiltered.iloc[0,:]
        else:
            print("Vacio")
            delta = 0
            while (True):
                delta += 0.01
                dataFiltered=_Resultmean1[round(_Resultmean1.Result.median()+delta,2)==round(_Resultmean1.Result,2)].sort_values('Equity DD %')
                if len(dataFiltered)!=0: 
                    BestFiltered[i[5:-4]]=dataFiltered.iloc[0,:]
                    print("Encuentra")
                    break
            
    print(f"****{s} succesfully Filtered**** ") 
    return BestFiltered

_2015data=file_XLM_to_df("2015")
_2016data=file_XLM_to_df("2016")
_2017data=file_XLM_to_df("2017")
_2018data=file_XLM_to_df("2018")
_2019data=file_XLM_to_df("2019")
_2020data=file_XLM_to_df("2020")
_2021data=file_XLM_to_df("2021")
_2022data=file_XLM_to_df("2022")


_2015BestFiltered=optFilteredData(_2015data)
_2016BestFiltered=optFilteredData(_2016data)
_2017BestFiltered=optFilteredData(_2017data)
_2018BestFiltered=optFilteredData(_2018data)
_2019BestFiltered=optFilteredData(_2019data)
_2020BestFiltered=optFilteredData(_2020data)
_2021BestFiltered=optFilteredData(_2021data)
_2022BestFiltered=optFilteredData(_2022data)



_2015df=pd.DataFrame(_2015BestFiltered)
_2016df=pd.DataFrame(_2016BestFiltered)
_2017df=pd.DataFrame(_2017BestFiltered)
_2018df=pd.DataFrame(_2018BestFiltered)
_2019df=pd.DataFrame(_2019BestFiltered)
_2020df=pd.DataFrame(_2020BestFiltered)
_2021df=pd.DataFrame(_2021BestFiltered)
_2022df=pd.DataFrame(_2022BestFiltered)

#allBestMedianData_df=pd.concat([_2015df],axis=1)

allBestMedianData_df=pd.concat([_2015df,_2016df,_2017df,_2018df,_2019df,_2020df,_2021df,_2022df],axis=1)

allBestMedianData_df.to_excel("BestMedianResults.xlsx")
print("***************** 100 % *****************")

