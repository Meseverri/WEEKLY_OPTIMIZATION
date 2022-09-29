import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def normOfDiference(list1,list2):
    arr1=np.array(list1)
    arr2=np.array(list2)
    dif=np.subtract(arr1,arr2)
    return round(np.linalg.norm(dif),3)

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


index = pd.MultiIndex.from_tuples(mIndex, names=["Year", "Week"])

relationMatrix.to_excel("relationMatrixMedian.xlsx")
print(relationMatrix.to_string())