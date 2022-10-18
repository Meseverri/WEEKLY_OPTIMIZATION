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


def getRelevantInfoOfHtml(tree):
    _info = {}
    netProfit = float(tree.xpath("//td[text()='Total Net Profit:']/following-sibling::td[1]/b/text()")[0].replace(" ", ""))
    _info['Total Net Profit'] = netProfit
    initialDeposit = float(tree.xpath("//td[text()='Initial Deposit:']/following-sibling::td[1]/b/text()")[0].replace(" ", ""))
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
        _relevantInfoAllHtml[i+1] = getRelevantInfoOfHtml(html.fromstring(htmlString))

    return _relevantInfoAllHtml

def getRelevantInfoDF(resultStrategyFolder):
    htmlStrings = getAllHtmlStrings(resultStrategyFolder)
    weeksInfo = getRelevantInfoAllHtml(htmlStrings)
    weeksInfoDF = pd.DataFrame.from_dict(weeksInfo,orient='index')
    weeksInfoDF.index.name = 'Week'
    weeksInfoDF['Relative Profit Acumulated'] = round(((weeksInfoDF['Relative Profit']/100+1).cumprod()-1)*100, 2)

    return weeksInfoDF


medianS1 = getRelevantInfoDF("2021_BT_results_Median_S1")

plt.plot(medianS1.index.values, medianS1['Relative Profit Acumulated'], label='Median S1')
plt.axhline(0, color='r', linestyle = ':')
plt.xlabel('Week')
plt.ylabel('Relative Balance Accumulated')
plt.title('Relative Balance Accumulated Graphic', loc='center')
plt.legend()
plt.show()

