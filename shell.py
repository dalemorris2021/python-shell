from abc import ABC
import argparse
import sys
from typing import Self, TextIO

PROGRAM_NAME = sys.argv[0]
MAX_FILE_DATA = 4096
ROWS = 32
COLUMNS = 64
BYTES = 32
HEADER = '''XX:                1               2               3
XX:0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF\n'''

class Config:
    def __init__(self: Self, in_file: TextIO = None) -> Self:
        self.in_file = in_file


class Cluster(ABC):
    pass


class EmptyCluster(Cluster):
    def __init__(self: Self, next_empty: int) -> Self:
        self.next_empty = next_empty


class DamagedCluster(Cluster):
    def __init__(self: Self, next_damaged: int) -> Self:
        self.next_damaged = next_damaged


class FileDataCluster(Cluster):
    def __init__(self: Self, content: str, next_data: int) -> Self:
        self.content = content
        self.next_data = next_data


class FileHeaderCluster(Cluster):
    def __init__(self: Self, name: str, content: str, next_header: int, next_data: int) -> Self:
        self.name = name
        self.content = content
        self.next_header = next_header
        self.next_data = next_data


class RootCluster(Cluster):
    def __init__(self: Self, name: str, empty: int, damaged: int, headers: int) -> Self:
        self.name = name
        self.empty = empty
        self.damaged = damaged
        self.headers = headers


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


def rawToCluster(raw: list[int]) -> Cluster:
    type = raw[0]
    match type:
        case 0:
            name = ''
            for i in range(4, BYTES):
                b = chr(raw[i])
                if b == 0:
                    break
                else:
                    name += b
            empty = chr(raw[1])
            damaged = chr(raw[2])
            headers = chr(raw[3])
            cluster = RootCluster(name, empty, damaged, headers)
        case 1:
            next_empty = chr(raw[1])
            cluster = EmptyCluster(next_empty)
        case 2:
            next_damaged = chr(raw[1])
            cluster = DamagedCluster(next_damaged)
        case 3:
            name = ''
            content = ''
            for i in range(3, BYTES):
                b = chr(raw[i])
                if b == 0:
                    content_start = i + 1
                    break
                else:
                    name += b
            for i in range(content_start, BYTES):
                b = chr(raw[i])
                if b == 0:
                    break
                else:
                    content += b
            next_header = chr(raw[1])
            next_data = chr(raw[2])
            cluster = FileHeaderCluster(name, content, next_header, next_data)
        case 4:
            content = ''
            for i in range(2, BYTES):
                b = chr(raw[i])
                if b == 0:
                    break
                else:
                    content += b
            next_data = chr(raw[1])
            cluster = FileDataCluster(content, next_data)
    
    return cluster


def rawToClusters(raw: list[list[int]]) -> list[Cluster]:
    clusters = []
    for i in range(len(raw)):
        clusters.append(rawToCluster(raw[i]))
    
    return clusters


def run(config: Config) -> None:
    contents = config.in_file.read(MAX_FILE_DATA)
    
    raw = contentsToRaw(contents)
    clusters = rawToClusters(raw)
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
