from bitarray import bitarray
from binarytree import Node

Base = 2
Byte = 8

def shannon_encoder(inputFile: str, outputFile: str, chunk: int):
    # Skaitome teksta baitais ir grazina bitu str
    table_of_frequencies, word_list, padding = read_input_from_file(inputFile, chunk)
    print("Duomenys perskaityti ir sudaryta dzniu lentele")

    # Sudarome tikimybiu lentele
    table_of_binary_values, lenCompressed = to_binary_table(table_of_frequencies, len(word_list))
    # print(lenCompressed)
    print("Sudaryta uzkoduotu zodziu lentele")

    # Suspaudziame teksta
    compressed_text = word_to_bin(word_list, table_of_binary_values)
    print("Uzkoduotas tekstas")

    # Surasome i bin faila
    write_binary_to_file(table_of_binary_values, compressed_text, lenCompressed, chunk, padding, outputFile)
    print("Uzkoduota")


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


# Returns number of zeros needed for uncompleted byte
def get_padding_size(bitText: str, chunkSize: int) -> int:
    pad = chunkSize - len(bitText) % chunkSize
    if pad != Byte:
        return pad
    else:
        return 0

# Write all info to binary file
def write_binary_to_file(table: dict, text: str, text_len: int, chunkSize: int, symbolPaddingSize: int,
                         filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:

            tableDataToString = ""

            for k, v in table.items():
                tableDataToString += k
                tableDataToString += format(len(v), '08b')
                tableDataToString += v

            chunk = f'{chunkSize - 1:08b}'[-4:]  # -1 SVARBU

            numOfEntries = f'{len(table) - 1:016b}'[-chunkSize:]

            lastSymbolPadding = f'{symbolPaddingSize:08b}'[-4:]  # PAZIUREK

            dataPaddingSize = Byte - (
                        len(chunk + numOfEntries + lastSymbolPadding + tableDataToString) + text_len + 3) % Byte
            if dataPaddingSize == Byte:
                dataPaddingSize = 0
            dataPadding = f'{dataPaddingSize:08b}'[-3:] + dataPaddingSize * '0'
            # print(chunkSize)
            # print(len(table))
            # print(symbolPaddingSize)

            # print(dataPadding)

            # print(dataPaddingSize)

            # all = chunk+numOfEntries+lastSymbolPadding+dataPadding+tableDataToString
            # print(table)

            bitarray(chunk + numOfEntries + lastSymbolPadding + dataPadding + tableDataToString + text).tofile(file)
            return True

    except OSError:
        print("Failas nerastas.")
    return False


