from abc import ABC
import argparse
from enum import Enum
import sys
from typing import Self, TextIO

PROGRAM_NAME = sys.argv[0]
MAX_FILE_DATA = 4096
ROWS = 32
COLUMNS = 64
BYTES = 32
HEADER = '''XX:                1               2               3
XX:0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF\n'''

class ShellAction(Enum):
    DISK = 0
    DIR = 1


class Config:
    def __init__(self: Self, action: ShellAction, in_file: TextIO = None) -> Self:
        self.action = action
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


def contentsToRaw(contents: str) -> list[list[bytes]]:
    raw = contents.splitlines()[2:]
    for i in range(len(raw)):
        raw[i] = bytes.fromhex('0' + raw[i][3:len(raw[i])-1])

    return raw


def rawToContents(raw: list[list[bytes]]) -> str:
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


def rawToCluster(raw: list[bytes]) -> Cluster:
    type = raw[0]
    match type:
        case 0:
            name = ''
            for i in range(4, BYTES):
                b = chr(raw[i])
                if b == '\0':
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
            content_start = BYTES # Start at BYTES in case name spans entire row
            for i in range(3, BYTES):
                b = chr(raw[i])
                if b == '\0':
                    content_start = i + 1
                    break
                else:
                    name += b
            for i in range(content_start, BYTES):
                b = chr(raw[i])
                if b == '\0':
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
                if b == '\0':
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


def printContents(contents: str) -> None:
    print(contents)


def printFiles(clusters: list[Cluster]) -> None:
    for cluster in clusters:
        if isinstance(cluster, FileHeaderCluster):
            print(cluster.name)


def run(config: Config) -> None:
    contents = config.in_file.read(MAX_FILE_DATA)
    
    raw = contentsToRaw(contents)
    clusters = rawToClusters(raw)
    newContents = rawToContents(raw)
    
    match config.action:
        case ShellAction.DISK:
            printContents(newContents)
        case ShellAction.DIR:
            printFiles(clusters)


def main() -> None:
    parser = argparse.ArgumentParser(
            prog=PROGRAM_NAME,
            description='A shell for the Flinstone Disk Project.',
            add_help=False,
            usage='%(prog)s [OPTIONS]')
    parser.add_argument('-h', '-H', '-?', '--help', action='help', help='show this help message and exit')
    parser.add_argument('-v', '-V', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-i', action='store', help='input file')
    parser.add_argument('-dir', action='store_true', help='list files on disk')
    
    args = parser.parse_args()
    
    if args.i == None:
        in_file = sys.stdin
    else:
        try:
            in_file = open(args.i, 'r', encoding='utf-8')
        except FileNotFoundError:
            print('File not found')
            return
    
    if args.dir:
        action = ShellAction.DIR
    else:
        action = ShellAction.DISK
    
    config = Config(action, in_file)
    
    run(config)
    if config.in_file != sys.stdin:
        config.in_file.close()


if __name__ == '__main__':
    main()
