from cfnsphinx.cfn_gen import CfnParserJson, CfnParserYaml
import argparse

class CfnBuilder:
    @classmethod
    def run(cls, args):
        print("Processing {}...".format(args.input))
        out = ""

        with open(args.input, 'r') as f:
            data = f.read()

            if args.json:
                out = CfnParserJson.parse(data, args.input)
            else:
                out = CfnParserYaml.parse(data, args.input)

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
