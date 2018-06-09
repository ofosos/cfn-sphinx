from docutils.parsers import rst
from os.path import basename
import docutils
from docutils import nodes
import sphinx
from docutils.parsers.rst import directives
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.roles import XRefRole
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx import addnodes
import requests

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

    def get_type_node(self):
        return addnodes.desc_type(text=self.options.get('type'))

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(text=sig)
        signode += self.get_type_node()
        return sig

    def add_target_and_index(self, name_cls, sig, signode):
        signode['ids'].append(self.get_meta_type() + '-' + sig)
        if 'noindex' not in self.options:
            objs = self.env.domaindata['cfn']['objects']
            index = self.env.domaindata['cfn']['object_index']
            index["{}.{}.{}".format('cfn', self.get_meta_type(), sig)] =\
                {'type': self.options.get('type')}
            objs.append(("{}.{}.{}".format('cfn', self.get_meta_type(), sig),
                         sig,
                         self.get_meta_type(),
                         self.env.docname,
                         self.get_meta_type() + '-' + sig,
                         0))


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

class CfnMapping(CfnNode):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
    }
    has_content = True

    def get_meta_type(self):
        return 'Mapping'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Mapping)') % (name_cls[0])


class CfnCondition(CfnNode):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
    }
    has_content = True

    def get_meta_type(self):
        return 'Condition'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Condition)') % (name_cls[0])


class CfnResource(CfnNode):
    required_arguments = 1
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
        'type': rst.directives.unchanged,
        'description': rst.directives.unchanged
    }
    has_content = True

    def get_type_node(self):
        typename = self.options.get('type')
        awsref = ''

        if not 'cfncache' in self.env.domaindata['cfn']:
            try:
                # this is the us-east-1 resource spec
                r = requests.get('https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json')
                self.env.domaindata['cfn']['cfncache'] = r.json()
            except:
                print("Error downloading CFN reference JSON.")
        cfncache = self.env.domaindata['cfn']['cfncache']
        awsref = cfncache['ResourceTypes'][typename]['Documentation']

        return nodes.reference(typename,
                               typename,
                               internal=False,
                               refuri=awsref,
                               classes=['awslink'])

    def get_meta_type(self):
        return 'Resource'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Resource)') % (name_cls[0])


class CfnOutput(CfnNode):
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'description': rst.directives.unchanged,
        'value': rst.directives.unchanged        
    }
    has_content = True

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(text=sig)
        signode += addnodes.desc_type(text='Output')
        return sig

    def get_meta_type(self):
        return 'Output'

    def get_index_text(self, stackname, name_cls):
        return _('{} (Cfn Output)') % (name_cls[0])


class CloudformationIndex(Index):

    name = 'cfn'
    localname = 'CloudFormation Index'
    shortname = 'Cfn'

    def __init__(self, *args, **kwargs):
        super(CloudformationIndex, self).__init__(*args, **kwargs)

    def generate(self, docnames=None):
        """Return entries for the index given by *name*.  If *docnames* is
        given, restrict to entries referring to these docnames.

        The return value is a tuple of ``(content, collapse)``, where
        * collapse* is a boolean that determines if sub-entries should
        start collapsed (for output formats that support collapsing
        sub-entries).

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

        content = {}
        items = ((name, dispname, type, docname, anchor)
                 for name, dispname, type, docname, anchor, prio
                 in self.domain.get_objects())
        items = sorted(items, key=lambda item: item[0])
        for name, dispname, type, docname, anchor in items:
            lis = content.setdefault(type, [])
            obj = self.domain.data['object_index'][name]
            lis.append((
                dispname, 0, docname,
                anchor,
                docname, '', obj.get('type')
            ))
        re = [(k, v) for k, v in sorted(content.items())]

        return (re, True)


class CfnDomain(Domain):
    name = 'cfn'
    label = 'CloudFormation'

    roles = {
        'param': XRefRole(),
        'res': XRefRole(),
        'out': XRefRole(),
        'map': XRefRole(),
        'cnd': XRefRole(),
    }

    directives = {
        'parameter': CfnParameter,
        'resource': CfnResource,
        'output': CfnOutput,
        'mapping': CfnMapping,
        'condition': CfnCondition,
    }

    initial_data = {
        'objects': [],  # object list
        'object_index': {},  # name -> object
    }

    indices = [
        CloudformationIndex
    ]

    def get_full_qualified_name(self, node):
        # type: (nodes.Node) -> unicode
        """Return full qualified name for given node."""
        return "{}.{}.{}.{}".format('cfn',
                                    type(node).__name__,
                                    node.options.get('Type'),
                                    node.arguments[0])

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

    def resolve_xref(self, env, fromdocname, builder, typ,
                     target, node, contnode):
        lookup = {
            'res': 'Resource',
            'out': 'Output',
            'param': 'Parameter',
            'map': 'Mapping',
            'cnd': 'Condition',
        }
        meta = lookup[typ]

        todoc, targ = target.split(':', 1)
        return make_refnode(builder, fromdocname, todoc,
                            meta + '-' + targ,
                            contnode, targ)


def setup(app):
    app.add_domain(CfnDomain)

    app.add_node(CodeNode, html=(do_nothing, do_nothing),
                 latex=(do_nothing, do_nothing))
