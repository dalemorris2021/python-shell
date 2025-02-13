import argparse
import sys

PROGRAM_NAME = sys.argv[0]
MAX_FILE_DATA = 4096

class Config:
    def __init__(self, in_file):
        self.in_file = in_file

def zeroPad2(s):
    if len(s) == 1:
        return '0' + s
    else:
        return s

def contentsToRaw(contents: str) -> list[list[str]]:
    temp1 = contents.splitlines()[2:]
    for i in range(len(temp1)):
        temp1[i] = temp1[i][3:len(temp1[i])-1]
    for i in range(len(temp1)):
        temp1[i] = '0' + temp1[i]
    temp2 = []
    for i in range(len(temp1)):
        temp2.append([temp1[i][j:j+2] for j in range(0, len(temp1[i]), 2)])
    return temp2

def rawToContents(raw: list[list[str]]) -> str:
    temp1 = []
    for i in range(len(raw)):
        temp1.append(''.join(raw[i]))
    for i in range(len(temp1)):
        temp1[i] = temp1[i][1:]
        temp1[i] += '0'
        temp1[i] = zeroPad2(hex(i)[2:].upper()) + ':' + temp1[i]
    temp2 = 'XX:                1               2               3\n' + 'XX:0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF\n'
    temp2 += '\n'.join(temp1)
    return temp2

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
