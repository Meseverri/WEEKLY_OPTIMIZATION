import xml.etree.ElementTree as ET
import pandas as pd

f = open('2017/2017W41.xml', encoding='utf-8')
xml_data = f.read()
f.close()

root = ET.fromstring(xml_data)

all = []
col = []
sCountList=[]
rList=[]
rowCount=0

for i in range(len(root[2][0])):
  colCount=0
  for n in range(len(root[2][0][0])):
    
    
    if root[2][0][i][n][0].text==None:
      
      sCountList.append([rowCount,colCount])
      rList.append(rowCount)
      
    colCount+=1
    
    col.append(root[2][0][i][n][0].text)
  rowCount+=1
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
    'slowEMAPeriod': int, 'vwapZoneMultiplyer': int}

# df=df.astype(dict)
print(sCountList)
print(df.iloc[rList,:].to_string())
print(df.to_string())

