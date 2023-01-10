import os
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
    #print(i, " ", initialDeposit)
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

"""
Todos los cambios solos son al "VWap EA original"
Cambio1: Se agrega la simulacion del primer cruce de los emas
Cambio2: Se agrega la recalculacion de los VWAPS cuando son modifivados de pivotes para evitar dejar pivotes ya rotos DESCARTADO POR MAL DESEMPEÑO
Cambio3: Se modifica el cambio de los VWAPs para que sean en cada tick en vez de ser en cada vela nueva
Cambio4: Se cierran todos los trades abiertos a partir de las 9 o 11pm DESCARTADO POR MAL DESEMPEÑO 
Cambio5: Se utiliza el TrueRisk tanto en compras como en ventas ya que en el codigo original solo se aplica a las compras DESCARTADO POR MAL DESEMPEÑO
Cambio6: Se invierte la utilizacion del TrueRisk, ahora se usa en ventas y no en las compras DESCARTADO POR MAL DESEMPEÑO
Cambio7: Se cambian las funciones del TrueRisk por las nuevas ya que en el viejo se usa la del seno que en teoria no tiene sentido por la periodicidad que tiene esta funcion y ademas las nuevas funciones estan pensadas para realizar cambios a partir de los 100 minutos (ParamGenerator53 strategy 2)  ESTE CAMBIO CONLLEVA UNA NUEVA OPT
Cambio8: Se cambian las funciones del TrueRisk por las nuevas ya que en el viejo se usa la del seno que en teoria no tiene sentido por la periodicidad que tiene esta funcion y ademas las nuevas funciones estan pensadas para realizar cambios a partir de los 100 minutos (ParamGenerator strategy 1)  ESTE CAMBIO CONLLEVA UNA NUEVA OPT
CambioX: Se eliminan los controles de riesgo por funciones con graficas curvas y se aplica Kelly criterium
"""

#median_2022_53_2 = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2")
# median_2022_53_2_cambio1 = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2_cambio1")
# median_2022_53_2_cambio3 = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2_cambio3")


# median_2022_53_2_fixed = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2_fixed")
# median_2022_53_2_cambio1_fixed = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2_cambio1_fixed")
# median_2022_53_2_cambio3_fixed = getRelevantInfoDF("2022_BT_results_Median_53_Viejo_2_cambio3_fixed")
#median_2022_FunctOriginal_4_original_fixed = getRelevantInfoDF("2022_BT_results_Median_FunctOriginal_4_original_fixed")

median_2022_FunctOriginal_4_cambio1_fixed = getRelevantInfoDF("2022_BT_results_Median_FunctOriginal_4_cambio1_fixed")

median_2022_FunctOriginal_4_cambio2_fixed = getRelevantInfoDF("2022_BT_results_Median_FunctOriginal_4_cambio2_fixed")

median_2022_FunctOriginal_4_cambio3_fixed = getRelevantInfoDF("2022_BT_results_Median_FunctOriginal_4_cambio3_fixed")

#plt.plot(median_2022_53_2.index.values, median_2022_53_2['Relative Profit Acumulated'], label='Median 53 viejo 2')
# plt.plot(median_2022_53_2_cambio1.index.values, median_2022_53_2_cambio1['Relative Profit Acumulated'], label='Median 53 viejo 2 cambio1')
# plt.plot(median_2022_53_2_cambio3.index.values, median_2022_53_2_cambio3['Relative Profit Acumulated'], label='Median 53 viejo 2 cambio3')

# plt.plot(median_2022_53_2_fixed.index.values, median_2022_53_2_fixed['Relative Profit Acumulated'], label='Median 53 viejo 2 fixed')
# plt.plot(median_2022_53_2_cambio1_fixed.index.values, median_2022_53_2_cambio1_fixed['Relative Profit Acumulated'], label='Median 53 viejo 2 cambio1 fixed')
# plt.plot(median_2022_53_2_cambio3_fixed.index.values, median_2022_53_2_cambio3_fixed['Relative Profit Acumulated'], label='Median 53 viejo 2 cambio3 fixed')
#plt.plot(median_2022_FunctOriginal_4_original_fixed.index.values, median_2022_FunctOriginal_4_original_fixed['Relative Profit Acumulated'], label='Median Funcion Original Strategy 4 codigo original fixed')

#plt.plot(median_2022_FunctOriginal_4_cambio1_fixed.index.values, median_2022_FunctOriginal_4_cambio1_fixed['Relative Profit Acumulated'], label='Median Funcion Original Strategy 4 cambio1 fixed')

#plt.plot(median_2022_FunctOriginal_4_cambio2_fixed.index.values, median_2022_FunctOriginal_4_cambio2_fixed['Relative Profit Acumulated'], label='Median Funcion Original Strategy 4 cambio2 fixed')

plt.plot(median_2022_FunctOriginal_4_cambio3_fixed.index.values, median_2022_FunctOriginal_4_cambio3_fixed['Relative Profit Acumulated'], label='Median Funcion Original Strategy 4 cambio3 fixed')

plt.axhline(0, color='r', linestyle = ':')
plt.xlabel('Week')
plt.ylabel('Relative Balance Accumulated')
plt.title('Relative Balance Accumulated Graphic', loc='center')
plt.legend()
plt.show()

