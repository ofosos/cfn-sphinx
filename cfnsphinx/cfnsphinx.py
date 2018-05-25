from docutils.parsers import rst
from os.path import basename
import docutils
import sphinx
import yaml
import json
from docutils.parsers.rst import directives
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.roles import XRefRole
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx import addnodes

class CfnExporter:
    def from_yaml(self, yml):
        reslis = []

        name = "CfnStack"
        reslis.append("{}\n{}\n{}\n\n".format("=" * len(name), name, "=" * len(name)))
        
        for key, val in yml['Parameters'].items():
            name = key
            typ = val['Type']

            vals = ['Description', 'Default', 'AllowedValues', 'ConstraintDescription']

            reslis.append(".. cfn:parameter:: {}".format(name))
            reslis.append("    :type: {}\n".format(typ))
            for v in vals:
                if v in val:
                    reslis.append("    :{}: {}\n".format(v.lower(), val[v]))

            reslis.append("")
        
        for key, val in yml['Resources'].items():
            name = key
            typ = val['Type']
            prop = val['Properties']
            
            reslis.append(".. cfn:resource:: {}".format(name))
            reslis.append("   :type: {}\n".format(typ))
            for k,v in prop.items():
                reslis.append("    :{}: {}\n".format(k,v))
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

class CfnParserJson(rst.Parser):
    supported = ()

    def parse(self, inputstring, document):
        y = json.loads(inputstring)
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

class CfnNode(ObjectDescription):
    """A custom node that represents Cfn elements."""

    option_spec = {
        'noindex': directives.flag
    }

    doc_field_types = [
        Field('type', label=l_('Type'), has_arg=False,
              names=('type', 'typ')),
        Field('description', label=l_('Description'), has_arg=False,
              names=('desc', 'description'))
    ]

    def get_meta_type(self):
        raise NotImplementedError('must be implemented in subclasses')

    def get_index_text(self, stackname, name):
        """
        Return the text for the index entry of the object.
        """
        raise NotImplementedError('must be implemented in subclasses')

    def handle_signature(self, sig, signode):
        print("SIGGY {}".format(sig))
        signode += addnodes.desc_type(sig, '')
        return sig
    
    def add_target_and_index(self, name_cls, sig, signode):
        print("YEAH FOOBAR")
        signode['ids'].append(name_cls[0])
        if 'noindex' not in self.options:
            print("APPEND {}".format(self))
            objs = self.env.domaindata['cfn']['objects']
            index = self.env.domains['cfn'].object_index
            index["{}.{}.{}".format('cfn', self.get_meta_type(), self.arguments[0])] =\
                  self
            print(self.get_meta_type() + '-' + self.arguments[0])
            objs.append(("{}.{}.{}".format('cfn', self.get_meta_type(), self.arguments[0]),self.arguments[0],self.get_meta_type(), self.env.docname, self.get_meta_type() + '-' + self.arguments[0], 0))

class CfnParameter(CfnNode):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
        'type': rst.directives.unchanged
    }
    has_content = True

    def get_meta_type(self):
        return 'Parameter'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Parameter)') % (name_cls[0])


class CfnResource(CfnNode):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
        'type': rst.directives.unchanged
    }
    has_content = True

    def get_meta_type(self):
        return 'Resource'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Resource)') % (name_cls[0])


class CloudformationIndex(Index):

    name = 'cfn'
    localname = 'CloudFormation Index'
    shortname = 'Cfn'

    def __init__(self, *args, **kwargs):
        super(CloudformationIndex, self).__init__(*args, **kwargs)

        # During HTML generation these values pick from class,
        # not from instance so we have a little hack the system
        cls = self.__class__

    def generate(self, docnames=None):
        """Return entries for the index given by *name*.  If *docnames* is
        given, restrict to entries referring to these docnames.

        The return value is a tuple of ``(content, collapse)``, where *collapse*
        is a boolean that determines if sub-entries should start collapsed (for
        output formats that support collapsing sub-entries).

        *content* is a sequence of ``(letter, entries)`` tuples, where *letter*
        is the "heading" for the given *entries*, usually the starting letter.

        *entries* is a sequence of single entries, where a single entry is a
        sequence ``[name, subtype, docname, anchor, extra, qualifier, descr]``.
        The items in this sequence have the following meaning:

        - `name` -- the name of the index entry to be displayed
        - `subtype` -- sub-entry related type:
          0 -- normal entry
          1 -- entry with sub-entries
          2 -- sub-entry
        - `docname` -- docname where the entry is located
        - `anchor` -- anchor for the entry within `docname`
        - `extra` -- extra info for the entry
        - `qualifier` -- qualifier for the description
        - `descr` -- description for the entry

        Qualifier and description are not rendered e.g. in LaTeX output.
        """

        print("YEAH HIT MY CODE")
        for obj in self.domain.get_objects():
            print("DOMAIN {}".format(obj))

        content = {}
        items = ((name, dispname, type, docname, anchor)
                 for name, dispname, type, docname, anchor, prio  in self.domain.get_objects())
        items = sorted(items, key=lambda item: item[0])
        for name, dispname, type, docname, anchor in items:
            lis = content.setdefault(type, [])
            obj = self.domain.object_index[name]
            print("ANCHOR {}".format(anchor))
            lis.append((
                dispname, 0, docname,
                anchor,
                docname, '', obj.options.get('type')
            ))
        re = [ (k, v) for k, v in sorted(content.items()) ]

        print(re)
        return (re, True)


class CfnDomain(Domain):
    name = 'cfn'
    label = 'CloudFormation'

    roles = {
        'param': XRefRole(),
        'res': XRefRole()
    }

    directives = {
        'parameter': CfnParameter,
        'resource': CfnResource
    }
    
    initial_data = {
        'objects': [],  # object list
    }

    object_index = {}
    
    indices = [
        CloudformationIndex
    ]

    def get_full_qualified_name(self, node):
        # type: (nodes.Node) -> unicode
        """Return full qualified name for given node."""
        return "{}.{}.{}.{}".format('cfn', type(node).__name__, node.options.get('Type'), node.arguments[0])

    def get_objects(self):
        """Return an iterable of "object descriptions", which are tuples with
        five items:

        * `name`     -- fully qualified name
        * `dispname` -- name to display when searching/linking
        * `type`     -- object type, a key in ``self.object_types``
        * `docname`  -- the document where it is to be found
        * `anchor`   -- the anchor name for the object
        * `priority` -- how "important" the object is (determines placement
          in search results)

          - 1: default priority (placed before full-text matches)
          - 0: object is important (placed before default-priority objects)
          - 2: object is unimportant (placed after full-text matches)
          - -1: object should not show up in search at all
        """
        for obj in self.data['objects']:
            yield(obj)
    
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
        source_parsers['.json'] = CfnParserJson
        app.config._raw_config['source_parsers'] = source_parsers


def setup(app):
    _add_cfn_parser(app)

    #app.add_directive('cfn-res', CfnResource)
    #app.add_directive('cfn-param', CfnParam)
    app.add_domain(CfnDomain)

    app.add_node(CodeNode, html=(do_nothing, do_nothing), latex=(do_nothing, do_nothing))
