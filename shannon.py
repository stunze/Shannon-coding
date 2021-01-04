from bitarray import bitarray
from binarytree import Node

Base = 2
Byte = 8


def shannon_encoder(inputFile: str, outputFile: str, chunk: int):
    # Skaitome teksta baitais ir grazina bitu str
    table_of_frequencies, word_list, padding = read_input_from_file(inputFile, chunk)


    # Sudarome tikimybiu lentele
    table_of_binary_values, lenCompressed = to_binary_table(table_of_frequencies, len(word_list))
    print(lenCompressed)

    # Suspaudziame teksta
    compressed_text = word_to_bin(word_list, table_of_binary_values)

    # Surasome i bin faila
    write_binary_to_file(table_of_binary_values, compressed_text, lenCompressed, chunk, padding, outputFile)
    print("encoded")




def yield_from_file(stream, num_of_bytes=1024):
    while True:
        data = stream.read(num_of_bytes)
        if not data:
            break
        yield data


# Reads input file in bytes and returns binary string representation of text
def read_input_from_file(fileName: str, chunkSize: int):
    dictionary = {}
    tempBuffer = bitarray()
    words = []
    bits = ""
    all = ""
    try:
        with open(fileName, "rb") as stream:

            bytesFromFile = yield_from_file(stream)
            for dataChunk in bytesFromFile:
                tempBuffer.frombytes(dataChunk)
                bits += tempBuffer.to01()
                del tempBuffer[:]
                while len(bits) > chunkSize:
                    word = bits[:chunkSize]
                    fill_frequency_table(word, dictionary)
                    words.append(word)
                    bits = bits[chunkSize:]
                    all += word

            extraZeros = chunkSize - len(bits)
            if len(bits) != 0:
                bits += (chunkSize - len(bits)) * '0'
                fill_frequency_table(bits, dictionary)
                words.append(bits)

            sorted_tuples = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)  # sorted list of tuples
            sorted_probTable = {k: v for k, v in sorted_tuples}  # from list to dict

            return sorted_probTable, words, extraZeros


    except OSError:
        print("Failas nerastas")


# Calculates frequencies of each symbol and sorts it
def fill_frequency_table(word: str, dict):
    if word in dict:
        dict[word] += 1
    else:
        dict.update({word: 1})


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
def to_binary_table(probTable: dict, dataSize: int):
    sum = 0
    sizeOfText = 0
    binaryTable = {}
    for key, value in probTable.items():
        bit_len = length_of_bin_from_freq(value, dataSize)
        bits = int_to_bin(sum, bit_len, dataSize)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value
        sizeOfText += value * bit_len
    return binaryTable, sizeOfText


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
def write_binary_to_file(table: dict, text: str, text_len: int, chunkSize: int, symbolPaddingSize: int, filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:

            tableDataToString = ""

            for k, v in table.items():
                tableDataToString += k
                tableDataToString += format(len(v), '08b')
                tableDataToString += v

            textPaddingSize = 8 - (text_len % 8)
            tablePadding = get_padding_size(tableDataToString, Byte)

            wholeTable = tableDataToString + tablePadding * '0'
            tableSize = int((len(tableDataToString) + tablePadding) / Byte)

            wholeText = text + textPaddingSize * '0'


            bitarray(f'{tableSize:016b}').tofile(file)  # writing table size to file
            bitarray(f'{chunkSize:08b}').tofile(file)  # writing chunk size to file
            bitarray(f'{tablePadding:08b}').tofile(file)  # writing chunk size to file
            bitarray(f'{symbolPaddingSize:08b}').tofile(file)  # writing chunk size to file
            bitarray(f'{textPaddingSize:08b}').tofile(file)  # writing chunk size to file
            print("Lenteles dydis", tableSize)
            print("Chunk dydis", chunkSize)
            print("Lenteles paddingas ", tablePadding)
            print("Simbolio paddingas ", symbolPaddingSize)
            print("Teksto paddingas ", textPaddingSize)

            bitarray(wholeTable).tofile(file)  # writing table data to file
            bitarray(wholeText).tofile(file)  # writing file data to file
            return True

    except OSError:
        print("Failas nerastas.")
    return False


def write_text_to_file(text: str, output_file: str) -> bool:
    try:
        with open(output_file, "wb") as output_stream:
            bitarray(text).tofile(output_stream)
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
            symbol_padding_size = int.from_bytes(input_stream.read(1), "big")
            text_padding_size = int.from_bytes(input_stream.read(1), "big")

            # print("Lenteles dydis", size_of_encoded_table)
            # print("Chunk dydis", chunk)
            # print("Lenteles paddingas ", table_padding)
            # print("Simbolio paddingas ", symbol_padding_size)
            # print("Teksto paddingas ", text_padding_size)

            data = ""

            while True:
                dataByte = input_stream.read(1)
                if not dataByte:
                    break
                data += '{:08b}'.format(ord(dataByte))
                # process data

            binary_table = data[:size_of_encoded_table * Byte-table_padding]


            startOfText = size_of_encoded_table * Byte

            binary_text = data[startOfText:-text_padding_size]

            # print("be galo", binary_text)

            return binary_table, binary_text, chunk, symbol_padding_size

    except OSError:
        print("Failas nerastas.")


def shannon_decoder(inputFile, outputFile):
    binary_table, binary_text, chunk, symbol_padding = read_from_bin(inputFile)

    decoded_table = data_to_dictionary(binary_table, chunk)

    decoded_text = data_to_text(binary_text, decoded_table)
    #print(binary_text[-200:])

    if symbol_padding != 0:
        write_text_to_file(decoded_text[:-symbol_padding], outputFile)
        print("gavosi", decoded_text[-300:])
        print("gavosi", len(decoded_text[:-symbol_padding])/8)
    else:
        write_text_to_file(decoded_text, outputFile)
        # print("gavosi", decoded_text)







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
    shannon_encoder("black.bmp", "vb.shn", 11)
    shannon_decoder("vb.shn", "black2.bmp")
