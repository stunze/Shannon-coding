import sys

from bitarray import bitarray

Base = 2
Byte = 8


def read_input_from_file(filename: str) -> str:
    try:
        with open(filename, mode='r') as file:  # reading characters from file
            word = file.read()
        return word
    except OSError:
        print("Failas nerastas.")


def frequency_table(word: list) -> dict:
    differentValues = (word)
    probTable = {}
    length = len(word)

    for letter in differentValues:
        p = word.count(letter)
        probTable.update({letter: p})  # e.g. {'a':0.25}

    # PATAISYTA DALIS. Buvo klaida nes grazindavo sarasa, o ne zodyna
    sorted_tuples = sorted(probTable.items(), key=lambda x: x[1], reverse=True)  # grazina surikiuota poru SARASA
    sorted_probTable = {k: v for k, v in sorted_tuples}  # is poru SARASO i zodyna

    return sorted_probTable


def length_of_bin_from_freq(frequency: int, data_len: int) -> int:
    total_sum = frequency
    counter = 0
    while total_sum < data_len:
        total_sum *= Base
        counter += 1
    return counter


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


def to_binary_table(probTable: dict, dataSize: int) -> dict:
    sum = 0
    binaryTable = {}
    for key, value in probTable.items():
        bit_len = length_of_bin_from_freq(value, dataSize)
        bits = int_to_bin(sum, bit_len, dataSize)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value
    return binaryTable


def word_to_bin(word: str, binDict: dict) -> str:
    bits = ""
    for c in word:
        c_bits = binDict.get(c)
        bits += c_bits

    return bits


def write_output_to_file(table: dict, text: str, filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:  # reading characters from file

            tableDataToString = ""

            for k, v in table.items():
                tableDataToString += "".join(format(ord(k), '016b'))
                tableDataToString += v

            total_bits = len(tableDataToString)

            diff = 8 - total_bits % 8

            tableSize = bitarray(f'{int((total_bits + diff) / Byte):016b}')

            tableSizepadding = bitarray(f'{diff:08b}')

            tableWithExtraZeros = diff * '0' + tableDataToString

            print(tableWithExtraZeros)
            tableSize.tofile(file)
            tableSizepadding.tofile(file)
            bitarray(tableWithExtraZeros).tofile(file)
            bitarray(text).tofile(file)

            return True

    except OSError:
        print("Failas nerastas.")
    return False


def prepare_to_write(table: dict, text: str) -> list:
    toWrite = ""


def shannon_encoder(inputFile: str, outputFile: str):
    word = read_input_from_file(inputFile)
    table_of_probabilities = frequency_table(word)

    table_of_binary_values = to_binary_table(table_of_probabilities, len(word))
    text_in_binary = word_to_bin(word, table_of_binary_values)

    prepare_to_write(table_of_binary_values, text_in_binary)
    write_output_to_file(table_of_binary_values, text_in_binary, outputFile)
    read_from_bin(outputFile, "antras.txt")


def read_from_bin(input_file: str, output_file: str):
    """Decompresses the data and writes it out to the output file"""
    try:
        with open(input_file, "rb") as input_stream, open(output_file, "wb") as output_stream:


            # read the size of encoded table 2B 16 bits
            size_of_encoded_table = int.from_bytes(input_stream.read(2), "big") #kazkodel size gaunasi iki failo galo...

            # read the size of encoded table padding 1B
            table_padding = int.from_bytes(input_stream.read(1), "big")

            encoded_table = ""

            for byte in input_stream.read(size_of_encoded_table):
                encoded_table += f"{bin(byte)[2:]:0>8}"

            print(encoded_table)
            encoded_table = encoded_table[table_padding:] #NEBEREIK cia reik +1 kazkodel pridet ir pastumt



            """Writes out the data in string as a byte arrays"""

            print(len(encoded_table))
            for i in range(0, len(encoded_table)+20, 20): #o cia + 20 bituku (tie 5 baitai)
                #o kas cia per nesamone gaunas as nezinau
                print(chr(int(encoded_table[i:i+8], 2)))
                print(chr(int(encoded_table[i+8:i+12], 2)))
                print(chr(int(encoded_table[i+12:i+20], 2)))
                # print(symbol_array)
                # length_array.append(int(encoded_table[i+8:i+12], 2))
                # code_array.append(int(encoded_table[i+12:i+20], 2))
            #.....
            #.....

    except OSError:
        print("Failas nerastas.")


if __name__ == '__main__':
    shannon_encoder("test.txt", "answer.bin")
