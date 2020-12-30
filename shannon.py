from bitarray import bitarray
from binarytree import Node

Base = 2
Byte = 8


def shannon_encoder(inputFile: str, outputFile: str, chunk: int):

    # Skaitome teksta baitais ir grazina bitu str
    bitText = read_input_from_file(inputFile)

    # Gauname teksto paddinga
    padding = get_padding_size(bitText, chunk)

    # Pridedame gale paddinga
    bitText += padding * '0'

    # Daliname teksta i smulkesnes dalis
    word_list = text_to_chunks(bitText, chunk)

    # Sudarome dazniu lentele
    table_of_frequencies = frequency_table(word_list)

    # Sudarome tikimybiu lentele
    table_of_binary_values = to_binary_table(table_of_frequencies, len(word_list))

    # Suspaudziame teksta
    compressed_text = word_to_bin(word_list, table_of_binary_values)

    # Surasome i bin faila
    write_binary_to_file(table_of_binary_values, compressed_text, chunk, padding, outputFile)


# Reads input file in bytes and returns binary string representation of text
def read_input_from_file(filename: str) -> str:
    bits = ""
    try:
        with open(filename, mode='rb') as input_stream:
            while True:
                dataByte = input_stream.read(1)
                if not dataByte:
                    break
                bits += '{:08b}'.format(ord(dataByte))

        return bits
    except OSError:
        print("Failas nerastas.")


# Calculates frequencies of each symbol and sorts it
def frequency_table(bitText: list) -> dict:
    differentValues = set(bitText)
    probTable = {}

    for letter in differentValues:
        p = bitText.count(letter)
        probTable.update({letter: p})  # e.g. {'a':0.25}

    sorted_tuples = sorted(probTable.items(), key=lambda x: x[1], reverse=True)  # sorted list of tuples
    sorted_probTable = {k: v for k, v in sorted_tuples}  # from list to dict

    return sorted_probTable


# Changes each symbol to a new value from dict
def word_to_bin(bitText: list, binDict: dict) -> str:
    bits = ""
    for c in bitText:
        c_bits = binDict.get(c)
        bits += c_bits

    return bits


# Returns length of binary representation
def length_of_bin_from_freq(frequency: int, data_len: int) -> int:
    total_sum = frequency
    counter = 0
    while total_sum < data_len:
        total_sum *= Base
        counter += 1
    return counter


# Int frequency to binary representation
def int_to_bin(value: float, length: int, dataSize: int) -> str:
    bits = ""
    newNum = value
    for i in range(0, length):
        newNum *= 2
        if newNum > dataSize:
            bits += '1'
            newNum -= dataSize
        else:
            bits += '0'

    return bits


# Frequency table to binary table
def to_binary_table(probTable: dict, dataSize: int) -> dict:
    sum = 0
    binaryTable = {}
    for key, value in probTable.items():
        bit_len = length_of_bin_from_freq(value, dataSize)
        bits = int_to_bin(sum, bit_len, dataSize)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value
    return binaryTable


# Text to binary
def text_to_binary(text: str) -> str:
    bitWord = ""
    for c in text:
        bitWord += format(ord(c), '08b')

    return bitWord


# Returns number of zeros needed for uncompleted byte
def get_padding_size(bitText: str, chunkSize: int) -> int:
    pad = chunkSize - len(bitText) % chunkSize
    if pad != Byte:
        return pad
    else:
        return 0


# Returns text parsed in chunks
def text_to_chunks(bitText: str, chunkSize: int) -> list:
    bitWordList = []

    for index in range(0, len(bitText), chunkSize):
        bitWordList.append(bitText[index:index + chunkSize])

    return bitWordList


# Write all info to binary file
def write_binary_to_file(table: dict, text: str, chunkSize: int, padding: int, filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:

            tableDataToString = ""

            for k, v in table.items():
                tableDataToString += k
                tableDataToString += format(len(v), '08b')
                tableDataToString += v

            textWithPaddingSize = f'{padding:08b}' + text
            textPadding = get_padding_size(textWithPaddingSize, Byte)
            wholeText = f'{textPadding:08b}' + textPadding*"0" + textWithPaddingSize

            tablePadding = get_padding_size(tableDataToString, Byte)
            wholeTable = f'{tablePadding:08b}' + tablePadding * '0' + tableDataToString
            tableSize = int((len(tableDataToString) + tablePadding) / Byte)

            bitarray(f'{tableSize:016b}').tofile(file)  # writing table size to file
            bitarray(f'{chunkSize:08b}').tofile(file)   # writing chunk size to file
            bitarray(wholeTable).tofile(file)     # writing table data to file
            bitarray(wholeText).tofile(file)    # writing file data to file
            return True

    except OSError:
        print("Failas nerastas.")
    return False


def write_text_to_file(output_file: str, text: str) -> bool:

    try:
        with open(output_file, "wb") as output_stream:
            output_stream.write(text)
        return True
    except OSError:
        print("Failas nerastas")
    return False


def byte_from_file(stream, chunkSize):
    while True:
        chunk = stream.read(chunkSize)
        if chunk:
            yield chunk
        else:
            return


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


def shannon_decoder(outputFile):
    binary_table, binary_text, chunk = read_from_bin("encoded.shannon")

    decoded_table = data_to_dictionary(binary_table, chunk)


    textPadding = int(binary_text[0:Byte], 2)
    symbolPadding = int(binary_text[Byte:2 * Byte], 2)


    decoded_text = data_to_text(binary_text[2 * Byte + textPadding:], decoded_table)

    write_text_to_file(decoded_text, outputFile)


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

    for bit in encoded_data:
        symbol += bit
        if bts(root, symbol):
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


def binary_to_char(bitText: str) -> str:
    ans = ""
    for i in range(0, len(bitText), 8):
        ans += bitarray(bitText[i:i + 8]).tobytes().decode('utf-8')
    return ans


if __name__ == '__main__':
    shannon_encoder("flowers.bmp", "encoded.shanon", 8)
    shannon_decoder("flowers2.bmp")
