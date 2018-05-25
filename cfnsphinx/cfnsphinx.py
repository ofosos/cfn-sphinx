from docutils.parsers import rst
import docutils
import sphinx
import yaml


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
    def create(cls, text, language='none', **kwargs):
        """Create a new CodeNode containing a literal_block node.
        Apparently, this cannot be done in CodeNode.__init__(), see:
        https://groups.google.com/forum/#!topic/sphinx-dev/0chv7BsYuW0
        """
        node = docutils.nodes.literal_block(text, text, language=language,
                                            **kwargs)
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

        container += CodeNode.create(name, classes=['cfn-res-name'])
        container += CodeNode.create(typ, classes=['cfn-res-type'])

        text = '\n'.join(self.content.data)
        body = CodeNode.create(text, classes=['cfn-res-definition'])

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
