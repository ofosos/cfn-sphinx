from cfnsphinx.cfn_gen import CfnParserJson, CfnParserYaml
import argparse
from re import match
from os.path import basename

class CfnBuilder:
    @classmethod
    def run(cls, args):
        print("Processing {}...".format(args.input))
        out = ""

        bname = basename(args.input)
        m = match(r'^(.+)(\..+)$', bname)
        docname, _ = m.groups()
        with open(args.input, 'r') as f:
            data = f.read()

            if args.json:
                out = CfnParserJson.parse(data, docname)
            else:
                out = CfnParserYaml.parse(data, docname)

        with open(args.output, 'w') as fo:
            fo.write(out)


def main():
    parser = argparse.ArgumentParser(description='Parse Cfn files and generate RST.')
    parser.add_argument('-j', '--json', dest='json', action='store_true')
    parser.add_argument('-y', '--yaml', dest='yaml', action='store_true')
    parser.add_argument('-f', '--file', dest='input', action='store')
    parser.add_argument('-o', '--output', dest='output', action='store')

    CfnBuilder.run(parser.parse_args())


if __name__ == '__main__':
    main()
