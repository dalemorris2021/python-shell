import argparse
import enum
import sys
from typing import Self, TextIO

PROGRAM_NAME = sys.argv[0]
MAX_FILE_DATA = 4096
HEADER = '''XX:                1               2               3
XX:0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF\n'''

class Config:
    def __init__(self: Self, in_file: TextIO) -> Self:
        self.in_file = in_file


class EmptyCluster:
    def __init__(self: Self, next_empty: Self) -> Self:
        self.next_empty = next_empty


class DamagedCluster:
    def __init__(self: Self, next_damaged: Self) -> Self:
        self.next_damaged = next_damaged


class FileDataCluster:
    def __init__(self: Self, next_data: Self, content: str):
        self.next_data = next_data
        self.content = content


class FileHeaderCluster:
    def __init__(self: Self, next_header: Self, next_data, name: str, content: str) -> Self:
        self.next_header = next_header
        self.next_data = next_data
        self.name = name
        self.content = content


class RootCluster:
    def __init__(self: Self, empty: EmptyCluster, damaged: DamagedCluster, headers: FileHeaderCluster, name: str) -> Self:
        self.empty = empty
        self.damaged = damaged
        self.headers = headers
        self.name = name


def leftPad(s: str, char: str, n: int) -> str:
    return char * (n - len(s)) + s


def contentsToRaw(contents: str) -> list[list[int]]:
    raw = contents.splitlines()[2:]
    for i in range(len(raw)):
        raw[i] = bytes.fromhex('0' + raw[i][3:len(raw[i])-1])

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
