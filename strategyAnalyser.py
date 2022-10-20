from cProfile import label
import json
import os
from turtle import color
import pandas as pd
from lxml import html
import matplotlib.pyplot as plt

def getAllHtmlStrings(directory):
    allHtmlStrings=[]
    for filename in sorted(os.listdir(directory)):
            F = os.path.join(directory, filename)
            if os.path.isfile(F): 
                if F[-4:]==".htm" or F[-5:]==".html":
                    f = open(F, "r", encoding='utf-16')
                    allHtmlStrings.append(f.read())
                    f.close()
    
    return allHtmlStrings


def getRelevantInfoOfHtml(tree,i):
    _info = {}
    netProfit = float(tree.xpath("//td[text()='Total Net Profit:']/following-sibling::td[1]/b/text()")[0].replace(" ", ""))
    _info['Total Net Profit'] = netProfit
    initialDeposit = float(tree.xpath("//td[text()='Initial Deposit:']/following-sibling::td[1]/b/text()")[0].replace(" ", ""))
    print(i, " ", initialDeposit)
    relativeProfit = (netProfit*100)/initialDeposit
    _info['Relative Profit'] = relativeProfit
    dd = tree.xpath("//td[text()='Balance Drawdown Relative:']/following-sibling::td[1]/b/text()")[0].replace(" ", "")
    _info['Balance Drawdown Relative'] = float(dd[:dd.find('%')])
    _info['Total Trades'] = int(tree.xpath("//td[text()='Total Trades:']/following-sibling::td[1]/b/text()")[0].replace(" ", ""))
    zScore = tree.xpath("//td[text()='Z-Score:']/following-sibling::td[1]/b/text()")[0].replace(" ", "")
    _info['Z-Score'] = float(zScore[:zScore.find('(')-1])

    return _info

def getRelevantInfoAllHtml(allHtmlStrings):
    _relevantInfoAllHtml = {}
    for i, htmlString in enumerate(allHtmlStrings):
        _relevantInfoAllHtml[i+1] = getRelevantInfoOfHtml(html.fromstring(htmlString),i+1)

    return _relevantInfoAllHtml

def getRelevantInfoDF(resultStrategyFolder):
    htmlStrings = getAllHtmlStrings(resultStrategyFolder)
    weeksInfo = getRelevantInfoAllHtml(htmlStrings)
    weeksInfoDF = pd.DataFrame.from_dict(weeksInfo,orient='index')
    weeksInfoDF.index.name = 'Week'
    weeksInfoDF['Relative Profit Acumulated'] = round(((weeksInfoDF['Relative Profit']/100+1).cumprod()-1)*100, 2)

    return weeksInfoDF


#medianS1 = getRelevantInfoDF("2021_BT_results_Median_S1")
#medianS1_4 = getRelevantInfoDF("2021_BT_results_Median_S1_4")
#medianS1_4_2 = getRelevantInfoDF("2021_BT_results_Median_S1_4_2")
medianS2 = getRelevantInfoDF("2021_BT_results_Median_S2")
medianS2_1_1 = getRelevantInfoDF("2021_BT_results_Median_S2_1.1")




#plt.plot(medianS1.index.values, medianS1['Relative Profit Acumulated'], label='Median S1')
#plt.plot(medianS1_4.index.values, medianS1_4['Relative Profit Acumulated'], label='Median S1 4')
#plt.plot(medianS1_4_2.index.values, medianS1_4_2['Relative Profit Acumulated'], label='Median S1 4 2')
plt.plot(medianS2.index.values, medianS2['Relative Profit Acumulated'], label='Median S2')
plt.plot(medianS2_1_1.index.values, medianS2_1_1['Relative Profit Acumulated'], label='Median S2 1.1')

plt.axhline(0, color='r', linestyle = ':')
plt.xlabel('Week')
plt.ylabel('Relative Balance Accumulated')
plt.title('Relative Balance Accumulated Graphic', loc='center')
plt.legend()
plt.show()

