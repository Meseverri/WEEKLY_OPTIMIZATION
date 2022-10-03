from cmath import nan
import re

def parseToSet (_params, baseFile):
    f = open(baseFile,"r", encoding='utf-16')
    baseFileConf = f.read()

    for word, replacement in _params.items():
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
    "{Expert}":"VWap EA.ex5",
    "{ExpertParameters}":"test1.set",
    "{Symbol}":"EURUSD",
    "{Period}":"M5",
    "{FromDate}":"2011.01.01",
    "{ToDate}":"2011.01.07",
    "{Report}":"test_AutoVWAP",
}
print(parseToSet(dictionaryInputs, "myCommonStrategyTester.ini"))

