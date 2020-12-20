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


def frequency_table(bitText: list) -> dict:
    differentValues = set(bitText)
    probTable = {}

    for letter in differentValues:
        p = bitText.count(letter)
        probTable.update({letter: p})  # e.g. {'a':0.25}

    sorted_tuples = sorted(probTable.items(), key=lambda x: x[1], reverse=True)  # grazina surikiuota poru SARASA
    sorted_probTable = {k: v for k, v in sorted_tuples}  # is poru SARASO i zodyna

    return sorted_probTable


def word_to_bin(bitText: list, binDict: dict) -> str:
    bits = ""
    for c in bitText:
        c_bits = binDict.get(c)
        bits += c_bits

    return bits


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


def text_to_binary(text: str) -> str:
    bitWord = ""
    for c in text:
        bitWord += format(ord(c), '08b')

    return bitWord


def get_padding_size(bitText: str, chunkSize: int) -> int:
    pad = chunkSize - len(bitText) % chunkSize
    if pad != Byte:
        return pad
    else:
        return 0


def text_to_chunks(bitText: str, chunkSize: int) -> list:
    bitWordList = []

    for index in range(0, len(bitText), chunkSize):
        bitWordList.append(bitText[index:index + chunkSize])

    return bitWordList


###################################################################################################################


def shannon_encoder(inputFile: str, outputFile: str, chunk: int):
    # Perskaitome duomenis is failo
    text = read_input_from_file(inputFile)

    # Paverciame viska i bitus
    bitText = text_to_binary(text)

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

    # Skaitome is bin failo
    read_from_bin(outputFile, "decoded.txt")


def write_binary_to_file(table: dict, text: str, chunkSize: int, padding: int, filename: str) -> bool:
    try:
        with open(filename, mode='wb') as file:  # reading characters from file

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

            #print("Lenteles duomenys issiunciant: \n", tableDataToString)
            print("Teksto ilgis: ", len(text) - padding)
            print("Paskutinio simbolio paddingo dydis: ", padding)
            print("Teksto paddingo dydis: ", textPadding)
            bitarray(f'{tableSize:016b}').tofile(file)
            bitarray(f'{chunkSize:08b}').tofile(file)  # chunk dydis
            bitarray(wholeTable).tofile(file)
            bitarray(wholeText).tofile(file)
            return True

    except OSError:
        print("Failas nerastas.")
    return False


def write_text_to_file(output_file: str, text: str) -> bool:
    try:
        with open(output_file, "w") as output_stream:
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


def read_from_bin(input_file: str, output_file: str):
    """Decompresses the data and writes it out to the output file"""
    try:
        with open(input_file, "rb") as input_stream:
            # read the size of encoded table 2B 16 bits

            print("############### GAUTI DUOMENYS #####################")
            size_of_encoded_table = int.from_bytes(input_stream.read(2), "big")
            print("Lenteles dydis baitais: ", size_of_encoded_table)

            chunk = int.from_bytes(input_stream.read(1), "big")
            print("Chunk dydis: ", chunk)
            # read the size of padding 1B
            table_padding = int.from_bytes(input_stream.read(1), "big")

            print("Lenteles paddingo dydis: ", table_padding)

            data = ""

            while True:  # --> replaced `file` with `True` to be clear
                dataByte = input_stream.read(1)
                if not dataByte:  # empty => EOF
                    # OR   if len(data) < 4: if you don't want last incomplete chunk
                    break
                data += '{:08b}'.format(ord(dataByte))
                # process data

            binary_table = data[table_padding:size_of_encoded_table * Byte]

            binary_text = data[size_of_encoded_table * Byte:]
            print("ilgissss :", len(binary_text)-16)
            decoded_table = data_to_dictionary(binary_table, chunk)

            # print(decoded_table)

            textPadding = int(binary_text[0:Byte], 2)
            symbolPadding = int(binary_text[Byte:2 * Byte], 2)
            print("Teksto paddingo dydis: ", textPadding)
            print("Paskutinio ismb paddingo dydis: ", symbolPadding)
            print(binary_text[textPadding + symbolPadding:textPadding + symbolPadding:+24])
            decoded_text = data_to_text(decoded_table, binary_text[2*Byte + textPadding:])
            print("Po dekodavimo: ", len(binary_text[2*Byte + textPadding:]))
            text = binary_to_char(decoded_text)
            write_text_to_file(output_file, decoded_text)

    except OSError:
        print("Failas nerastas.")


def data_to_dictionary(bitText: str, chunk: int) -> dict:
    dictionary = {}
    i = 0
    while i < len(bitText):
        symbol = bitText[i:i + chunk]
        size_bits = int(bitText[i + chunk: i + chunk + Byte], 2)
        bits = bitText[i + chunk + Byte:i + chunk + Byte + size_bits]
        dictionary.update({symbol: bits})
        i += chunk + Byte + size_bits

    return dictionary


def data_to_text(dictionary: dict, encoded_text: str) -> str:
    symbol = ""
    decoded_text = ""

    for bit in encoded_text:
        symbol += bit
        for key, value in dictionary.items():
            if symbol == value:
                decoded_text += key
                symbol = ""
    return decoded_text


def binary_to_char(bitText: str) -> str:
    ans = ""
    print("ilgiuszas ", len(bitText))
    for i in range(0, len(bitText), 8):
        ans += bitarray(bitText[i:i + 8]).tobytes().decode('utf-8')
    return ans


if __name__ == '__main__':
    shannon_encoder("test.txt", "encoded.bin", 16)
