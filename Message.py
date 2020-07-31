from datetime import datetime


def check_is_number(value) -> bool:
    if value.isnumeric():
        return True
    return False


def check_is_letter(value) -> bool:
    if value.isalpha():
        return True
    return False


def check_is_dot(value) -> bool:
    if value == ".":
        return True
    return False


def check_is_sonder(value) -> bool:
    if (value == "-") or (value == ",") or (value == ":") or (value == "%") or (value == "/") or (value == "`") or (
            value == " "):
        return True
    return False


class Message:
    hide: bool
    comboBox: bool
    allow_all_values: bool

    def __init__(self, name, typ, default, allowed_values, allowed_character, description, hide, date_format):
        self.name = name
        self.typ = typ
        self.default_values = default
        self.allowed_values = allowed_values
        if allowed_values[0] == 'all':
            self.allow_all_values = True
        else:
            self.allow_all_values = False
        if not self.allow_all_values and self.allowed_values[0] != "":
            self.comboBox = True
        else:
            self.comboBox = False

        self.allowed_character = allowed_character
        self.description = description
        if hide == "False":
            self.hide = False
        else:
            self.hide = True

        if not self.allow_all_values and self.allowed_values[0] != "":
            self.comboBox = True
        else:
            self.comboBox = False
        self.date_format = date_format

    def __str__(self):
        return "Name: " + self.name + " Typ: " + self.typ + " defaultvalues: " + str(
            self.default_values) + " allowedvalues: " + self.allowed_values + " description: " + self.description

    def is_value_allowed(self, value) -> str:
        ok = False
        if (self.typ == "M") and (value == ""):
            return "Darf nicht leer sein."
        if self.allow_all_values:
            ok = True
        else:
            for a in self.allowed_values:
                if value == a:
                    ok = True
        if ok:
            checked = self.check_value(value)
            if checked == "Ok":
                return "Ok"
            else:
                return "Unerlaubte Zeichen.\n" + checked
        else:
            return "Unerlaubter Wert."

    def check_value(self, value) -> str:
        if value == "":
            return "Ok"
        else:
            if self.allowed_character == "default":
                for l in value:
                    if not (check_is_number(l) or check_is_letter(l) or check_is_dot(l) or check_is_sonder(
                            l)):
                        return "Muss erlaubtes Zeichen sein."
                return "Ok"

            elif self.allowed_character == "date":
                try:
                    if value != datetime.strptime(value, self.date_format).strftime(self.date_format):
                        raise ValueError
                    return "Ok"
                except ValueError:
                    return "Muss Datum sein."

            elif self.allowed_character == "numbers":
                if not (check_is_number(value)):
                    return "Muss Zahl sein."
                return "Ok"

            elif self.allowed_character == "letters":
                if not (check_is_letter(value.replace(" ", ""))):
                    print("NOT LETTER")
                    return "Muss Buchstabe sein."
                return "Ok"

            elif self.allowed_character == "letters+numbers":
                for l in value:
                    if not (check_is_number(l) or check_is_letter(l)):
                        return "Muss Zahl oder Buchstabe sein."
                return "Ok"

            else:
                print("unknown")
                return "Ok"
