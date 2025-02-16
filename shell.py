import argparse
import sys

PROGRAM_NAME = sys.argv[0]
MAX_FILE_DATA = 4096
HEADER = '''XX:                1               2               3
XX:0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF\n'''

class Config:
    def __init__(self, in_file):
        self.in_file = in_file


def leftPad(s: str, char: str, n: int) -> str:
    return char * (n - len(s)) + s


def contentsToRaw(contents: str) -> list[list[int]]:
    temp1 = contents.splitlines()[2:]
    for i in range(len(temp1)):
        temp1[i] = '0' + temp1[i][3:len(temp1[i])-1]
    
    raw = []
    for i in range(len(temp1)):
        raw.append([temp1[i][j:j+2] for j in range(0, len(temp1[i]), 2)])
    
    for i in range(len(raw)):
        for j in range(len(raw[0])):
            raw[i][j] = int(raw[i][j], 16)
    
    return raw


def rawToContents(raw: list[list[int]]) -> str:
    temp1 = []
    for i in range(len(raw)):
        temp1.append([])
        for j in range(len(raw[0])):
            temp1[i].append(leftPad(hex(raw[i][j])[2:], '0', 2).upper())
    
    temp2 = []
    for i in range(len(temp1)):
        temp2.append(''.join(temp1[i]))
    for i in range(len(temp2)):
        temp2[i] = leftPad(hex(i)[2:].upper(), '0', 2) + ':' + temp2[i][1:] + '0'
    
    contents = HEADER + '\n'.join(temp2)
    
    return contents


def run(config: Config) -> None:
    contents = config.in_file.read(MAX_FILE_DATA)
    
    raw = contentsToRaw(contents)
    newContents = rawToContents(raw)
    
    print(newContents)


def main() -> None:
    parser = argparse.ArgumentParser(
            prog=PROGRAM_NAME,
            description='A shell for the Flinstone Disk Project.',
            add_help=False,
            usage='%(prog)s [OPTIONS]')
    parser.add_argument('-h', '-H', '-?', '--help', action='help', help='show this help message and exit')
    parser.add_argument('-v', '-V', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-i', action='store', help='input file')
    
    args = parser.parse_args()
    
    if args.i == None:
        in_file = sys.stdin
    else:
        in_file = open(args.i, 'r', encoding='utf-8')
        
    config = Config(in_file)
    
    run(config)
    if config.in_file != sys.stdin:
        config.in_file.close()


if __name__ == '__main__':
    main()
