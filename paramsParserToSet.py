import re

def parseToSet (_params, baseFile):
    f = open(baseFile,"r")
    baseFileConf = f.read()
    print(baseFileConf)

    for word, replacement in _params.items():
        baseFileConf = baseFileConf.replace(word, replacement)

    return baseFileConf

    
_dic = {"{ClosePercentInput}":"Hola soy german"}
print(parseToSet(_dic, "GeneralInputConf.set"))

