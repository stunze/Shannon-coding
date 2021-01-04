from bitarray import bitarray

Base = 2
Byte = 8


def shannon_encoder(inputFile: str, outputFile: str, chunk: int):
    # Skaitome teksta baitais ir grazina bitu str
    table_of_frequencies, word_list, padding = read_input_from_file(inputFile, chunk)

    # Sudarome tikimybiu lentele
    table_of_binary_values = to_binary_table(table_of_frequencies, len(word_list))


    # # Suspaudziame teksta
    compressed_text = word_to_bin(word_list, table_of_binary_values)


    # Surasome i bin faila
    write_binary_to_file(table_of_binary_values, chunk, padding, compressed_text, outputFile)
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
    try:
        with open(fileName, "rb") as stream:

            bytesFromFile = yield_from_file(stream)
            for dataChunk in bytesFromFile:
                tempBuffer.frombytes(dataChunk)
                bits = tempBuffer.to01()
                del tempBuffer[:]


                while len(bits) > chunkSize:
                    word = bits[:chunkSize]
                    fill_frequency_table(word, dictionary)
                    words.append(word)
                    bits = bits[chunkSize:]


            extraZeros = chunkSize-len(bits)
            if len(bits) != 0:
                bits += (chunkSize-len(bits))*'0'
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
        c_bits = binDict[c]
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
def to_binary_table(probTable: dict, dataSize: int) -> dict: ## PABANDYT
    sum = 0
    binaryTable = {}

    for key, value in probTable.items():
        bit_len = length_of_bin_from_freq(value, dataSize)
        bits = int_to_bin(sum, bit_len, dataSize)
        binaryTable.update({key: bits})  # format(<the_integer>, "<0><width_of_string><format_specifier>")
        sum += value


    return binaryTable


# # Text to binary
# def text_to_binary(text: str) -> str:
#     bitWord = ""
#     for c in text:
#         bitWord += format(ord(c), '08b')
#
#     return bitWord


# Returns number of zeros needed for uncompleted byte
def get_padding_size(bitText: str, chunkSize: int) -> int:
    pad = chunkSize - len(bitText) % chunkSize
    if pad != Byte:
        return pad
    else:
        return 0


# # Returns text parsed in chunks
# def text_to_chunks(bitText: str, chunkSize: int) -> list:
#     bitWordList = []
#
#     for index in range(0, len(bitText), chunkSize):
#         bitWordList.append(bitText[index:index + chunkSize])
#
#     return bitWordList


# Write all info to binary file
def write_binary_to_file(table: dict, chunkSize: int, padding: int, text: str, outputFile: str) -> bool:
    try:
        with open(outputFile, mode='wb') as file:


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

def read_input_from_file2(fileName: str, chunkSize: int, dictionary):
    tempBuffer = bitarray()
    words = bitarray()
    bits = ""
    try:
        with open(fileName, "rb") as stream:

            bytesFromFile = yield_from_file(stream)
            for dataChunk in bytesFromFile:
                tempBuffer.frombytes(dataChunk)
                bits = tempBuffer.to01()
                del tempBuffer[:]

                while len(bits) > chunkSize:
                    word = bits[:chunkSize]
                    words.extend(dictionary[word])
                    bits = bits[chunkSize:]


            if len(bits) != 0:
                bits += (chunkSize-len(bits))*'0'
                words.extend(dictionary[word])

            return words


    except OSError:
        print("Failas nerastas")



def byte_from_file(stream, chunkSize):
    while True:
        chunk = stream.read(chunkSize)
        if chunk:
            yield chunk
        else:
            return

