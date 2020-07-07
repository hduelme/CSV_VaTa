
class Message():
    hide: bool
    comboBox: bool
    allowallvalues: bool

    def __init__(self,name,typ,default,allowedvalues,allowedcharacter,description,hide):
        self.name = name
        self.typ = typ
        self.defaultvalues = default
        self.allowedvalues = allowedvalues
        if(allowedvalues[0]=='all'):
            self.allowallvalues = True
        else:
            self.allowallvalues = False
        if (not self.allowallvalues and self.allowedvalues[0] != ""):
            self.comboBox = True
        else:
            self.comboBox = False

        self.allowedcharacter = allowedcharacter
        self.description = description
        if(hide=="False"):
            self.hide = False
        else:
            self.hide = True

        if(not self.allowallvalues and self.allowedvalues[0]!=""):
            self.comboBox = True
        else:
            self.comboBox = False

    def toString(self):
        return "Name: "+self.name+" Typ: "+self.typ+" defaultvalues: "+str(self.defaultvalues)+" allowedvalues: "+self.allowedvalues+" description: "+self.description

    def isvalueAllowed(self,value):
        ok = False
        if((self.typ=="M")and (value=="")):
            return "Darf nicht leer sein."
        if (self.allowallvalues):
            ok = True
        else:
            for a in self.allowedvalues:
                if (value == a):
                    ok = True
        if(ok):
            checked = self.checkValue(value)
            if(checked=="Ok"):
                return "Ok"
            else:
                return "Unerlaubte Zeichen.\n"+checked
        else:
            return "Unerlaubter Wert."

    def checkValue(self,value):
        if(value==""):
            return "Ok"
        else:
            if (self.allowedcharacter=="default"):
                for l in value:
                    if(not (self.checkisNumber(l) or self.checkisLetter(l) or self.checkisDot(l) or self.checkisSonder(l))):
                        return "Muss erlaubtes Zeichen sein."
                return "Ok"

            elif(self.allowedcharacter=="date"):
                for l in value:
                    if(not (self.checkisNumber(l) or self.checkisDot(l))):
                        return "Muss Datum sein."
                return "Ok"

            elif(self.allowedcharacter=="numbers"):
                if(not (self.checkisNumber(value))):
                    return "Muss Zahl sein."
                return "Ok"

            elif(self.allowedcharacter=="letters"):
                if(not (self.checkisLetter(value.replace(" ", "")))):
                    print("NOT LETTER")
                    return "Muss Buchstabe sein."
                return "Ok"

            elif(self.allowedcharacter=="letters+numbers"):
                for l in value:
                    if (not (self.checkisNumber(l) or self.checkisLetter(l))):
                        return "Muss Zahl oder Buchstabe sein."
                return "Ok"

            else:
                print("unknown")
                return "Ok"

    def checkisNumber(self,value):
        if(value.isnumeric()):
            return True
        return False

    def checkisLetter(self,value):
        if(value.isalpha()):
            return True
        return False

    def checkisDot(self,value):
        if(value=="."):
            return True
        return False

    def checkisSonder(self,value):
        if((value=="-")or (value==",") or (value==":") or (value=="%") or (value=="/") or (value=="`") or (value==" ")):
            return True
        return False