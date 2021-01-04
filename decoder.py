from binarytree import Node
from bitarray import bitarray
Base = 2
Byte = 8


def shannon_decoder(inputFile, outputFile):
    binary_table, binary_text, chunk = read_from_bin(inputFile)

    decoded_table = data_to_dictionary(binary_table, chunk)
    print("be sutvarkymu", binary_text)
    symbolPadding = int(binary_text[0:Byte], 2)
    print("simbolio paddingas", symbolPadding)
    text_padding = int(binary_text[-Byte:], 2)
    print("texto paddingas", text_padding)
    print(binary_text[2 * Byte+symbolPadding:-text_padding])
    decoded_text = data_to_text(binary_text[Byte:-text_padding-Byte], decoded_table)
    print("dekoduotas", decoded_text)

    write_text_to_file(outputFile, decoded_text[:-symbolPadding])


def write_text_to_file(output_file: str, text: str) -> bool:
    try:
        with open(output_file, "wb") as output_stream:
            bitarray(text).tofile(output_stream)
        return True
    except OSError:
        print("Failas nerastas")
    return False

def read_from_bin(input_file: str):
    """Decompresses the data and writes it out to the output file"""
    try:
        with open(input_file, "rb") as input_stream:
            # read the size of encoded table 2B 16 bits

            size_of_encoded_table = int.from_bytes(input_stream.read(2), "big")

            chunk = int.from_bytes(input_stream.read(1), "big")

            table_padding = int.from_bytes(input_stream.read(1), "big")

            data = ""

            while True:
                dataByte = input_stream.read(1)
                if not dataByte:
                    break
                data += '{:08b}'.format(ord(dataByte))
                # process data

            binary_table = data[table_padding:size_of_encoded_table * Byte]

            binary_text = data[size_of_encoded_table * Byte:]

            return binary_table, binary_text, chunk

    except OSError:
        print("Failas nerastas.")


def data_to_dictionary(bitText: str, chunk: int) -> dict:
    dictionary = {}
    i = 0
    while i < len(bitText):
        symbol = bitText[i:i + chunk]
        size_bits = int(bitText[i + chunk: i + chunk + Byte], 2)
        bits = bitText[i + chunk + Byte:i + chunk + Byte + size_bits]
        dictionary.update({bits: symbol})
        i += chunk + Byte + size_bits

    return dictionary


def data_to_text(encoded_data: str, dictionary: dict) -> str:
    symbol = ""
    decoded_text = ""
    root = build_binary_tree(dictionary)
    print(root)
    for bit in encoded_data:
        symbol += bit
        if bts(root, symbol):
            print(symbol)
            decoded_text += dictionary[symbol]
            symbol = ""
    return decoded_text


def bts(root: Node, word: str) -> bool:
    for bit in word:
        if bit == '0':
            root = root.left
        else:
            root = root.right

    if root.left is None and root.right is None:
        return True
    else:
        return False


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

