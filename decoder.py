from bitarray import bitarray
from binarytree import Node

Base = 2
Byte = 8


def read_from_bin(input_file: str):
    """Decompresses the data and writes it out to the output file"""
    try:
        with open(input_file, "rb") as input_stream:
            # read the size of encoded table 2B 16 bits
            buffer = bitarray()
            buffer.frombytes(input_stream.read(5))
            header = buffer.to01()
            # print(header)

            chunk = int(header[:4], 2) + 1

            startPosition = 4
            numberOfEntries = int(header[startPosition:startPosition + chunk], 2) + 1

            startPosition += chunk
            symbolPadding = int(header[startPosition:startPosition + 4], 2)

            startPosition += 4
            dataPadding = int(header[startPosition:startPosition + 3], 2)

            startPosition += 3 + dataPadding
            data = header[startPosition:]

            # print(header)
            # print(chunk)
            # print(numberOfEntries)
            # print(symbolPadding)
            # print(dataPadding)

            del buffer[:]
            buffer.frombytes(input_stream.read())
            data += buffer.to01()
            # print(data[0:200])
            symbol = ""
            dictionary = {}
            currPosition = 0
            print("Duomenys perskaityti")
            for index in range(0, numberOfEntries):
                symbol = data[currPosition: currPosition + chunk]
                currPosition += chunk
                size_bits = int(data[currPosition: currPosition + Byte], 2)
                currPosition += Byte
                bits = data[currPosition:currPosition + size_bits]
                dictionary.update({bits: symbol})
                data = data[currPosition + size_bits:]
                currPosition = 0

            print("Lentele sudaryta")
            return dictionary, data, symbolPadding

    except OSError:
        print("Failas nerastas.")


def shannon_decoder(inputFile, outputFile):
    decoded_table, binary_text, symbol_padding = read_from_bin(inputFile)

    decoded_text = data_to_text(binary_text, decoded_table)
    print("Dekoduotas tekstas")

    if symbol_padding != 0:
        write_text_to_file(decoded_text[:-symbol_padding], outputFile)

    else:
        write_text_to_file(decoded_text, outputFile)

    print("Dekoduota")


def data_to_text(encoded_data: str, dictionary: dict) -> str:
    symbol = ""
    decoded_text = ""
    root = build_binary_tree(dictionary)
    print("Sudarytas medis")
    currRoot = root
    for bit in encoded_data:
        currRoot = bts(currRoot, bit)
        symbol += bit
        if currRoot is None:
            decoded_text += dictionary[symbol]
            symbol = ""
            currRoot = root
    return decoded_text


def bts(root: Node, word: str) -> None:
    for bit in word:
        if bit == '0':
            root = root.left
        else:
            root = root.right

    if root.left is None and root.right is None:
        return None
    else:
        return root


def build_binary_tree(dictionary: dict) -> Node:
    root = Node(2)
    for value in list(dictionary.keys()):
        currNode = root
        for bit in value:
            if bit == '0':
                if currNode.left is not None:
                    currNode = currNode.left
                else:
                    currNode.left = Node(0)
                    currNode = currNode.left
            else:
                if currNode.right is not None:
                    currNode = currNode.right
                else:
                    currNode.right = Node(1)
                    currNode = currNode.right

    return root



def write_text_to_file(text: str, output_file: str) -> bool:
    try:
        with open(output_file, "wb") as output_stream:
            bitarray(text).tofile(output_stream)
        return True
    except OSError:
        print("Failas nerastas")
    return False
