from docutils.parsers import rst
import docutils
import sphinx
import yaml
import requests, json

link_to_aws_json='https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json'

class CfnExporter:
    def from_yaml(self, yml):
        reslis = []

        for key, val in yml['Resources'].items():
            name = key
            typ = val['Type']
            prop = val['Properties']

            reslis.append("======\n{}\n======\n\n".format(name))
            
            reslis.append(".. cfn-res:: {}".format(name))
            reslis.append("   :type: {}\n".format(typ))
            for line in yaml.dump(prop).split("\n"):
                reslis.append("    " + line)
            reslis.append("")
        return '\n'.join(reslis)


class CfnParser(rst.Parser):
    supported = ()

    def parse(self, inputstring, document):
        y = yaml.load(inputstring)
        exporter = CfnExporter()
        rest = exporter.from_yaml(y)

        print("parsed a document")

        rst.Parser.parse(self, rest, document)


def do_nothing(self, node):
    pass


class CodeNode(docutils.nodes.Element):
    """A custom node that contains a literal_block node."""

    @classmethod
    def create(cls, text, data={}, language='none', **kwargs):
        """Create a new CodeNode containing a literal_block node.
        Apparently, this cannot be done in CodeNode.__init__(), see:
        https://groups.google.com/forum/#!topic/sphinx-dev/0chv7BsYuW0
        """

        #default: just return a literal_block with the text in it
        node = docutils.nodes.literal_block(text, text, language=language, **kwargs)

        #check if we can upgrade this into an aws documentation link
        doc_link = data.get("ResourceTypes",{}).get(text,{}).get("Documentation",{})
        if doc_link:
            referencenode = docutils.nodes.reference(text, text, refuri=doc_link, **kwargs)
            node = docutils.nodes.literal_block(" ", " ", referencenode, **kwargs)

        return cls(text, node)


class CfnResource(rst.Directive):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
        'type': rst.directives.unchanged
    }
    has_content = True

    def run(self):
        classes = ['cfn-resource']
        container = docutils.nodes.container(classes=classes)

        name = self.arguments[0]
        typ = self.options.get('type')

        # get the aws documentation links as json
        try:
            response = requests.get(link_to_aws_json).text
            aws_doc = json.loads(response)
        except:
            raise Exception('Downloading and converting the aws documentation references failed.')

        container += CodeNode.create(name, classes=['cfn-res-name'], data=aws_doc)
        container += CodeNode.create(typ, classes=['cfn-res-type'], data=aws_doc)

        text = '\n'.join(self.content.data)
        body = CodeNode.create(text, classes=['cfn-res-definition'], data=aws_doc)

        container += body

        return [container]


def _add_cfn_parser(app):
    """Ugly hack to modify source_suffix and source_parsers.
    Once https://github.com/sphinx-doc/sphinx/pull/2209 is merged (and
    some additional time has passed), this should be replaced by ::
        app.add_source_parser('.ipynb', NotebookParser)
    See also https://github.com/sphinx-doc/sphinx/issues/2162.
    """
    source_suffix = app.config._raw_config.get('source_suffix', ['.rst'])
    if isinstance(source_suffix, sphinx.config.string_types):
        source_suffix = [source_suffix]
    if '.yml' not in source_suffix:
        source_suffix.append('.yml')
        app.config._raw_config['source_suffix'] = source_suffix
    source_parsers = app.config._raw_config.get('source_parsers', {})
    if '.yml' not in source_parsers and 'yml' not in source_parsers:
        source_parsers['.yml'] = CfnParser
        app.config._raw_config['source_parsers'] = source_parsers


def setup(app):
    _add_cfn_parser(app)

    app.add_directive('cfn-res', CfnResource)

    app.add_node(CodeNode, html=(do_nothing, do_nothing), latex=(do_nothing, do_nothing))
