from configparser import ConfigParser
import Message


class Config:
    def __init__(self):
        self.read_Sections = []
        self.lastFile = ""
        self.linesperpage = 100
        self.encoding = 'utf-8'
        self.dateformate = '%d.%m.%Y'

    def createConfig(self, Sections):
        config = ConfigParser()
        config.insert_comment('Test')
        config['settings'] = {
            'lastFile': '',
            'linessperpage': '100',
            'encoding': 'UTF8'
        }

        x = 0
        for s in Sections:
            config['Section' + str(x)] = {
                'name': s,
                'typ': 'O',
                'defaultValues': '',
                'allowedValues': 'all',
                'allowedcharacter': 'default',
                'Description': 'missing'
            }
            x += 1
        with open('config.cfg', 'w') as f:
            config.write(f)

    def read_Config(self):
        parser = ConfigParser()
        parser.read('config.cfg')
        sections = parser.sections()
        for s in sections:
            if s == 'settings':
                if 'lastfile' in parser.options(s):
                    self.lastFile = parser.get(s, 'lastfile')
                else:
                    print('Missing LastFile-Option')
                if 'linessperpage' in parser.options(s):
                    self.wordsperpage = parser.get(s, 'linessperpage')
                else:
                    print('Missing linessperpage-Option')
                if 'encoding' in parser.options(s):
                    self.encoding = parser.get(s, 'encoding')
                else:
                    print('Missing encoding-Option')
                if 'dateformate' in parser.options(s):
                    self.dateformate = parser.get(s, 'dateformate')
                else:
                    print('Missing dateformate-Option')
            else:
                name = "?"
                typ = "?"
                defaultvalues = ""
                allowedvalues = "all"
                allowedcharacter = "default"
                description = "missing"
                hide = "False"
                if 'name' in parser.options(s):
                    name = parser.get(s, 'name')
                else:
                    print("Missing name for: " + s)
                if 'typ' in parser.options(s):
                    typ = parser.get(s, 'typ')
                else:
                    print("Missing typ for: " + s)
                if 'defaultvalues' in parser.options(s):
                    defaultvalues = parser.get(s, 'defaultvalues')
                else:
                    print("Missing defaultvalues for: " + s)
                if 'allowedvalues' in parser.options(s):
                    allowedvalues = parser.get(s, 'allowedvalues')
                    array = allowedvalues.split(';')
                else:
                    print("Missing allowedvalues for: " + s)
                if 'allowedcharacter' in parser.options(s):
                    allowedcharacter = parser.get(s, 'allowedcharacter')
                else:
                    print("Missing allowedcharacter for: " + s)
                if 'description' in parser.options(s):
                    description = parser.get(s, 'description')
                else:
                    print("Missing description for: " + s)
                if 'hide' in parser.options(s):
                    hide = parser.get(s, 'hide')
                else:
                    print("Missing hide for: " + s)
                m = Message.Message(name, typ, defaultvalues, array, allowedcharacter, description, hide,
                                    self.dateformate)
                self.read_Sections.append(m)

    def save_currentFile(self, file):
        config = ConfigParser()
        config.read('config.cfg')
        config.set('settings', 'lastFile', file)
        with open('config.cfg', 'w') as f:
            config.write(f)
