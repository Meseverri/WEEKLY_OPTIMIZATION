from cmath import nan
import re

def parseToSet (_params, baseFile):
    f = open(baseFile,"r", encoding='utf-16')
    baseFileConf = f.read()

    for word, replacement in _params.items():
        try:
            float(replacement)
        except ValueError as ve:
            print("Se ha encontrado un elemento en el diccionario que no es un numero")
            continue
        
        replacement = str(replacement)
        oldBaseFileConf = baseFileConf
        baseFileConf = baseFileConf.replace(word, replacement)
        if oldBaseFileConf == baseFileConf:
            print(f"No se encontro la clave {word}")

    patron = r'\{\w*\}'
    patron_compilado = re.compile(patron)
    restoClaves = patron_compilado.findall(baseFileConf)

    for i in restoClaves:
        baseFileConf = baseFileConf.replace(i, "0.0")

    return baseFileConf

    
dictionaryInputs={
    "{ClosePercentInput}":50,
    "{SlFactorInput}":nan,
    "{TpFactorInput}":nan,
    "{riskPercentageInput}":1,
    "{riskRewardTargetInput}":2,
    "{minHoldingPeriodInput}":0,
    "{atrPeriodInput}":nan,
    "{deltaInput}":nan,
    "{optionInput}":nan,
    "{fastEmaPeriodInput}":nan,
    "{slowEMAPeriodInput}":nan,
    "{vwapZoneMultiplyerInput}":nan,
    "{switchCandelConditionInput}":0,
    "{maxDrowdownInput}":100,
    "{maxDrowdownAnualInput}":100,
    "{maxDrowdownMonthlyInput}":100,
    "{maxDrowdownDailyInput}":15,
    "{TargetAnualyInput}":80,
    "{TargetMonthlyInput}":80,
    "{TargetDailyInput}":20
}
print(parseToSet(dictionaryInputs, "GeneralInputConf.set"))

