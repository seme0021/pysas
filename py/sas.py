

class SAS:
    def __init__(self):
        pass

    def Field(self, name, mtype, sas_length, null, description):
        """
        Python object to hold SAS variable definition.
        name: Variable Name
        mtype: MySQL datatype
        sas_length: SAS Variable Name (ie. 8. or $8.)
        null: True/False whether this field can be NULL
        description: Variable Description
        """
        return {'name': name,
                'mtype': mtype,
                'sas_length': sas_length,
                'null': null,
                'description': description
                }

    def help(self, need):
        """

        """
        if need == 'macro':
            str = """

                  """
            print str

    def Macro(self, name, default, null, description, type='param'):
        """
        Macro function wraps the structural components of a SAS macro into an objects. Main purpose is when defining
        name: name of the macro parameter
        default: default value of the parameter
        null: True/False whether NULLs are allowed
        description: Description of the parameter
        type: parameter type. Supported types are:
            param: standard parameter
            dataset: SAS DataSet
        macro objects like so:

        Examples
        --------
        >>> parms_macro1 = {1: Macro('param1', '&dataset1', 0, 'DataSet description', 'dataset'),
        2: Macro('param2', '&parameter', 0, 'Parameter Description', 'param')
        }
        """
        return {'name': name,
                'default': default,
                'null': null,
                'type': type,
                'description': description
                }

    def sas_dataset(self, obj):
        """
        Reads object defined using the Field function to construct a proper structure of the SAS dataset. Includes keep
        statement and lenght statements. Also, checks for neccessary input variables.
        obj: Object that contains:
            dsn: Dataset Name
            fields: Required Fields, defined by the Field() function
            input_check: Variables to check on input
        """
        null_map = {0: ' not null',
                    1: ' null'
                    }
        l = obj['fields']
        dsn = obj['dsn']

        m = max(l.keys())
        cols = ""
        for i in l.keys():
            cols += l[i]['name'] + " "
        sas = "data %s(keep = %s);" % (dsn, cols) + "\n"
        sas += "   length "
        for i in l.keys():
            sas += l[i]['name'] + ' ' + l[i]['sas_length'] + ' '
        sas += ';' + '\n'
        sas += "   set &dsn_in;" + '\n'
        sas += "/*Your code here*/" + '\n'
        sas += "run;"
        return sas

    def dsn_exists(self, dsn):
        """
        Writes SAS code to check whether a SAS dataset exists.
        dsn: Dataset Name

        Returns a string.
        """
        sp = ' ' * 3
        sas = sp + "%let exists = %sysfunc(exist(&" + str(dsn) + "));\n"
        sas += sp + "%if &exists = 0 %then %do;" + "\n"
        sas += sp + sp + '%' + "put USER ERROR: Dataset %s does not exist;" % dsn + "\n"
        sas += sp + sp + "%abort;" + "\n"
        sas += sp + "%end;" + "\n"
        return sas

    @staticmethod
    def spaces(self, s):
        l = len(s)
        return ' ' * (l + 1)

    def write_macro_call(self, parms, name):
        """
        Writes the SAS code to call the macro
        parms:z
        """
        l = self.spaces(name)
        m = len(parms)
        sas = '%' + '%s(' % name + '\n'
        for i in parms.keys():
            if i != m:
                sas += l + parms[i]['name'] + ' = ' + parms[i]['default'] + ',\n'
            elif i != m:
                sas += l + parms[i]['name'] + ' = ' + parms[i]['default'] + '\n'
        sas += ');'
        return  sas

    def compile_macro(self, parms, name, subroutine=None):
        """
       Writes the SAS code that generates the macro.
       parms: Dictionary that holds Macro definitions of each input.
       name: name of the macro variable to be compiled
       subroutine: list of dictionaries of subroutine calls to be compiled within this macro {'name': ,'parms': }
       """
        l = self.spaces(name)
        m = len(parms)
        #Write the macro header
        sas = '%macro ' + '%s(' % name + '\n'
        for i in parms.keys():
            if i != m:
                sas += l + parms[i]['name'] + ' = ,\n'
            elif i == m:
                sas += l + parms[i]['name'] + ' =  \n'
        sas += ');' + '\n'
        #write the macro description
        sas += '/*' + '=' * 75 + '*\ \n'
        for i in parms.keys():
            sas += '   ' + parms[i]['name'] + ': ' + parms[i]['description'] + ' \n'
        sas += '\n'
        sas += '\*' + '=' * 75 + '*/ \n'
        sas += '\n'
        for i in parms.keys():
            sas += "   %let " + parms[i]['name'] + ' = ' + parms[i]['default'] + '; \n'
        sas += "/*" + '=' * 75 + '*/ \n'
        for i in parms.keys():
            if parms[i]['type'] == 'dataset':
                sas += self.dsn_exists(parms[i]['name'])
        sas += "/*" + '=' * 75 + '*/ \n'
        #if subroutines are included, write the code here )
        if subroutine is not None:
            for sub in subroutine:
                m = len(sub['parms'])
                sas += '   %' + sub['name'] + '(' + '\n'
                for i in sub['parms']:
                    if i != m:
                        sas += ' ' * 16 + sub['parms'][i]['name'] + ' = ' + sub['parms'][i]['default'] + ',\n'
                    elif i == m:
                        sas += ' ' * 16 + sub['parms'][i]['name'] + ' = ' + sub['parms'][i]['default'] + '\n'
                sas += '    );\n'
                sas += '\n'
        sas += '%mend;'
        return  sas

