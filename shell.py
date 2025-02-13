MAX_FILE_DATA = 4096

def zeroPad2(s):
    if len(s) == 1:
        return '0' + s
    else:
        return s

def contentsToRaw(contents):
    temp1 = contents.splitlines()[2:]
    for i in range(len(temp1)):
        temp1[i] = temp1[i][3:len(temp1[i])-1]
    for i in range(len(temp1)):
        temp1[i] = '0' + temp1[i]
    temp2 = []
    for i in range(len(temp1)):
        temp2.append([temp1[i][j:j+2] for j in range(0, len(temp1[i]), 2)])
    return temp2

def rawToContents(raw: list[list[str]]):
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

def main():
    with open('data/emptydisk.txt', 'r', encoding='utf-8') as in_file:
        contents = in_file.read(MAX_FILE_DATA)
    
    raw = contentsToRaw(contents)
    newContents = rawToContents(raw)
    
    print(newContents)

if __name__ == '__main__':
    main()
