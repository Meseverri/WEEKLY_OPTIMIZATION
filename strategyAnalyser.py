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

#median_2020_S2 = getRelevantInfoDF("2020_BT_results_Median_S2")
#median_2020_S2_1 = getRelevantInfoDF("2020_BT_results_Median_S2.1")
#plt.plot(median_2020_S2.index.values, median_2020_S2['Relative Profit Acumulated'], label='Median S2 2020')
#plt.plot(median_2020_S2_1.index.values, median_2020_S2_1['Relative Profit Acumulated'], label='Median S2.1 2020')
#plt.axhline(0, color='r', linestyle = ':')
#plt.xlabel('Week')
#plt.ylabel('Relative Balance Accumulated')
#plt.title('Relative Balance Accumulated Graphic', loc='center')
#plt.legend()
#plt.show()


#median_2021_S2 = getRelevantInfoDF("2021_BT_results_Median_S2")
#median_2021_S2_1 = getRelevantInfoDF("2021_BT_results_Median_S2.1")
#median_2021_S2_1_RPT_0_5 = getRelevantInfoDF("2021_BT_results_Median_S2.1_RPT_0.5")


#plt.plot(median_2021_S2.index.values, median_2021_S2['Relative Profit Acumulated'], label='Median S2 2021')
#plt.plot(median_2021_S2_1.index.values, median_2021_S2_1['Relative Profit Acumulated'], label='Median S2.1 2021')
#plt.plot(median_2021_S2_1_RPT_0_5.index.values, median_2021_S2_1_RPT_0_5['Relative Profit Acumulated'], label='Median S2.1 RTP 0.5 2021')
#plt.axhline(0, color='r', linestyle = ':')
#plt.xlabel('Week')
#plt.ylabel('Relative Balance Accumulated')
#plt.title('Relative Balance Accumulated Graphic', loc='center')
#plt.legend()
#plt.show()


#median_2022_S2 = getRelevantInfoDF("2022_BT_results_Median_S2")
median_2022_S2_1 = getRelevantInfoDF("2022_BT_results_Median_S2.1")
median_2022_S2_2 = getRelevantInfoDF("2022_BT_results_Median_S2_2.0")

#plt.plot(median_2022_S2.index.values, median_2022_S2['Relative Profit Acumulated'], label='Median S2 2022')
plt.plot(median_2022_S2_1.index.values, median_2022_S2_1['Relative Profit Acumulated'], label='Median S2.1 2022 hasta W43 version 1.0')
plt.plot(median_2022_S2_2.index.values, median_2022_S2_2['Relative Profit Acumulated'], label='Median S2 2.0 2022 hasta W44')
plt.axhline(0, color='r', linestyle = ':')
plt.xlabel('Week')
plt.ylabel('Relative Balance Accumulated')
plt.title('Relative Balance Accumulated Graphic', loc='center')
plt.legend()
plt.show()

