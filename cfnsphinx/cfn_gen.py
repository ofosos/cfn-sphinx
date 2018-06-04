import yaml
import json


class CfnExporter:
    def format(self, yml, nesting):
        res = ""
        if type(yml) is type([]):
            for el in yml:
                if type(el) is type(""):
                    res = res + "* " + el + "\n" + (" " * nesting)
                else:
                    res = res + "* " + self.format(el, nesting + 1) + "\n" + (" " * nesting)
        elif type(yml) is type({}):
            res = res + "\n" + (" " * (nesting))
            for k, v in yml.items():
                res = res + k + "\n" + (" " * (nesting + 2)) + self.format(v, nesting + 2) + "\n" + (" " * nesting)
        else: #string, int, float?
            return str(yml)

        return res
    
    def from_data(self, yml, document):
        reslis = []

        name = "CfnStack"
        reslis.append("{}\n{}\n{}\n\n".format("=" * len(name),
                                              name, "=" * len(name)))

        if 'Parameters' in yml:
            name = "Parameters"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Parameters'].items():
                name = key
                typ = val['Type']

                vals = ['Description', 'Default', 'AllowedValues',
                        'ConstraintDescription']

                reslis.append(".. cfn:parameter:: {}".format(name))
                reslis.append("    :type: {}\n".format(typ))
                for v in vals:
                    if v in val:
                        reslis.append("    :{}: {}\n".format(v.lower(), val[v]))

                reslis.append("")

        if 'Mappings' in yml:
            name = "Mappings"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Mappings'].items():
                name = key
                typ = 'Mapping'

                reslis.append(".. cfn:mapping:: {}\n".format(name))
                reslis.append((" " * 6) + self.format(val, 6))

                reslis.append("")

        if 'Conditions' in yml:
            name = "Conditions"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Conditions'].items():
                name = key
                typ = 'Condition'

                reslis.append(".. cfn:condition:: {}\n".format(name))
                reslis.append((" " * 6) + self.format(val, 6))

                reslis.append("")


            name = "Resources"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

        if 'Resources' in yml:
            for key, val in yml['Resources'].items():
                name = key
                typ = val['Type']
                prop = val['Properties']

                vals = ['Description', 'Default', 'AllowedValues',
                        'ConstraintDescription']

                reslis.append(".. cfn:resource:: {}".format(name))
                reslis.append("   :type: {}\n".format(typ))
                for v in vals:
                    if v in val:
                        reslis.append("    :{}:\n".format(v.lower()))
                        reslis.append((" " * 5) + self.format(val[v], 5))

                for k, v in prop.items():
                    reslis.append("    :{}:\n".format(k))
                    reslis.append((" " * 5) + self.format(v, 5))
                reslis.append("")

        if 'Outputs' in yml:
            name = "Outputs"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Outputs'].items():
                name = key

                keylis = ['Description', 'Value']

                reslis.append(".. cfn:output:: {}\n".format(name))
                for lookup in keylis:
                    if lookup in val:
                        reslis.append("     :{}: {}".format(lookup, (" " * 6) + self.format(val[lookup], 6)))

                reslis.append("")

        return '\n'.join(reslis)


class CfnParserYaml:
    @classmethod
    def parse(cls, inputstring, document):
        y = yaml.load(inputstring)
        exporter = CfnExporter()
        rest = exporter.from_data(y, document)

        return rest


class CfnParserJson:
    @classmethod
    def parse(cls, inputstring, document):
        y = json.loads(inputstring)
        exporter = CfnExporter()
        rest = exporter.from_data(y, document)

        return rest
